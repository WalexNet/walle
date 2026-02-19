from .funciones import lee_archivo_txt

def parse_block(lines):
    stack = []
    current_dict = {}
    
    for line in lines:
        line = line.strip()  # Eliminar espacios en blanco y saltos de línea extra
        
        if line.startswith("config"):
            stack.append((current_dict, line))
            current_dict[line] = {}
            current_dict = current_dict[line]
        
        elif line.startswith("set"):
            parts = line.split(maxsplit=2)
            if len(parts) == 3:
                key, value = parts[1], parts[2].strip('"') # Quetamos las Comillas dobles
                current_dict[key] = value
        
        elif line.startswith("edit"):
            edit_key = line.split(maxsplit=1)[1]  # Mantener la clave como string
            stack.append((current_dict, edit_key))
            current_dict[edit_key] = {}
            current_dict = current_dict[edit_key]
        
        elif line == "next":
            current_dict, _ = stack.pop()
        
        elif line == "end":
            if stack:
                current_dict, _ = stack.pop()
    
    return current_dict

def sumar_puntajes(puntajes, res):
    return sum(puntajes[i] for i, item in enumerate(res) if item['status'])


# Clase Principal
class Auditor:
    def __init__(self, archivo_conf):
        self.data = lee_archivo_txt(archivo_conf)
        self.datos = parse_block(self.data)
        # Claves
        self.politicas            = self.datos['config firewall policy']
        self.user_radius          = self.datos['config user radius']
        self.config_sys_global    = self.datos['config system global']
        self.sys_admin            = self.datos['config system admin']
        self.interfaces           = self.datos['config system interface']
        self.ntp_servers          = self.datos['config system ntp']['config ntpserver'] if self.datos.get('config system ntp', {}).get('config ntpserver') is not None else False
        self.ha                   = self.datos['config system ha']
        self.config_fortianalyzer = self.datos['config log fortianalyzer setting'] if 'config log fortianalyzer setting' in self.datos else None
        self.config_central_mgm   = self.datos['config system central-management'] if 'config system central-management' in self.datos else None
        self.snmp                 = self.datos['config system snmp sysinfo']
        self.truster_network      = self.sys_admin['"Radius_Access"'] if '"Radius_Access"' in self.sys_admin else None


            
    # 1 - Politicas Any Any
    # 'config firewall policy'
    def any_any(self):
        respuesta = {}
        for id, politica in self.politicas.items():
            if 'srcaddr' in politica and 'dstaddr' in politica and 'action' in politica and not 'status' in politica:
                if politica['srcaddr'].lower() == 'all' and politica['dstaddr'].lower() == 'all' and politica['service'].lower() == 'all':
                    respuesta[id] = politica
                elif (politica['srcaddr'].lower() == 'all' or politica['dstaddr'].lower() == 'all') and politica['service'].lower() == 'all':
                    respuesta[id] = politica
        return dict(sorted(respuesta.items(), key=lambda x: int(x[0])))
    
    # 2 - Excepciones Salida con Supervision
    def salida_supervicion(self):
        missing_keys = {}
        claves = ['ssl-ssh-profile', 'av-profile', 'ips-sensor', 'application-list']
        for id, politica in self.politicas.items():
            if 'inter' in politica['dstintf'].lower():
                faltantes = [key for key in claves if key not in politica]
                if faltantes:
                    missing_keys[id] = faltantes
                    
        # Ordenamos el resultado por ID (clave del diccionario)
        return dict(sorted(missing_keys.items(), key=lambda x: int(x[0])))
    
    # 3 - Deny BlackList
    def deny_blacklist(self):
        deny_listanegra = {}
        for id, politica in self.politicas.items():
            if 'dstaddr' in politica and 'srcaddr' in politica:
                if (politica['dstaddr'] == 'Blacklist-Ips' or politica['srcaddr'] == 'Blacklist-Ips') and 'action' in politica:
                    deny_listanegra[id] = 'action accept'
        return deny_listanegra

    # 4 - Deny Malicious Countries    
    def malicius_countries(self):
        malicius_paises = {}
        for id, politica in self.politicas.items():
            if 'dstaddr' in politica and 'srcaddr' in politica:
                if ('GRP_Malicious_Countries' in politica['dstaddr'] or 'GRP_Malicious_Countries' in politica['srcaddr']) and 'action' in politica:
                    malicius_paises[id] = 'action accept'
        return malicius_paises
    
    # 5 - ClearPass
    def clearPass(self):
        server = ["radius1.central.cirsa.com",
                "radius2.central.cirsa.com",
                "radius3.central.cirsa.com",
                "radius4.central.cirsa.com"]
        
        if '"ClearPass Admin"' in self.user_radius :
            clearPass = self.user_radius['"ClearPass Admin"']
            return clearPass['server'] in server and clearPass['secondary-server'] in server
        else:
            return False

    # 6 - Administrator truster network
    def contains_trusthost_value(self, search_value='10.0.0.0 255.0.0.0'):
        return (
            '"Radius_Access"' in self.sys_admin
            and self.truster_network
            and any(value == search_value for key, value in self.truster_network.items() if key.startswith('trusthost'))
        )
        
    # 7 - Acceso por dos Interfaces
    def acceso_interfaces(self):
        list_int = []
        for id, valor in self.interfaces.items():
            if 'allowaccess' in valor:
                list_int.append(valor['allowaccess'].split())
        return sum(1 for sublist in list_int if 'https' in sublist)
    
    # 8 - SNMP
    def snmp_ok(self):
        return 'status' in self.snmp
    
    # 9 - SysLog
    def syslog_ok(self):
        if 'config log syslogd setting' in self.datos:
            syslog = self.datos['config log syslogd setting']
            return syslog['status'] == 'enable'
    
    # 10 - NTP
    def servidores_ntp(self):
        ntp_srv = ['1.es.pool.ntp.org', '2.es.pool.ntp.org', '3.es.pool.ntp.org', '4.es.pool.ntp.org']
        if self.ntp_servers:
            if len(self.ntp_servers) == 4:
                return all(entry.get('server') in ntp_srv for entry in self.ntp_servers.values())
        else: 
            return False
        
    # 11 - SecuritePort
    def securite_ports(self):
        if 'admin-sport' in self.config_sys_global:
            return '8443' == self.config_sys_global['admin-sport']
        else:
            return False
    
    # 12 - Config de HA
    def ha_ok(self):
        if 'hbdev' in self.ha and 'priority' in self.ha:
            hbdev = self.ha['hbdev'].replace('"', '').split()[1]
            priority = self.ha['priority']
            return hbdev == '150' and priority == '200'
        
    # 13 - Integracion con Analizer
    def inte_ana(self):
        fortianalizer = False
        if self.config_fortianalyzer:
            if 'status' in self.config_fortianalyzer and 'server' in self.config_fortianalyzer:
                fortianalizer = self.config_fortianalyzer['status'] == 'enable' and self.config_fortianalyzer['server'] == "10.146.66.4"
        return fortianalizer

    # 14 - Integracion con Fabric
    def inte_fab(self):
        central_mgm = False
        if self.config_central_mgm:
            if 'type' in self.config_central_mgm and 'fmg' in self.config_central_mgm:
                central_mgm = self.config_central_mgm['type'] == 'fortimanager' and self.config_central_mgm['fmg'] == "10.146.66.5"
        return central_mgm
    
    def datos_archivo_conf(self):
        datos_archivo = {
        'version'   : self.data[0].split('=')[1].split(':')[0],
        'user'      : self.data[0].split('=')[4].strip(),
        'host_name' : self.config_sys_global['hostname']
        }
        return datos_archivo
    
    def mostrar(self, seccion):
        if seccion not in self.datos:
            return f'No existe la {seccion}'
        return self.datos[seccion]


def res_auditoria(archivo):
    def politicas_error(diccionario):
        #print('Hola',diccionario)
        return [
            f"ID: {id}, Nombre: {politicas['name']}" if 'name' in politicas else f"ID: {id} - {politicas}"
            for id, politicas in diccionario.items()
        ]

    auditamos = Auditor(archivo)
    puntajes = [40,10,5,5,5,5,5,5,4,4,4,4,2,2]
    auditorias = [
        ('Politicas Any Any', auditamos.any_any(), True),
        ('Excepciones Salida con Supervision', auditamos.salida_supervicion(), True),
        ('Deny BlackList', auditamos.deny_blacklist(), True),
        ('Deny Malicious Countries', auditamos.malicius_countries(), True),
        ('ClearPass', auditamos.clearPass(), False, ['user_radius']),
        ('Administrator truster network', auditamos.contains_trusthost_value(), False, ['user_radius']),
        ('Acceso por dos Interfaces', auditamos.acceso_interfaces(), False, ['Total: ']),
        ('SNMP', auditamos.snmp_ok(), False, ['config system snmp sysinfo']),
        ('SysLog', auditamos.syslog_ok(), False, ['config log syslogd setting']),
        ('NTP', auditamos.servidores_ntp(), False, ['config system ntp - config ntpserver']),
        ('SecuritePort', auditamos.securite_ports(), False, ['config_sys_global - admin-sport']),
        ('HA', auditamos.ha_ok(), False, ['config system ha']),
        ('Integracion con Fabric', auditamos.inte_fab(), False, ['config system central-management']),
        ('Integracion con Analizer', auditamos.inte_ana(), False, ['config log fortianalyzer setting']),
    ]
    
    res = [
        {
            'status': bool(resultado) if isinstance(resultado, (bool, int)) else not bool(resultado),
            'name': nombre,
            'errors': (
                politicas_error(resultado) if analizar_errores 
                else ([] if resultado else ([f'Total: {resultado}'] if nombre == 'Acceso por dos Interfaces' else errores))
            )
        }
        for nombre, resultado, analizar_errores, *errores in auditorias
    ]

    return res, auditamos.datos_archivo_conf(), sumar_puntajes(puntajes,res)



if __name__ == '__main__':
    archivo_conf = 'ESQTCPSLOTSFW01.conf'
    audit, datos_archivo_config, total = res_auditoria(archivo_conf)
    for res in audit:
        print(res)