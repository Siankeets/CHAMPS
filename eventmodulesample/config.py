class Config:
    SECRET_KEY = 'champs_secret_key'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/champs_db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False