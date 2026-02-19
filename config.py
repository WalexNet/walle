class Config:
    DEBUG = True
    TESTING = True

    # Configuracion de la base de datos
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # SQLite
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///../db/inventario_equipos.db'

    # MariaDB
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@localhost:3306'
    
    # PostreSQL Director
    #SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:pgSQL2023@10.16.39.100:5432/marte'

    # PostreSQL Server Cirsa
    SQLALCHEMY_DATABASE_URI = 'postgresql://montual:VvKzUsgWmiBSTFtmCCer@rhmonsql:5432/marte'

    # PostreSQL (Pruebas Local)
    #SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:pgSQL2023@127.0.0.1:5432/marte'

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    SECRET_KEY = 'dev'


