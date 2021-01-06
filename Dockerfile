FROM python:3.8
RUN apt-get update -y
RUN apt-get install -y postgresql-client
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . /app
WORKDIR /app


ENTRYPOINT bash postgres_waiter.sh postgres_internal && bash postgres_waiter.sh postgres_test_base &&  cd alembic && alembic upgrade head && cd ../ && cd tests && python3 db_preparation.py && cd ../ &&  pytest -v
