FROM python:3.10

RUN pip install -U pip setuptools wheel
RUN pip install pdm

COPY pyproject.toml pdm.lock data.db /project/
COPY src/ /project/src

WORKDIR /project

RUN pdm sync --no-editable

ENV APP_DB_DRIVER="sqlite"
ENV APP_DB_HOST=""
ENV APP_DB_USER=""
ENV APP_DB_PASSWORD=""
ENV APP_DB_DATABASE="data.db"

EXPOSE 1234

CMD ["pdm", "run", "app"]