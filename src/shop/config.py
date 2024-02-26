import environ


@environ.config
class AppConfig:
    url = environ.var(default="http://127.0.0.1:5000")
    max_content_length = environ.var(default=1 * 1024 * 1024)


print()
