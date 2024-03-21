import environ


@environ.config
class AppConfig:
    db_driver = environ.var(default="postgresql")
    db_host = environ.var(default="localhost")
    db_user = environ.var(default="postgres")
    db_password = environ.var(default="test1234")
    db_database = environ.var(default="shop")
