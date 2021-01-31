echo "listen_addresses='*'" >> /etc/postgresql/9.3/main/postgresql.conf
/etc/init.d/postgresql restart

cd alembic && alembic upgrade head
cd ../src
python3.6 rest_base.py
