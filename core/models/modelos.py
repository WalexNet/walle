from core import db
from datetime import datetime

class Equipo(db.Model):
    __tablename__ = 'Equipos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip = db.Column(db.String(15))
    nombre = db.Column(db.String(50))
    mac = db.Column(db.String(50))
    n_serie = db.Column(db.String(50))
    router = db.Column(db.String(50))
    port_sw_aps = db.Column(db.String(50))
    cattools = db.Column(db.String(10))
    tacacs = db.Column(db.Boolean)
    eliminar_loopback_telefonica = db.Column(db.Boolean)
    snmp_v3 = db.Column(db.Boolean)
    check_mk = db.Column(db.Boolean)
    eliminar_usr_locales = db.Column(db.Boolean)
    crear_usr_local = db.Column(db.Boolean)
    ip_syslog = db.Column(db.Boolean)
    sin_banner = db.Column(db.Boolean)
    ip_cattools = db.Column(db.Boolean)
    eliminar_telnet_http = db.Column(db.Boolean)
    comentarios = db.Column(db.Text)
    stack = db.Column(db.Boolean)
    ios = db.Column(db.String(50))
    rack = db.Column(db.String(50))
    gestion = db.Column(db.String(50))
    sw_to_ap = db.Column(db.String(50))
    tipo_autentication = db.Column(db.String(6))
    # Clave Foranea
    id_estado_cirsa = db.Column(db.Integer, db.ForeignKey('estado_cirsa.id'), nullable=True)
    id_tipo_dispositivo = db.Column(db.Integer, db.ForeignKey('tipo_dispositivo.id'), nullable=True)
    id_fabricante = db.Column(db.Integer, db.ForeignKey('fabricante.id'), nullable=True)
    id_modelo = db.Column(db.Integer, db.ForeignKey('modelo.id'), nullable=True)
    id_tipo_acceso = db.Column(db.Integer, db.ForeignKey('tipo_acceso.id'), nullable=True)
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id'), nullable=True)
    id_sede = db.Column(db.Integer, db.ForeignKey('Sedes.id'))
    # Relaciones
    estado_cirsa = db.relationship('EstadoCirsa', back_populates='equipos', uselist=False, single_parent=True)
    tipo = db.relationship('Tipo', back_populates='equipos', uselist=False, single_parent=True)
    fabricante = db.relationship('Fabricante', back_populates='equipos', uselist=False, single_parent=True)
    modelo = db.relationship('Modelo', back_populates='equipos', uselist=False, single_parent=True)
    tipo_acceso = db.relationship('Acceso', back_populates='equipos', uselist=False, single_parent=True)
    rol = db.relationship('Rol', back_populates='equipos', uselist=False, single_parent=True)
    sede = db.relationship('Sedes', back_populates='equipos', uselist=False, single_parent=True)
    vlanes = db.relationship('RedesVlanes', back_populates='equipos')
    parent = db.relationship('Parents', back_populates='equipos')
    
class RedesVlanes(db.Model):
    __tablename__ = 'redes_vlanes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(50))
    dhcp_serv = db.Column(db.String(15))
    mascara = db.Column(db.String(15))
    red = db.Column(db.String(20))
    vlan_name = db.Column(db.String(50))
    ip_vlan = db.Column(db.String(20))
    cidr = db.Column(db.Integer)
    # Clave Foranea
    id_equipo = db.Column(db.Integer, db.ForeignKey('Equipos.id'))
    # Relaciones
    equipos = db.relationship('Equipo', back_populates='vlanes')

class Sedes(db.Model):
    __tablename__ = 'Sedes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cod_sede_ceco = db.Column(db.String(20))
    cod_sede = db.Column(db.String(30))
    activo = db.Column(db.Boolean)
    sede = db.Column(db.String(100))
    empresa = db.Column(db.String(100))
    cif = db.Column(db.String(20))
    ceco = db.Column(db.String(20))
    direccion = db.Column(db.String(100))
    coor_lat = db.Column(db.String(40))
    coor_long = db.Column(db.String(40))
    # Clave Foranea
    id_circuito = db.Column(db.Integer, db.ForeignKey('circuito.id'))
    id_div = db.Column(db.Integer, db.ForeignKey('division.id'))
    id_prov = db.Column(db.Integer, db.ForeignKey('Provincia.id'))
    id_pob = db.Column(db.Integer, db.ForeignKey('Poblacion.id'))
    id_contacto = db.Column(db.Integer, db.ForeignKey('contacto.id'))
    id_pais = db.Column(db.Integer, db.ForeignKey('pais.id'))
    id_topologia = db.Column(db.Integer, db.ForeignKey('topologia.id'))
    # Relaciones
    circuito = db.relationship('Circuito', back_populates='sede')
    division = db.relationship('Division', back_populates='sede', uselist=False, single_parent=True)
    prov = db.relationship('Provincia', back_populates='sede', uselist=False, single_parent=True)
    pob = db.relationship('Poblacion', back_populates='sede', uselist=False, single_parent=True)
    contacto = db.relationship('Contacto', back_populates='sede', uselist=False, single_parent=True)
    paises = db.relationship('Pais', back_populates='sede')
    equipos = db.relationship('Equipo', back_populates='sede')
    CircuitosDatos = db.relationship('CircuitoDato', back_populates='sede')
    topo = db.relationship('Topologia', back_populates='sede')
    
    def __repr__(self):
        return f'{self.cod_sede} -- {self.sede}'
    
    def __str__(self):
        return self.cod_sede

class EstadoCirsa(db.Model):
    __tablename__ = 'estado_cirsa'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(25))
    # Relación
    equipos = db.relationship('Equipo', back_populates='estado_cirsa')
    
    def __repr__(self):
        return f'{self.id}, {self.nombre}'
    
    def __str__(self):
        return self.nombre

class Tipo(db.Model):
    __tablename__ = 'tipo_dispositivo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(25))
    # Relación
    equipos = db.relationship('Equipo', back_populates='tipo')
    
    def __repr__(self):
        return f'{self.id}, {self.nombre}'
    
    def __str__(self):
        return self.nombre

class Fabricante(db.Model):
    __tablename__ = 'fabricante'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(25))
    device_type = db.Column(db.String(20))
    # Relación
    equipos = db.relationship('Equipo', back_populates='fabricante')
    
    def __repr__(self):
        return f'{self.id}, {self.nombre}'
    
    def __str__(self):
        return self.nombre

class Modelo(db.Model):
    __tablename__ = 'modelo'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    end_of_sale = db.Column(db.Date, nullable=True)
    end_of_sec_support = db.Column(db.Date, nullable=True)
    end_of_hw_support = db.Column(db.Date, nullable=True)
    # Relación
    equipos = db.relationship('Equipo', back_populates='modelo')
    
    def __repr__(self):
        return f'{self.id}, {self.nombre}'
    
    def __str__(self):
        return self.nombre

class Acceso(db.Model):
    __tablename__ = 'tipo_acceso'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(25))
    # Relación
    equipos = db.relationship('Equipo', back_populates='tipo_acceso')
    
    def __repr__(self):
        return f'{self.id}, {self.nombre}'
    
    def __str__(self):
        return self.nombre

class CircuitoDato(db.Model):
    __tablename__ = 'CircuitoDatos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cod_sede = db.Column(db.String(50))
    admin = db.Column(db.String(20))
    tel_router = db.Column(db.String(20))
    vrf = db.Column(db.String(50))
    # Clave Foranea
    id_tipo_circuito = db.Column(db.Integer, db.ForeignKey('tipo_circuito.id'), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id'), nullable=False)
    id_bw = db.Column(db.Integer, db.ForeignKey('ancho_banda.id'), nullable=False)
    id_sede = db.Column(db.Integer, db.ForeignKey('Sedes.id'), nullable=False)
    # Relaciones
    tipo_circuito = db.relationship('TipoCircuito', back_populates='CircuitosDatos', uselist=False, single_parent=True)
    rol = db.relationship('Rol', back_populates='CircuitosDatos', uselist=False, single_parent=True)
    bw = db.relationship('AnchoBanda', back_populates='CircuitosDatos', uselist=False, single_parent=True)
    sede = db.relationship('Sedes', back_populates='CircuitosDatos', uselist=False, single_parent=True)

class TipoCircuito(db.Model):
    __tablename__ = 'tipo_circuito'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(30))
    # Relación
    CircuitosDatos = db.relationship('CircuitoDato', back_populates='tipo_circuito')
    
    def __repr__(self):
        return f'{self.id}, {self.nombre}'
    
    def __str__(self):
        return self.nombre

class Rol(db.Model):
    __tablename__ = 'rol'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(30))
    # Relación
    CircuitosDatos = db.relationship('CircuitoDato', back_populates='rol')
    equipos = db.relationship('Equipo', back_populates='rol')
    
    def __repr__(self):
        return f'{self.id}, {self.nombre}'
    
    def __str__(self):
        return self.nombre

class Pais(db.Model):
    __tablename__ = 'pais'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(30))
    # Relación
    sede = db.relationship('Sedes', back_populates='paises')
    
    def __repr__(self):
        return f'{self.id}, {self.nombre}'
    
    def __str__(self):
        return self.nombre

class AnchoBanda(db.Model):
    __tablename__ = 'ancho_banda'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50))
    # Relación
    CircuitosDatos = db.relationship('CircuitoDato', back_populates='bw')
    
    def __repr__(self):
        return f'{self.id}, {self.nombre}'
    
    def __str__(self):
        return self.nombre

class Poblacion(db.Model):
    __tablename__ = 'Poblacion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100))
    # Relación
    sede = db.relationship('Sedes', back_populates='pob')
    
    def __repr__(self):
        return f'{self.id}, {self.nombre}'
    
    def __str__(self):
        return self.nombre

class Provincia(db.Model):
    __tablename__ = 'Provincia'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50))
    # Relación
    sede = db.relationship('Sedes', back_populates='prov')
    
    def __repr__(self):
        return f'{self.id}, {self.nombre}'
    
    def __str__(self):
        return self.nombre

class Contacto(db.Model):
    __tablename__ = 'contacto'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cod_sede = db.Column(db.String(50))
    responsable_cirsa = db.Column(db.String(100))
    persona_contacto_cirsa = db.Column(db.String(100))
    tel_contacto_cirsa = db.Column(db.String(25))
    persona_contacto_sala = db.Column(db.String(100))
    tel_contacto_sala = db.Column(db.String(25))
    persona_mantenimiento = db.Column(db.String(100))
    tel_persona_mantenimiento = db.Column(db.String(25))
    # Relación
    sede = db.relationship('Sedes', back_populates='contacto', uselist=False, single_parent=True)

class Circuito(db.Model):
    __tablename__ = 'circuito'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50))
    # Relación
    sede = db.relationship('Sedes', back_populates='circuito')
    
    def __repr__(self):
        return f'{self.id}, {self.nombre}'
    
    def __str__(self):
        return self.nombre

class Division(db.Model):
    __tablename__ = 'division'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50))
    # Relación
    sede = db.relationship('Sedes', back_populates='division')
    
    def __repr__(self):
        return f'{self.id}, {self.nombre}'
    
    def __str__(self):
        return self.nombre

class Topologia(db.Model):
    __tablename__ = 'topologia'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    # Relación
    sede = db.relationship('Sedes', back_populates='topo')
    
    def __repr__(self):
        return f'{self.id}, {self.nombre}'
    
    def __str__(self):
        return self.nombre

class Parents(db.Model):
    __tablename__ = 'parents'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_parent = db.Column(db.String(25))
    # Clave Foranea
    id_host = db.Column(db.Integer, db.ForeignKey('Equipos.id'))
    # Relaciones
    equipos = db.relationship('Equipo', back_populates='parent')
    
    def __repr__(self):
        return f'{self.id} - {self.host_parent}'
    
    def __str__(self):
        return self.host_parent
    
# Esta es la vista
class Todo(db.Model):
    __tablename__ = 'todo'
    
    id = db.Column(db.Integer, primary_key=True)
    id_sede = db.Column(db.Integer)
    ip = db.Column(db.String)
    hostname = db.Column(db.String)
    mac = db.Column(db.String)
    n_serie = db.Column(db.String)
    router = db.Column(db.String)
    port_sw_aps = db.Column(db.String)
    dispositivo = db.Column(db.String)
    fabricante = db.Column(db.String)
    modelo = db.Column(db.String)
    acceso = db.Column(db.String)
    rol = db.Column(db.String)
    estado = db.Column(db.String)
    sede = db.Column(db.String)
    nom_sede = db.Column(db.String)
    emp_sede = db.Column(db.String)
    direccion = db.Column(db.String)
    responsable_cirsa = db.Column(db.String)
    persona_contacto_cirsa = db.Column(db.String)
    tel_contacto_cirsa = db.Column(db.String)
    persona_contacto_sala = db.Column(db.String)
    tel_contacto_sala = db.Column(db.String)
    comentarios = db.Column(db.String)

# Esta tabla no se usa, es equivalente a division
class TipoSede(db.Model):
    __tablename__ = 'tipo_sede'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_sede = db.Column(db.String(4))
    nombre = db.Column(db.String(50))


# Eschema wiki_walle
class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'wiki_walle'}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    post = db.relationship('Post', back_populates= 'user')
    comments = db.relationship("Comment", back_populates='user')
    
class Data(db.Model):
    __tablename__ = 'data'
    __table_args__ = {'schema': 'wiki_walle'}
    id = db.Column(db.Integer, primary_key=True)
    us_name = db.Column(db.String(50), nullable=False)
    ps_name = db.Column(db.String(50), nullable=False, unique=True)
    
    def __repr__(self):
        """Método de representación útil para debugging."""
        return f"<Data(id={self.id}, us_name='{self.us_name}', ps_name='{self.ps_name}')>"
    

class Post(db.Model):
    __tablename__ = 'posts'
    __table_args__ = {'schema': 'wiki_walle'}
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('wiki_walle.users.id'))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", back_populates='post')
    comments = db.relationship("Comment", back_populates='post')

class Comment(db.Model):
    __tablename__ = 'comments'
    __table_args__ = {'schema': 'wiki_walle'}
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('wiki_walle.posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('wiki_walle.users.id'))
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    post = db.relationship("Post", back_populates="comments")
    user = db.relationship("User", back_populates="comments")

# Tareas de tecnicos
class Tecnico(db.Model):
    __tablename__ = 'tecnicos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True) # Opcional, para notificaciones
    activo = db.Column(db.Boolean, default=True)     # Por si alguien está de vacaciones
    orden_rotacion = db.Column(db.Integer, nullable=False, default=0)
    de_vacaciones = db.Column(db.Boolean, default=False)
    no_disponible = db.Column(db.Boolean, default=False)
    
    # Relación para acceder a las tareas de este técnico fácilmente
    tareas = db.relationship('Tarea', backref='tecnico', lazy=True)

    def __repr__(self):
        return f'<Tecnico {self.nombre}>'

class Tarea(db.Model):
    __tablename__ = 'tareas'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    prioridad = db.Column(db.String(20), default='Media') # Baja, Media, Alta, Critica
    estado = db.Column(db.String(20), default='Pendiente') # Pendiente, En Progreso, Cerrada
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Clave foránea que vincula la tarea al técnico
    tecnico_id = db.Column(db.Integer, db.ForeignKey('tecnicos.id'), nullable=False)

    def __repr__(self):
        return f'<Tarea {self.titulo}>'

# ************************

def all_paginated(tabla, page=1, per_page=20):
    return tabla.query.paginate(page=page, per_page=per_page, error_out=False).items