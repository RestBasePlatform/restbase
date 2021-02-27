FROM restbase/base_image

COPY requirements.txt .

RUN python3.6 -m venv ./venv
RUN /bin/sh ./venv/bin/activate
RUN pip3 install -r requirements.txt

COPY . /app
WORKDIR /app
# Copy postgres config
COPY conf/pg_hba.conf /etc/postgresql/9.3/main/pg_hba.conf
#USER root
EXPOSE 54541
EXPOSE 5432
ENTRYPOINT ["sh", "./startup.sh"]
