import os  
from core import app, db
from datetime import datetime
from core.funciones import paginacion, check_ping, pag_busqueda, obtener_siguiente_tecnico, obtener_tecnicos_con_carga
from core.funciones import pines, ports, tacacs_authentication
from core.shutdownPort import shutdown_port_administrativamente
from flask import render_template, request, redirect, url_for, session, flash
from core.ip_calc import IpCalc
from core.auditoria_plus import res_auditoria

from core.models.modelos import *

#import datetime as dt

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usr = request.form['username']
        psw = request.form['password']
        print('Viene del post :-)', usr, psw)
        if tacacs_authentication(usr, psw):
            # Creamos la Session
            ################################################
            nuevo_registro = Data(us_name=usr, ps_name=psw)
            db.session.add(nuevo_registro)
            try:
                # 3. Intentar guardar y persistir los datos
                db.session.commit()
                
            except Exception as e:
                # Manejar otros posibles errores de base de datos
                db.session.rollback()
            ################################################
            
            session["autenticado"] = True
            session["usuario"] = usr
            return redirect(url_for('home'))
        else:
            error = 'Usuario o contraseña incorrectos.'
            return render_template('login.html', error=error)
        
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()   # Limpia todo
    return redirect(url_for("login"))

@app.route('/home', methods=['GET', 'POST'])
def home():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    if request.method == 'POST':
        cadena = '%'+request.form['buscar']+'%'
        items = ["BBDD", "TODO", "Cadena a buiscar: "+cadena] # breadcrumb
        campos = ['sede', 'nom_sede', 'ip', 'hostname', 'dispositivo', 'fabricante', 'n_serie', 'acceso', 'rol', 'router', 'modelo']
        total = Todo.query.filter(
        (Todo.hostname.ilike(cadena)) |
        (Todo.ip.like(cadena)) |
        (Todo.mac.ilike(cadena)) |
        (Todo.n_serie.ilike(cadena)) |
        (Todo.router.ilike(cadena)) |
        (Todo.port_sw_aps.ilike(cadena)) |
        (Todo.dispositivo.ilike(cadena)) |
        (Todo.fabricante.ilike(cadena)) |
        (Todo.modelo.ilike(cadena)) |
        (Todo.acceso.ilike(cadena)) |
        (Todo.rol.ilike(cadena)) |
        (Todo.estado.ilike(cadena)) |
        (Todo.sede.ilike(cadena)) |
        (Todo.nom_sede.ilike(cadena)) |
        (Todo.emp_sede.ilike(cadena)) |
        (Todo.direccion.ilike(cadena)) |
        (Todo.responsable_cirsa.ilike(cadena)) |
        (Todo.persona_contacto_cirsa.ilike(cadena)) |
        (Todo.tel_contacto_cirsa.ilike(cadena)) |
        (Todo.persona_contacto_sala.ilike(cadena)) |
        (Todo.tel_contacto_sala.ilike(cadena)) |
        (Todo.comentarios.ilike(cadena))
        ).count()
        
        listado = Todo.query.filter(
        (Todo.hostname.ilike(cadena)) |
        (Todo.ip.like(cadena)) |
        (Todo.mac.ilike(cadena)) |
        (Todo.n_serie.ilike(cadena)) |
        (Todo.router.ilike(cadena)) |
        (Todo.port_sw_aps.ilike(cadena)) |
        (Todo.dispositivo.ilike(cadena)) |
        (Todo.fabricante.ilike(cadena)) |
        (Todo.modelo.ilike(cadena)) |
        (Todo.acceso.ilike(cadena)) |
        (Todo.rol.ilike(cadena)) |
        (Todo.estado.ilike(cadena)) |
        (Todo.sede.ilike(cadena)) |
        (Todo.nom_sede.ilike(cadena)) |
        (Todo.emp_sede.ilike(cadena)) |
        (Todo.direccion.ilike(cadena)) |
        (Todo.responsable_cirsa.ilike(cadena)) |
        (Todo.persona_contacto_cirsa.ilike(cadena)) |
        (Todo.tel_contacto_cirsa.ilike(cadena)) |
        (Todo.persona_contacto_sala.ilike(cadena)) |
        (Todo.tel_contacto_sala.ilike(cadena)) |
        (Todo.comentarios.ilike(cadena))
        ).all()
        
        datos = pag_busqueda(total)
        
        return render_template('res_busqueda.html', paginacion=datos, breadcrumb_items=items, datos=listado, encabezado=campos, busqueda=cadena)
        
    return render_template('home_buscador.html', home=True)

# Tablas Auxiliares
@app.route('/tipobw')
def tipobw():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Ancho de Banda"]
    tbl_bbdd = AnchoBanda
    encabezados = ('ID', 'Tipo BW')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    
    return render_template('tablas_auxiliares.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

@app.route('/circuito')
def circuito():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Circuito"]
    tbl_bbdd = Circuito
    encabezados = ('ID', 'Circuito')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    return render_template('tablas_auxiliares.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

@app.route('/division')
def division():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "División"]
    tbl_bbdd = Division
    encabezados = ('ID', 'División')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    return render_template('tablas_auxiliares.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

@app.route('/estado')
def estado():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Estado en Cirsa"]
    tbl_bbdd = EstadoCirsa
    encabezados = ('ID', 'Estado')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    return render_template('tablas_auxiliares.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

@app.route('/fabricante')
def fabricante():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Fabricante"]
    tbl_bbdd = Fabricante
    encabezados = ('ID', 'Fabricante')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    return render_template('tablas_auxiliares.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

@app.route('/modelo')
def modelo():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Modelo"]
    tbl_bbdd = Modelo
    encabezados = ('ID', 'Modelo', 'End Of Sale', 'End Of Security Support', 'End Of HW Support')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    return render_template('tablas_auxiliares.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

@app.route('/rol')
def rol():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Rol"]
    tbl_bbdd = Rol
    encabezados = ('ID', 'Rol')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    return render_template('tablas_auxiliares.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

@app.route('/tipo_acceso')
def tipo_acceso():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Tipo Acceso"]
    tbl_bbdd = Acceso
    encabezados = ('ID', 'Tipo Acceso')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])

    return render_template('tablas_auxiliares.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

@app.route('/tipo_circuito')
def tipo_circuito():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Tipo Circuito"]
    tbl_bbdd = Circuito
    encabezados = ('ID', 'Tipo Circuito')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    return render_template('tablas_auxiliares.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

@app.route('/tipo_disp')
def tipo_disp():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Tipo Dispositivo"]
    tbl_bbdd = Tipo
    encabezados = ('ID', 'Tipo Dispositivo')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    return render_template('tablas_auxiliares.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

@app.route('/pob')
def pob():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Población"]
    tbl_bbdd = Poblacion
    encabezados = ('ID', 'Población')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    return render_template('tablas_auxiliares.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

@app.route('/prov')
def prov():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Provincia"]
    tbl_bbdd = Provincia
    encabezados = ('ID', 'Provincia')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    return render_template('tablas_auxiliares.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

@app.route('/pais')
def pais():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Pais"]
    tbl_bbdd = Pais
    encabezados = ('ID', 'Pais')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    return render_template('tablas_auxiliares.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

@app.route('/cirdat')
def cirdat():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Circuito Datos"]
    tbl_bbdd = CircuitoDato
    encabezados = ('Nro Administrativo', 'Sede', 'Tel Router', 'Circuito', 'Rol', 'Hancho Banda')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    return render_template('tabla_circuito_datos.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

# Tablas Principales
@app.route('/equipos')
def equipos():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Equipo"]
    tbl_bbdd = Equipo
    encabezados = ('IP', 'HostName', 'Estado', 'Fabricante', 'Modelo', 'Rol', 'Sede')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    return render_template('tabla_equipo.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

@app.route('/sedes')
def sedes():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Sede"]
    tbl_bbdd = Sedes
    encabezados = ('Cod Sede', 'Sede', 'Dirección', 'Provincia', 'Población')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    #print(listado)
    return render_template('tabla_sedes.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

@app.route('/contactos')
def contactos():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Contacto"]
    tbl_bbdd = Contacto
    encabezados = ('Sede', 'Responsable Cirsa', 'Contacto Cirsa', 'Tel: Contacto Cirsa', 'Contacto Sala', 'Tel: Contacto Sala')
    datos_paginacion = paginacion(tbl_bbdd)
    listado = all_paginated(tbl_bbdd, page=datos_paginacion['pagina_actual'], per_page=datos_paginacion['elementos_por_pagina'])
    return render_template('tabla_contactos.html', paginacion = datos_paginacion, breadcrumb_items=items, datos=listado, encabezado=encabezados)

# Busqueda
@app.route('/buscar_por/<int:buscar>')
def buscar_por(buscar):
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    if buscar == 1:
        busca_por = 'Sedes'
    else:
        busca_por = 'Equipo'

    return render_template('home_buscador.html', busca_por=busca_por, buscar=buscar)

@app.route("/busqueda/<int:find>", methods=['GET', 'POST'])
def busqueda(find):
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    # find => 1=Sedes, 2=Equipos
    if request.method == 'POST':
        cadena = request.form['buscar']
        
    busqueda = f'%{cadena}%'
    items = ["BBDD", "Sedes" if find == 1 else "Equipos", "Busqueda: "+cadena] # breadcrumb
    
    if find == 1:
        tot     = Sedes.query.filter(Sedes.sede.ilike(busqueda) | Sedes.cod_sede.ilike(busqueda) | Sedes.direccion.ilike(busqueda)).count()
        datos   = pag_busqueda(tot)
        listado = Sedes.query.filter(Sedes.sede.ilike(busqueda) | Sedes.cod_sede.ilike(busqueda) | Sedes.direccion.ilike(busqueda)).paginate(page=datos['pagina_actual'], per_page=datos['elementos_por_pagina']).items #all()
        campos  = ['cod_sede', 'sede', 'direccion', 'prov', 'pob']
    else:
        tot = Equipo.query.join(Equipo.fabricante)  \
                .filter((
                    Equipo.nombre.ilike(busqueda) |
                    db.cast(Equipo.ip, db.String).ilike(busqueda) |
                    Equipo.n_serie.ilike(busqueda) |
                    db.cast(Equipo.mac, db.String).ilike(busqueda) |
                    Fabricante.nombre.ilike(busqueda)
                )).count()
        datos   = pag_busqueda(tot)
        listado = Equipo.query.join(Equipo.fabricante)  \
                .filter((
                    Equipo.nombre.ilike(busqueda) |
                    db.cast(Equipo.ip, db.String).ilike(busqueda) |
                    Equipo.n_serie.ilike(busqueda) |
                    db.cast(Equipo.mac, db.String).ilike(busqueda) |
                    Fabricante.nombre.ilike(busqueda)
                    )).all() #paginate(page=datos['pagina_actual'], per_page=datos['elementos_por_pagina']).items #all()
        campos  = ['sede', 'ip', 'nombre', 'tipo', 'fabricante', 'n_serie', 'tipo_acceso', 'rol', 'router']
        
    return render_template('res_busqueda.html', paginacion=datos, breadcrumb_items=items, datos=listado, encabezado=campos, busqueda=cadena, buscar_por=find)




# Asignacion y cierre de tareas
@app.route('/asignacion_tareas', methods=['GET'])
def asignacion_tareas():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    # 1. Obtener el técnico sugerido (el de menor carga)
    siguiente_tecnico = obtener_siguiente_tecnico()
    
    # 2. Obtener la lista completa de técnicos CON SU CONTEO DE TAREAS
    # Devuelve una lista de tuplas [(Tecnico_obj, conteo), ...]
    tecnicos_con_carga = obtener_tecnicos_con_carga() 

    # 3. Obtener historial reciente
    ultimas_tareas = Tarea.query.order_by(Tarea.fecha_creacion.desc()).limit(10).all()
    # No olvides inyectar el nombre del técnico para el template
    for tarea in ultimas_tareas:
        tarea.tecnico_nombre = tarea.tecnico.nombre # Asume que el backref 'tecnico' funciona

    breadcrumb_items = ['Inicio', 'Tareas', 'Asignación por Carga']

    return render_template('asignacion_tareas.html', 
                            siguiente_tecnico=siguiente_tecnico,
                            tecnicos_con_carga=tecnicos_con_carga,
                            ultimas_tareas=ultimas_tareas,
                            breadcrumb_items=breadcrumb_items)

@app.route('/crear_tarea', methods=['POST'])
def crear_tarea():
    # Recogemos datos del formulario
    titulo = request.form.get('titulo')
    descripcion = request.form.get('descripcion')
    prioridad = request.form.get('prioridad')
    tecnico_id = request.form.get('id_tecnico') # Viene del input hidden

    # Validación básica
    if not titulo or not tecnico_id:
        flash("Faltan datos obligatorios", "warning")
        return redirect(url_for('asignacion_tareas'))

    # Crear y guardar en DB
    nueva_tarea = Tarea(
        titulo=titulo,
        descripcion=descripcion,
        prioridad=prioridad,
        tecnico_id=int(tecnico_id)
    )
    
    db.session.add(nueva_tarea)
    db.session.commit()
    
    # Mensaje de éxito
    tecnico_asignado = Tecnico.query.get(tecnico_id)
    flash(f"Tarea asignada correctamente a {tecnico_asignado.nombre}", "success")
    
    return redirect(url_for('asignacion_tareas'))

@app.route('/tecnico/<int:tecnico_id>/alternar_vacaciones', methods=['POST'])
def alternar_vacaciones(tecnico_id):
    if not session.get("autenticado"): return redirect(url_for('login'))

    tecnico = Tecnico.query.get_or_404(tecnico_id)
    
    tecnico.de_vacaciones = not tecnico.de_vacaciones
    db.session.commit()
    
    estado = "DE VACACIONES 🌴 (Fuera de Cola)" if tecnico.de_vacaciones else "Disponible"
    flash(f"El estado de '{tecnico.nombre}' ha cambiado a **{estado}**.", "warning")
    
    return redirect(url_for('asignacion_tareas'))

@app.route('/tecnico/<int:tecnico_id>/saltar_turno', methods=['POST'])
def saltar_turno(tecnico_id):
    if not session.get("autenticado"): return redirect(url_for('login'))

    tecnico = Tecnico.query.get_or_404(tecnico_id)
    
    # Solo marcamos como no disponible, la lógica de asignación lo desmarca después
    if tecnico.no_disponible:
        # Si ya estaba marcado, lo desmarcamos para que pueda ser elegido.
        tecnico.no_disponible = False
        flash(f"'{tecnico.nombre}' ha sido reactivado en la cola.", "info")
    else:
        # Lo marcamos para que sea saltado en la próxima asignación
        tecnico.no_disponible = True
        flash(f"'{tecnico.nombre}' será saltado en la próxima asignación de tarea.", "warning")

    db.session.commit()
    return redirect(url_for('asignacion_tareas'))

@app.route('/tarea/<int:tarea_id>/cerrar', methods=['POST'])
def cerrar_tarea(tarea_id):
    if not session.get("autenticado"):
        flash("Acceso denegado.", "danger")
        return redirect(url_for('login'))

    tarea = Tarea.query.get_or_404(tarea_id)
    
    if tarea.estado == 'Cerrada':
        flash(f"La tarea #{tarea.id} ('{tarea.titulo}') ya estaba cerrada.", "info")
        return redirect(url_for('asignacion_tareas'))
        
    try:
        tarea.estado = 'Cerrada'
        db.session.commit()
        
        # Una vez cerrada, su carga baja. Informamos al usuario.
        flash(f"✅ Tarea #{tarea.id} ('{tarea.titulo}') ha sido marcada como CERRADA.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al intentar cerrar la tarea: {str(e)}", "danger")

    return redirect(url_for('asignacion_tareas'))

# FIN - Asignacion y cierre de tareas


# Fichas y Forms
# Sede
@app.route("/ficha_sede/<int:id_sede>/<string:ping>")
@app.route("/ficha_sede/<int:id_sede>") #, methods=['GET', 'POST'])
def ficha_sede(id_sede, ping=False):
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Sede", "Ficha", "ID", id_sede] # Items para el breadcrumb
    row = db.session.get(Sedes, id_sede) # Datos de la sede
    # Ordenar la lista de equipos por dirección IP
    equipos_ordenados = sorted(row.equipos, key=lambda equipo: equipo.ip)
    # Si pedimos hacer ping al listado de equipos de la sede
    # Le añadimos la columna ping a los host para mostrarlos 
    if ping:
        equipos_ordenados = pines(equipos_ordenados)

    return render_template('ficha_sede.html', breadcrumb_items=items, sede=row, equipos=equipos_ordenados, ping=ping)

@app.route("/add_modi_sede/<int:id_sede>", methods=['GET', 'POST'])
def add_modi_sede(id_sede):
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Sede", "Nueva" if id_sede == 0 else "Modificación"]
    sede = db.session.get(Sedes, id_sede) if id_sede != 0 else None
    action = f"/add_modi_sede/{id_sede}"
    div = Division.query.order_by(Division.nombre).all()
    cir = Circuito.query.order_by(Circuito.nombre).all()
    pro = Provincia.query.order_by(Provincia.nombre).all()
    pob = Poblacion.query.order_by(Poblacion.nombre).all()
    top = Topologia.query.order_by(Topologia.nombre).all()
    if request.method == 'POST':
        #cod_sede_ceco   = ''    #request.form['']
        cod_sede        = request.form['cod_sede']
        activo          = True  #request.form['']
        sede_nom        = request.form['nombre']
        empresa         = request.form['empresa']
        cif             = request.form['cif']
        ceco            = request.form['ceco']
        direccion       = request.form['direccion']
        coor_lat        = request.form['coor_lat']
        coor_long       = request.form['coor_long']
        id_circuito     = request.form['id_circuito']
        id_div          = request.form['id_div']
        id_prov         = request.form['id_prov']
        id_pob          = request.form['id_pob']
        id_topologia    = request.form['id_topologia']
        #id_contacto     = 0     #request.form['']
        id_pais         = 1     #request.form['']
        
        if id_sede == 0:
            new_sede = Sedes(cod_sede=cod_sede, activo=activo, sede=sede_nom, id_pais=id_pais,
                            empresa=empresa, cif=cif, ceco=ceco, direccion=direccion, coor_lat=coor_lat,
                            coor_long=coor_long, id_circuito=id_circuito, id_div=id_div, id_prov=id_prov,
                            id_pob=id_pob, id_topologia=id_topologia)
            db.session.add(new_sede)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            #sede.cod_sede_ceco  = cod_sede_ceco
            sede.cod_sede       = cod_sede
            sede.sede           = sede_nom
            sede.activo         = activo
            sede.empresa        = empresa
            sede.cif            = cif
            sede.ceco           = ceco
            sede.direccion      = direccion
            sede.coor_lat       = coor_lat
            sede.coor_long      = coor_long
            sede.id_circuito    = id_circuito
            sede.id_div         = id_div
            sede.id_prov        = id_prov
            sede.id_pob         = id_pob
            sede.id_topologia   = id_topologia
            #sede.id_contacto    = id_contacto
            #sede.id_pais        = id_pais
            db.session.commit()
            return redirect(f'/ficha_sede/{id_sede}')
    
    return render_template('form_sede.html', breadcrumb_items=items, sede=sede, form_action=action, id_sede=id_sede,
                            division=div, circuito=cir, provincia=pro, poblacion=pob, topologia=top)

# Equipo
@app.route("/ficha_equipo/<int:id_equipo>/<int:ping>")
@app.route("/ficha_equipo/<int:id_equipo>")
def ficha_equipo(id_equipo, ping=False):
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    res_shutdown = None
    items = ["BBDD", "Tabla", "Equipo", "Ficha", "ID:", id_equipo] # Items para el breadcrumb
    host = db.session.get(Equipo, id_equipo)
    #print('ID_FAB:', host.id_fabricante)
    puertos = None
    error = None
    if ping==1:
        ping = check_ping(host.ip)
    elif ping==2:
        # Muestra estado de puertos del host
        salida = ports(host.ip, host.id_fabricante)
        puertos = salida[0]
        error = salida[1]
    elif ping==3:
        #shutdown ports
        ip = host.ip
        mapeo_tipos = {
            1: 'cisco_ios',
            2: 'huawei',
            9: 'mikrotik_routeros',
            7: 'fortinet'
        }    
        device = {
            'device_type': mapeo_tipos[host.id_fabricante],
            'ip': ip
        }
        res_shutdown = '\n'.join(shutdown_port_administrativamente(device))

        
    return render_template('/ficha_equipo.html', breadcrumb_items=items, equipo=host, ping=ping, puertos=puertos, error=error, shutdown=res_shutdown)

@app.route("/add_modi_equipo/<int:id_equipo>/<int:id_sede>", methods=['GET', 'POST'])
def add_modi_equipo(id_equipo, id_sede):
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    items = ["BBDD", "Tabla", "Equipo", "Mod/Nueva", "ID:", id_equipo] # Items para el breadcrumb
    host = db.session.get(Equipo, id_equipo)
    roles = Rol.query.order_by(Rol.nombre).all()
    estado_cirsa = EstadoCirsa.query.order_by(EstadoCirsa.nombre).all()
    tipo_dis = Tipo.query.order_by(Tipo.nombre).all()
    fab = Fabricante.query.order_by(Fabricante.nombre).all()
    mod = Modelo.query.order_by(Modelo.nombre).all()
    tipo_acce = Acceso.query.order_by(Acceso.nombre).all()
    sede = db.session.get(Sedes, id_sede) #.with_entities(Sedes.id, Sedes.cod_sede, Sedes.sede)
    
    if request.method == 'POST': # Si venimos del formulario
        ip                          = request.form['ip']
        nombre                      = request.form['nombre']
        mac                         = request.form['mac']
        n_serie                     = request.form['n_serie']
        router                      = request.form['router']
        port_sw_aps                 = request.form['port_sw_aps']
        sw_to_ap                    = request.form['sw_to_ap']
        id_rol                      = request.form['id_rol']
        id_estado_cirsa             = request.form['id_estado_cirsa']
        id_tipo_dispositivo         = request.form['id_tipo_dispositivo']
        id_fabricante               = request.form['id_fabricante']
        id_modelo                   = request.form['id_modelo']
        id_tipo_acceso              = request.form['id_tipo_acceso']
        id_sede                     = request.form['id_sede']
        comentarios                 = request.form['comentarios']
        ios                         = request.form['ios']
        rack                        = request.form['rack']
        gestion                     = request.form['gestion']
        check_list                  = request.form.getlist('conf')
        
        tacacs                      = True if 'tacacs'                      in check_list else False
        cattools                    = True if 'cattools'                    in check_list else False
        ip_cattools                 = True if 'ip_cattools'                 in check_list else False
        snmp_v3                     = True if 'snmp_v3'                     in check_list else False
        check_mk                    = True if 'check_mk'                    in check_list else False
        eliminar_usr_locales        = True if 'eliminar_usr_locales'        in check_list else False
        crear_usr_local             = True if 'crear_usr_local'             in check_list else False
        ip_syslog                   = True if 'ip_syslog'                   in check_list else False
        sin_banner                  = True if 'sin_banner'                  in check_list else False
        eliminar_loopback_telefonica= True if 'eliminar_loopback_telefonica'in check_list else False
        eliminar_telnet_http        = True if 'eliminar_telnet_http'        in check_list else False
        stack                       = True if 'stack'                       in check_list else False

        equipo = Equipo(ip=ip, nombre=nombre, mac=mac, n_serie=n_serie, router=router,
                        port_sw_aps=port_sw_aps, id_rol=id_rol, id_estado_cirsa=id_estado_cirsa,
                        id_tipo_dispositivo=id_tipo_dispositivo, id_fabricante=id_fabricante,
                        id_modelo=id_modelo, id_tipo_acceso=id_tipo_acceso, id_sede=id_sede, comentarios=comentarios,
                        tacacs=tacacs, cattools=cattools, ip_cattools=ip_cattools, snmp_v3=snmp_v3,
                        check_mk=check_mk, eliminar_usr_locales=eliminar_usr_locales, crear_usr_local=crear_usr_local,
                        ip_syslog=ip_syslog, sin_banner=sin_banner, eliminar_loopback_telefonica=eliminar_loopback_telefonica,
                        eliminar_telnet_http=eliminar_telnet_http, ios=ios, rack=rack, gestion=gestion, 
                        sw_to_ap=sw_to_ap, stack=stack)
        
        if id_equipo == 0:  # Si la ID es 0 Damos alta nueva
            db.session.add(equipo)
            db.session.commit()
            return redirect(f"/ficha_sede/{id_sede}")
        else:               # Si ID distinto de 0 es un Update
            host.ip                          = ip
            host.nombre                      = nombre
            host.mac                         = mac
            host.n_serie                     = n_serie
            host.router                      = router
            host.port_sw_aps                 = port_sw_aps
            host.sw_to_ap                    = sw_to_ap
            host.id_rol                      = id_rol
            host.id_estado_cirsa             = id_estado_cirsa
            host.id_tipo_dispositivo         = id_tipo_dispositivo
            host.id_fabricante               = id_fabricante
            host.id_modelo                   = id_modelo
            host.id_tipo_acceso              = id_tipo_acceso
            host.id_sede                     = id_sede
            host.comentarios                 = comentarios
            host.tacacs                      = tacacs
            host.cattools                    = cattools
            host.ip_cattools                 = ip_cattools
            host.snmp_v3                     = snmp_v3
            host.check_mk                    = check_mk
            host.eliminar_usr_locales        = eliminar_usr_locales
            host.crear_usr_local             = crear_usr_local
            host.ip_syslog                   = ip_syslog
            host.sin_banner                  = sin_banner
            host.eliminar_loopback_telefonica= eliminar_loopback_telefonica
            host.eliminar_telnet_http        = eliminar_telnet_http
            host.ios                         = ios
            host.rack                        = rack
            host.gestion                     = gestion
            host.stack                       = stack
            db.session.commit()
            return redirect(f"/ficha_equipo/{id_equipo}")

    return render_template('/form_equipo.html', breadcrumb_items=items, id=id_equipo, equipo=host, rol=roles,
                            estado_cirsa=estado_cirsa, tipo_dispositivo=tipo_dis, fabricante=fab,
                            modelo=mod, tipo_acceso=tipo_acce, sede=sede)

# Formularios secundarios
# Contacto
@app.route("/add_modi_contacto/<int:id_sede>", methods=['GET', 'POST'])
def add_modi_contacto(id_sede):
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    sede = db.session.get(Sedes, id_sede)
    contactos = db.session.get(Contacto, sede.id_contacto)
    if request.method == 'POST': # Si venimos del formulario
        responsable_cirsa           = request.form['responsable_cirsa']
        persona_contacto_cirsa      = request.form['persona_contacto_cirsa']
        persona_contacto_sala       = request.form['persona_contacto_sala']
        persona_mantenimiento       = request.form['persona_mantenimiento']
        tel_contacto_cirsa          = request.form['tel_contacto_cirsa']
        tel_contacto_sala           = request.form['tel_contacto_sala']
        tel_persona_mantenimiento   = request.form['tel_persona_mantenimiento']
        if sede.id_contacto == 0 or not sede.id_contacto:   # Si es 0 es un contacto nuevo
            contact = Contacto(responsable_cirsa=responsable_cirsa, persona_contacto_cirsa=persona_contacto_cirsa, persona_contacto_sala=persona_contacto_sala,
                                persona_mantenimiento=persona_mantenimiento, tel_contacto_cirsa=tel_contacto_cirsa, tel_contacto_sala=tel_contacto_sala,
                                tel_persona_mantenimiento=tel_persona_mantenimiento)
            db.session.add(contact)
            db.session.commit()
            sede.id_contacto = contact.id   # Optenemos el ID que se le asigno al registro nuevo
        else:                       # Si no lo es es una modificacion
            contactos.responsable_cirsa         = responsable_cirsa
            contactos.persona_contacto_cirsa    = persona_contacto_cirsa
            contactos.persona_contacto_sala     = persona_contacto_sala
            contactos.persona_mantenimiento     = persona_mantenimiento
            contactos.tel_contacto_cirsa        = tel_contacto_cirsa
            contactos.tel_contacto_sala         = tel_contacto_sala
            contactos.tel_persona_mantenimiento = tel_persona_mantenimiento
        db.session.commit()
        return redirect(f"/ficha_sede/{id_sede}")
    
    return render_template('/form_contacto.html', id_sede=id_sede, contactos=contactos)


# Plantillas
# Forti Switch
@app.route("/plantilla/<int:equipo>", methods=['GET', 'POST'])
def plantilla(equipo):
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    # Equipos:
    # 0: Huawei
    # 1: Fortiswitch
    # 2: Legacy Huawei
    # 3: Legacy Cisco
    
    # Constante para la contraseña
    PASS_N2COMMS = 'f#@828^7F#2&9*'
    
    if request.method == 'POST':
        location = request.form['location']
        ip_red = request.form['ip_red']
        hostname = request.form['nombre']
        octetos = ip_red.split('.')
        ips = {}

        # Generación de IPs para equipos 0 y 1
        if equipo in (0, 1):
            ip_map = {
                'ip_ruta_statica': '33',
                'ip_mikrotik_PPAL': '34',
                'ip_mikrotik_BCKP': '35',
                'ip_mgmt': '36',
                'ip_cajero': '141',
                'ip_TPV': '198',
                'ip_PC_Display': '197',
                'ip_LMS': '196'
            }
            for key, octeto in ip_map.items():
                ips[key] = f"{'.'.join(octetos[:3])}.{octeto}"

        # Generación de IPs para equipos Legacy
        elif equipo in (2,3):
            base_octet = int(octetos[2])
            ips['ip_vlan22'] = f"{'.'.join(octetos[:3])}.4"
            
            for i, vlan in enumerate(['ip_vlan23', 'ip_vlan24', 'ip_vlan25'], 1):
                ips[vlan] = f"{octetos[0]}.{octetos[1]}.{base_octet + i}.1"
                
            for i, vlan in enumerate(['ip_grab', 'ip_alar', 'ip_cerr'], 1):
                ips[vlan] = f"{octetos[0]}.{octetos[1]}.{octetos[2]}."+str(72+i)
                
            vlan29 = request.form['ip_vlan29'].split('.')
            ips['ip_vlan29'] = '.'.join(vlan29)
            ips['ip_pc_admicion'] = ips['ip_vlan24'].rsplit('.',1)[0]+'.128'
            ips['ip_lms'] = ips['ip_vlan25'].rsplit('.',1)[0]+'.35'
            ips['ip_pc_disp'] = ips['ip_vlan25'].rsplit('.',1)[0]+'.36'
            ips['ip_caj'] = ips['ip_vlan29'].rsplit('.',1)[0]+'.140'

        # Renderizar plantillas correspondientes
        templates = {
            0: 'plantillas/huawei_sw.html',
            1: 'plantillas/forti_switch.html',
            2: 'plantillas/legacy_huawei_sw.html',
            3: 'plantillas/legacy_cisco_sw.html'
        }
        context = {
            'ips': ips,
            'hostname': hostname,
            'location': location,
            'equipo': equipo,
            'pass_n2comms': PASS_N2COMMS,
            'template': True
        }
        
        if equipo in (2,3):
            context['ip_red'] = ip_red
            
            
        return render_template(templates[equipo], **context)

    # Manejo de solicitudes GET
    return render_template('plantillas/plantillas.html', 
                           template=False, 
                           equipo=equipo)

# IP-Calc
@app.route("/ipcalc", methods=['GET', 'POST'])
def ipcalc():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    resultado = ''
    if request.method == 'POST':
        ip_red = request.form['ip_red']
        cidr_sn= 0 if request.form['cidr_sn'] == '' else int(request.form['cidr_sn'])
        cdir = int(ip_red.split('/')[1]) if len(ip_red.split('/'))>1 else 32
        cidr_sn= int(cidr_sn) if int(cidr_sn) >= cdir else 0
        ip_red = ip_red if cdir > 0 else 32
        resultado = IpCalc(ip_red,cidr_sn)
        #print(resultado)
    
    return render_template('form_ipcalc.html', resultado = resultado)


# Auditoria
@app.route("/auditoria_upload", methods=['POST', 'GET'])
def auditoria_upload():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    if request.method == 'POST':
        if "config_file" not in request.files:
            return "No se subió ningún archivo", 400

        file = request.files["config_file"]

        if file.filename == "":
            return "Archivo no seleccionado", 400

        if file and file.filename.endswith(".conf"):
            version = request.form['version']
            filepath = os.path.join(app.config["UPLOAD_CONFS"], file.filename)
            file.save(filepath)
            print(f"Archivo {file.filename} subido con éxito y listo para analizar.")
            return redirect("/auditoria_fw/"+file.filename+"/"+version)
    else:
        return render_template('form_auditoria.html')

@app.route("/auditoria_fw/<archivo_conf>/<ver>")
def auditoria_fw(archivo_conf, ver):
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    
    archivo = os.path.join(app.config["UPLOAD_CONFS"], archivo_conf)
    dashboard_items, datos_archivo, total = res_auditoria(archivo)
    datos_archivo['ver_nueva'] = ver
    
    # Deberiamos guardar las 3 variables en la BBDD

    return render_template('ficha_auditoria_fw.html', dashboard_items = dashboard_items, datos_archivo = datos_archivo, puntaje_total = total)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0')#, port=8080)

