import environ


@environ.config
class AppConfig:
    url = environ.var(default="http://127.0.0.1:5000")


print()