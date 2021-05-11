FROM restbase/base_image

COPY . /app
WORKDIR /app
# Copy postgres config
COPY conf/pg_hba.conf /etc/postgresql/9.3/main/pg_hba.conf
#USER root

EXPOSE 54541
EXPOSE 5432

ENV internal_db_ip=localhost
ENV internal_db_user=postgres
ENV internal_db_password=password
ENV internal_db_database_name=postgres

ENTRYPOINT ["sh", "./startup.sh"]
