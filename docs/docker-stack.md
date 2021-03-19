# Local development with Docker-swarm

## Building metax-image (optional)

After installing [Docker prerequisites](docker-prerequisites.md), build the metax-web docker image with the following command:

`docker build -t fairdata-docker.artifactory.ci.csc.fi/fairdata-metax-web .`

## Running the stack locally

In the repository root, run

`docker stack deploy -c docker-compose.yml metax-dev`

## Running the stack without predefined docker-configs

`docker stack deploy -c config-swap-stack.yml metax-dev`

## Adding nginx to the stack

`docker stack deploy -c docker-compose.yml -c containers/nginx-docker.yml metax-dev`

## Running Metax management commands

To run  Metax management commands, locate the running metax-dev_metax container and open terminal inside it with:

`docker exec -it <container-name> bash`

## Adding docker-config to the stack

`docker service update --config-add source=metax-web-stable-config,target=/code/metax_api/settings/.env metax-dev_metax`

## Swapping docker-config in the stack

`docker service update --config-rm <docker-config-name> --config-add source=<docker-config-name>,target=/code/metax_api/settings/.env metax-dev_metax`

