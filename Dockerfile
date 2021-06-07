FROM restbase/base_image:fastapi

COPY . /app
WORKDIR /app/source

EXPOSE 54541

ENV internal_db_ip=10.5.0.5
ENV internal_db_user=postgres
ENV internal_db_password=password
ENV internal_db_database_name=postgres
ENV internal_db_port=5432

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "54541"]
