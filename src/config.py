class Config:
    SECRET_KEY = 'secretkey'

class DevelomentConfig(Config):
    DEBUG=True
    MYSQL_HOST = 'localhost' 
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'task_managament_system'

config={
    'develoment':DevelomentConfig
}