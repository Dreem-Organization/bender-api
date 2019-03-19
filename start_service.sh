PORT=8000

docker build -t bender .

docker rm bender-database
docker run -d --name bender-database -e POSTGRES_USER=dev -e POSTGRES_PASSWORD=dev -v ~/docker_data/postgresql:/var/lib/postgresql/data postgres:9.6
docker run -it --rm --env DJANGO_SETTINGS_MODULE="bender_service.settings.development" --link bender-database:bender-database -v "$(pwd)/bender_service:/usr/src/app" -p $PORT:8000 bender bash /run_development.sh
