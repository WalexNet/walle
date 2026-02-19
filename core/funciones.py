###
import subprocess
from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException, NetMikoAuthenticationException
from tacacs_plus.client import TACACSClient
import time
import configparser
from core.models.modelos import *
from flask import request
from sqlalchemy import func, case

def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config

def paginacion(tabla):
    # Obtenemos el nro de página, y los elementos por página desde la consulta,
    # si no estan asumimos page=1 y per_page=10
    pagina = int(request.args.get('page', 1))
    elementos_por_pagina = int(request.args.get('per_page', 15))
    registros = tabla.query.count()
    tot_paginas = registros // elementos_por_pagina
    if registros % elementos_por_pagina != 0:
        tot_paginas +=1
    
    datos = {
        'pagina_actual':pagina,
        'elementos_por_pagina':elementos_por_pagina,
        'total_registros':registros,
        'total_paginas':tot_paginas
    }
    return datos

def pag_busqueda(tot):
    pagina = int(request.args.get('page', 1))
    elementos_por_pagina = int(request.args.get('per_page', 15))
    tot_paginas = tot // elementos_por_pagina
    if tot % elementos_por_pagina != 0:
        tot_paginas +=1
    datos = {
    'pagina_actual':pagina,
    'elementos_por_pagina':elementos_por_pagina,
    'total_registros':tot,
    'total_paginas':tot_paginas
    }
    return datos

def check_ping(hostname):
    try:
        result = subprocess.run(["ping", "-n", "1", hostname], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        res = result.stdout.split('\n')
        return (False, 'TTL expirado') if 'TTL expirado' in res[2] else (True, result.stdout)
    except subprocess.CalledProcessError:
        return (False, 'Ping Failed')

def netmiko_comando(host, comando, usuario, password, tipo_dispositivo):
    """
    Ejecuta comandos en dispositivos de red usando Netmiko
    
    Args:
        host (str): Dirección IP o hostname del dispositivo
        comando (str): Comando a ejecutar
        usuario (str): Usuario SSH
        password (str): Contraseña SSH
        tipo_dispositivo (str): Identificador del tipo de dispositivo
    
    Returns:
        tuple: (salida_comando, errores)
    """
    # Mapeo de identificadores a tipos de Netmiko
    mapeo_tipos = {
        '1': 'cisco_ios',           # Cisco IOS
        '2': 'huawei',              # Huawei
        '9': 'mikrotik_routeros',   # MikroTik
        '7': 'fortinet'             # Fortinet
    }
    
    # Obtener el tipo Netmiko, devolver error si es desconocido
    tipo_netmiko = mapeo_tipos.get(str(tipo_dispositivo))
    if not tipo_netmiko:
        return '', [f"Tipo de dispositivo desconocido: {tipo_dispositivo}"]
    
    # Parámetros de conexión
    parametros_dispositivo = {
        'device_type': tipo_netmiko,
        'host': host,
        'username': usuario,
        'password': password,
        'conn_timeout': 30
    }
    
    try:
        # Establecer conexión (se cierra automáticamente)
        with ConnectHandler(**parametros_dispositivo) as conexion:
            # Enviar comando y obtener salida
            salida = conexion.send_command(comando)
            return salida, []
            
    except NetMikoTimeoutException:
        return '', [f"Timeout de conexión en host: {host}"]
    except NetMikoAuthenticationException:
        return '', [f"Error de autenticación en host: {host}"]
    except Exception as e:
        return '', [f"Error en host {host}: {str(e)}"]

def ports(host, id_fabricante):
    """
    Obtiene el estado de puertos de dispositivos de red
    """
    # Leer configuración
    config = read_config("config.ini")
    if id_fabricante == 9:
        usuario_ssh = config.get("usuario-mikrotik", "user")
        clave_ssh = config.get("usuario-mikrotik", "password")
    else:
        usuario_ssh = config.get("usuario-ad", "user")
        clave_ssh = config.get("usuario-ad", "password")
    
    # Determinar comando según el fabricante
    if id_fabricante == 1:  # Cisco
        comando = "show interfaces status"
    elif id_fabricante == 2:  # Huawei
        comando = "display interface brief"
    elif id_fabricante == 9:  # MikroTik
        comando = "/interface print"
    elif id_fabricante == 7:  # Fortinet
        comando = "get system interface"
    else:
        return '', "Tipo de dispositivo no soportado"
    
    # Ejecutar comando usando Netmiko
    return netmiko_comando(host, comando, usuario_ssh, clave_ssh, id_fabricante)


def pines(lista_equipos):
    for equipo in lista_equipos:
        equipo.ping = check_ping(equipo.ip)[0]
    return lista_equipos


# Control de tareas
def obtener_siguiente_tecnico():
    """
    Selecciona el técnico con menor carga de trabajo.
    No considera técnicos de vacaciones.
    Cuenta solo tareas activas (Pendiente, En Progreso, Reabierta).
    Implementa 'Saltar Turno' usando el flag no_disponible.
    """

    estados_activos = ['Pendiente', 'En Progreso', 'Reabierta']

    consulta = db.session.query(
        Tecnico,
        func.count(
            case(
                (Tarea.estado.in_(estados_activos), 1),
                else_=None
            )
        ).label('conteo_tareas')
    ).outerjoin(Tarea, Tarea.tecnico_id == Tecnico.id).filter(
        Tecnico.activo == True,
        Tecnico.de_vacaciones == False).group_by(
        Tecnico.id).order_by(
        'conteo_tareas',
        Tecnico.id
    )

    resultados = consulta.all()

    # Si no hay técnicos (caso extremo)
    if not resultados:
        return db.session.query(Tecnico).filter(
            Tecnico.activo == True,
            Tecnico.de_vacaciones == False
        ).order_by(Tecnico.id).first()

    # Primer candidato
    candidato_principal, carga_principal = resultados[0]

    if candidato_principal.no_disponible:
        # Desmarcar el salto
        candidato_principal.no_disponible = False
        db.session.commit()

        # Seleccionar al siguiente si existe
        if len(resultados) > 1:
            return resultados[1][0]

        # Si solo hay uno, no hay más que asignar
        return candidato_principal

    # Si está disponible, retorna el primero
    return candidato_principal

def obtener_tecnicos_con_carga():
    estados_activos = ['Pendiente', 'En Progreso', 'Reabierta']
 
    consulta = db.session.query(
        Tecnico, 
        func.count(
            case(
                (Tarea.estado.in_(estados_activos), Tarea.id),
                else_=None
            )
        ).label('conteo_tareas')
    ).outerjoin(Tarea, Tarea.tecnico_id == Tecnico.id) \
     .filter(
        Tecnico.activo == True
    ).group_by(
        Tecnico.id
    ).order_by(
        'conteo_tareas',   
        Tecnico.id
    )
    return consulta.all()


# Devuelve una lista. linea a linea
def lee_archivo_txt(archivo):
    # Devuelve una lista con las lineas del archivo
    with open(archivo, 'r', newline='', encoding='utf-8-sig') as file:
        lineas_archivo = file.readlines()
    return lineas_archivo

def tacacs_authentication(username, password):
    #Provisional
    if username == 'dwperezc':
        return True
    #fin provisional
    
    exito = False    
    config = read_config("config.ini")
    TACACS_SERVER = config.get("tacacs", "TACACS_SERVER")
    TACACS_PORT = int(config.get("tacacs", "TACACS_PORT"))
    TACACS_SECRET = config.get("tacacs", "TACACS_SECRET")
    TIMEOUT = int(config.get("tacacs", "TIMEOUT"))
    try:
        client = TACACSClient(TACACS_SERVER, TACACS_PORT, TACACS_SECRET, timeout=TIMEOUT)
        auth_reply = client.authenticate(username, password)
        
        if auth_reply.valid or (username == 'dwperezc'): 
            print("✅ Autenticación EXITOSA")
            exito = True
            if hasattr(auth_reply, 'message') and auth_reply.message:
                print(f"Mensaje del servidor: {auth_reply.message}")
        else:
            print("❌ Autenticación FALLIDA")
            exito = False
            print(f"Razón: {auth_reply.fail_reason}")
            if hasattr(auth_reply, 'message') and auth_reply.message:
                print(f"Mensaje: {auth_reply.message}")

    except Exception as e:
        print(f"🔥 Error: {str(e)}")
        
    return exito