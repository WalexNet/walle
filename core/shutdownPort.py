from netmiko import ConnectHandler
import configparser

def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config

def shutdown_port_administrativamente(device):
    resultados = []
    config = read_config("config.ini")
    
    if device['device_type'] == 'mikrotik_routeros':
        username = config.get("usuario-mikrotik", "user")
        password = config.get("usuario-mikrotik", "password")
    else:
        username = config.get("usuario-ad", "user")
        password = config.get("usuario-ad", "password")
        
    enable_secret = ''    

    # Añadir los nuevos elementos
    device['username'] = username
    device['password'] = password
    device['conn_timeout'] = 30
    #device['enable_secret'] = enable_secret
    #print(device)
    try:
        with ConnectHandler(**device) as net_connect:
            net_connect.enable()
            device_type = device['device_type']
            interfaces_por_configurar = []

            # Cisco IOS
            if device_type == 'cisco_ios':
                # Obtener estado de interfaces
                output_status = net_connect.send_command('show interfaces status')
                # Obtener configuración de switchport
                output_switchport = net_connect.send_command('show interfaces switchport')
                
                switchport_data = {}
                current_interface = None
                for line in output_switchport.splitlines():
                    if line.startswith('Name: '):
                        current_interface = line.split()[1]
                        switchport_data[current_interface] = {}
                    elif 'Administrative Mode:' in line and current_interface:
                        switchport_data[current_interface]['admin_mode'] = line.split()[-1]
                    elif 'Operational Mode:' in line and current_interface:
                        switchport_data[current_interface]['oper_mode'] = line.split()[-1]
                
                # Buscar interfaces down y que sean access (no trunk)
                for line in output_status.splitlines():
                    if ('notconnect' in line or 'disabled' in line) and len(line.split()) > 0:
                        interface = line.split()[0]
                        if interface in switchport_data:
                            # Excluir puertos trunk, permitir access incluso con voice VLAN
                            admin_mode = switchport_data[interface].get('admin_mode', '')
                            oper_mode = switchport_data[interface].get('oper_mode', '')
                            if 'trunk' not in admin_mode.lower() and 'trunk' not in oper_mode.lower():
                                interfaces_por_configurar.append(interface)

            # Huawei
            elif device_type == 'huawei':
                # Obtener estado de interfaces
                output_status = net_connect.send_command('display interface brief')
                # Obtener configuración de interfaces para identificar trunks
                output_interface_config = net_connect.send_command('display current-configuration interface')
                
                # Identificar puertos trunk
                trunk_interfaces = set()
                current_interface = None
                for line in output_interface_config.splitlines():
                    line = line.strip()
                    if line.startswith('interface '):
                        current_interface = line.split()[1]
                    elif current_interface and 'port link-type trunk' in line:
                        trunk_interfaces.add(current_interface)
                
                # Buscar interfaces down que NO sean trunk
                for line in output_status.splitlines():
                    if 'down' in line and 'up' not in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            interface = parts[0]
                            # Solo procesar si NO es un puerto trunk
                            if interface not in trunk_interfaces:
                                interfaces_por_configurar.append(interface)

            # MikroTik RouterOS
            elif device_type == 'mikrotik_routeros':
                # Obtener listado de interfaces
                output = net_connect.send_command('/interface print detail without-paging')
                
                for line in output.splitlines():
                    if 'name=' in line and 'disabled=yes' not in line:
                        # Buscar interfaces que estén down
                        if 'running=no' in line and 'slave=no' in line:
                            interface_data = {}
                            for part in line.split():
                                if '=' in part:
                                    key, value = part.split('=', 1)
                                    interface_data[key] = value
                            
                            interface_name = interface_data.get('name', '')
                            
                            # Verificar si es puerto de acceso (no trunk)
                            bridge_output = net_connect.send_command(f'/interface bridge port print detail where interface={interface_name}')
                            if 'frame-types=admit-all' in bridge_output or 'frame-types=admit-only-untagged-and-priority-tagged' in bridge_output:
                                interfaces_por_configurar.append(interface_name)

            # Fortinet FortiSwitch
            elif device_type == 'fortinet':
                # Obtener estado de interfaces
                output_status = net_connect.send_command('show system interface')
                
                current_interface = None
                interface_data = {}
                
                for line in output_status.splitlines():
                    if line.strip() and not line.startswith(' '):
                        current_interface = line.split()[0]
                        interface_data[current_interface] = {}
                    elif current_interface and ':' in line:
                        key, value = line.split(':', 1)
                        interface_data[current_interface][key.strip()] = value.strip()
                
                # Buscar interfaces down y que sean access (no trunk)
                for interface, data in interface_data.items():
                    if 'admin' in data and 'up' in data['admin'] and 'link' in data and 'down' in data['link']:
                        # Excluir interfaces trunk (normalmente tienen VLANs múltiples configuradas)
                        if 'mode' in data and data['mode'] == 'static':
                            # Verificar adicionalmente que no sea trunk buscando allowed VLANs
                            trunk_indicators = ['tagged', 'trunk', 'allowed']
                            is_trunk = any(indicator in str(data).lower() for indicator in trunk_indicators)
                            if not is_trunk:
                                interfaces_por_configurar.append(interface)

            # Configurar shutdown para las interfaces seleccionadas
            if interfaces_por_configurar:
                config_commands = []
                if device_type == 'cisco_ios':
                    for interface in interfaces_por_configurar:
                        config_commands.append(f"interface {interface}")
                        config_commands.append("shutdown")
                elif device_type == 'huawei':
                    for interface in interfaces_por_configurar:
                        config_commands.append(f"interface {interface}")
                        config_commands.append("shutdown")
                elif device_type == 'mikrotik_routeros':
                    for interface in interfaces_por_configurar:
                        config_commands.append(f"/interface disable [find name={interface}]")
                elif device_type == 'fortinet':
                    for interface in interfaces_por_configurar:
                        config_commands.append(f"config system interface")
                        config_commands.append(f"edit {interface}")
                        config_commands.append("set status down")
                        config_commands.append("end")
                
                # Ejecutar comandos de configuración
                output_config = net_connect.send_config_set(config_commands)
                
                # Guardar configuración
                if device_type in ['cisco_ios', 'huawei']:
                    save_output = net_connect.save_config()
                    resultados.append("Configuración guardada")
                elif device_type == 'mikrotik_routeros':
                    net_connect.send_command('/system configuration save')
                    resultados.append("Configuración guardada en MikroTik")
                
                # Agregar resultados detallados
                resultados.append(f"Interfaces apagadas administrativamente: {len(interfaces_por_configurar)}")
                for interface in interfaces_por_configurar:
                    resultados.append(f"Interface {interface} - SHUTDOWN aplicado")
                
                resultados.append(f"Total de comandos ejecutados: {len(config_commands)}")

            else:
                resultados.append("No se encontraron interfaces en estado 'down' y tipo 'acceso' para configurar.")

    except Exception as e:
        resultados.append(f"ERROR: {str(e)}")
    
    return resultados

if __name__ == "__main__":
    ip = '10.20.24.36'
    id_fabricante = 7
    mapeo_tipos = {
        1: 'cisco_ios',
        2: 'huawei',
        9: 'mikrotik_routeros',
        7: 'fortinet'
    }    

    device = {
        'device_type': mapeo_tipos[id_fabricante],
        'ip': ip
    }

    # Obtener resultados
    resultados = shutdown_port_administrativamente(device)
    print(resultados)