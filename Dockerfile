FROM python:3.10

RUN pip install -U pip setuptools wheel
RUN pip install pdm

COPY pyproject.toml pdm.lock /project/
COPY src/ /project/src

WORKDIR /project

RUN pdm sync --no-editable

ENV APP_URL="http://127.0.0.1:5000"
ENV APP_MAX_CONTENT_LENGTH="3000"

EXPOSE 5000

CMD ["pdm", "run", "app"]