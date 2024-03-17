
docker_compose_path="./dev-database/docker-compose.yml"


if [ "$1" = "--remove" ]; then
  echo "Removing dev. database, UI and data."
  read -p "Are you sure [Yy]? " response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        docker-compose -f $docker_compose_path down -v
    else
        echo "Exiting..."
    fi
else
    docker-compose -f $docker_compose_path up
fi