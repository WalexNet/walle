import ipaddress
import sys
from tabulate import tabulate

def ip_to_binary(ip):
    return '.'.join(f'{int(octet):08b}' for octet in ip.split('.'))

def calculate_network(ip_cidr):
    network = ipaddress.ip_network(ip_cidr, strict=False)
    ip_sin_prefijo = ip_cidr.split('/')[0]
    red = {
        'Address'  : [ip_sin_prefijo, ip_to_binary(ip_sin_prefijo)],
        'Netmask'  : [str(network.netmask), ip_to_binary(str(network.netmask))],
        'Wildcard' : [str(network.hostmask), ip_to_binary(str(network.hostmask))],
        'Network'  : [str(network.network_address)+'/'+str(network.prefixlen), ip_to_binary(str(network.network_address))],
    }
    if len(ip_cidr.split('/'))>1:
        red['HostMin']= [str(network.network_address + 1), ip_to_binary(str(network.network_address + 1))]
        red['HostMax']= [str(network.broadcast_address - 1), ip_to_binary(str(network.broadcast_address - 1))]
        red['Broadcast']= [str(network.broadcast_address), ip_to_binary(str(network.broadcast_address))]
        red['HostsNet']= network.num_addresses - 2
    return red

def calculate_subnets(ip_cidr, new_prefix):
    network = ipaddress.ip_network(ip_cidr, strict=False)
    subnets = list(network.subnets(new_prefix=new_prefix))
    sub_redes = []
    for i, subnet in enumerate(subnets, 1):
        sub_redes.append({
            "red_num"  : i,
            "Network"  : [str(subnet.network_address)+'/'+str(subnet.prefixlen), ip_to_binary(str(subnet.network_address))],
            "NetMask"  : [str(subnet.netmask),  ip_to_binary(str(subnet.netmask))],
            "HostMin"  : [str(subnet.network_address + 1), ip_to_binary(str(subnet.network_address + 1))],
            "HostMax"  : [str(subnet.broadcast_address - 1), ip_to_binary(str(subnet.broadcast_address - 1))],
            "Broadcast": [str(subnet.broadcast_address), ip_to_binary(str(subnet.broadcast_address))],
            "HostsNet" : str(subnet.num_addresses - 2)
        })
    return sub_redes


def IpCalc(ip_cidr, new_prefix):
    red = calculate_network(ip_cidr)
    if int(new_prefix) > 0:
        sub_redes = calculate_subnets(ip_cidr, int(new_prefix))

    # Preparamos los datos a mostrar
    datos_resultado = []
    header = ['Dato', 'IP (DEC)', 'IP (BIN)']
    datos_resultado.append(header)
    for campo, data in red.items():
        if campo != "HostsNet":
            datos_resultado.append([campo, data[0], data[1]])
        else:
            datos_resultado.append([campo, str(data)])

    datos_resultado.append('')
    if int(new_prefix) > 0:
        total_sn = len(sub_redes)
        datos_resultado.append(['Total Subnet\'s: ', total_sn])
        datos_resultado.append('')
        for data in sub_redes:
            for campo_sn, data_sn in data.items():
                if campo_sn != "HostsNet" and campo_sn != 'red_num':
                    datos_resultado.append([campo_sn, data_sn[0], data_sn[1]])
                else:
                    datos_resultado.append(['Red Nº:' if campo_sn == 'red_num' else campo_sn, data_sn])
                    if campo_sn == 'HostsNet':
                        datos_resultado.append('')

    resultado = tabulate(datos_resultado, headers="firstrow", tablefmt="simple")
    
    return resultado


if __name__ == "__main__":
    if len(sys.argv) == 3:
        print(IpCalc(sys.argv[1], sys.argv[2]))
    else:
        print(IpCalc(sys.argv[1], 0))
    
