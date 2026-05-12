class Config:
    SECRET_KEY = 'champs_secret_key'
 
    SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://root:@localhost/champs_db'
        '?charset=utf8mb4'
    )
 
    SQLALCHEMY_ENGINE_OPTIONS = {
        # Tells MariaDB/MySQL to allow zero dates without raising an error.
        # PyMySQL will then return None for 0000-00-00 values.
        'connect_args': {
            'init_command': "SET sql_mode='ALLOW_INVALID_DATES'"
        }
    }
 
    SQLALCHEMY_TRACK_MODIFICATIONS = False