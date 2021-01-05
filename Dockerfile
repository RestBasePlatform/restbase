FROM python:3.8
RUN apt-get update -y
RUN apt-get install -y postgresql-client
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . /app
WORKDIR /app


ENTRYPOINT bash postgres_waiter.sh postgres_internal && cd alembic && alembic upgrade head && cd ../ &&  pytest -v
