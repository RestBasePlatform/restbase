yes | docker-compose rm postgres_test_base
yes | docker-compose rm api
yes | docker-compose rm postgres
docker-compose up --build --force-recreate --no-deps --abort-on-container-exit
yes | docker-compose rm postgres_test_base
yes | docker-compose rm api
yes | docker-compose rm postgres
