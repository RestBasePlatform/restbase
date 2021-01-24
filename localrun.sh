docker network create -d bridge --subnet 192.168.0.0/24 --gateway 192.168.0.1 restbase
yes | docker-compose rm postgres
docker-compose up --build --force-recreate --no-deps --abort-on-container-exit
