FROM restbase/base_image:fastapi

COPY . /app
WORKDIR /app/source

EXPOSE 54541
EXPOSE 5432

ENV internal_db_ip=postgres
ENV internal_db_user=postgres
ENV internal_db_password=password
ENV internal_db_database_name=postgres

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "54541"]
