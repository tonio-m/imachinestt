# Kafka/Clickhouse/Python Challenge

This is my solution to the intuition machines challenge.

```
|-- README.md
|-- app (API code, tests, dockerfile)
|-- deployments (k8s deployments for all resources)
`-- utils (small scripts)
```

### Requirements:
- [X] POST Event endpoint

  ```sh
  curl -X POST localhost:8000/v1/events \
  -d '{ "site_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "type": "serve", "correlation_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "time": "2001-01-01T05:55:07"}' \
  -H 'Content-Type: application/json'
  ```

- [X] GET Report endpoint

  ```
  curl 'http://localhost:8000/v1/report' -H 'Content-Type: application/json'
  ```

### Bonus Points:
- [X] Schema validation

  I'm using `pydantic` to validate the request/response schemas on the tests.
  Also using a schema to validate the body of the `POST /v1/event` endpoint.

- [X] Query filters

  `GET /v1/report` has an optional querystring param called site_id that accepts arrays.
  e.g.: `localhost:8000/V1/report?site_id=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa&site_id=bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb`

- [X] Async support 

  All app functions are `async def` coroutines, using `await` to wait for the coroutines 

- [X] Api versioning 

  Using a library called `fastapi-versioning` for versioning under `/v1` and `/latest` prefixes

- [ ] Clickhouse migrations


## Overview

The task is to build the webserver, which accepts incoming captcha events in json format, puts them to clickhouse using kafka and then serves aggregated statistics. 

## Scalability

Although the Kafka deployment is single node, there is one with high availability provided by Confluent that can be used.

The API pod can be put easily on a k8s ReplicaSet.

On clickhouse, I didn't configure shards, but it can be done editing the xml config file and creating a StatefulSet defining many pods. 
Making a helm chart for clickhouse would help with this.

Making POST /v1/event receive batches of events, or stream events through websocket would also improve performance.

## Technical Debt

There are some things that should be improved in a production deployment:

- Clickhouse has no user authentication.
- All deployments are single node, although easily scalable.
- Kafka has no SSL configured for certificate authentication and for in transit encryption.
- I didn't configure any ingress on k8s for the services

## Deployment
```sh
# create k8s cluster on AWS
eksctl create cluster -f ./deployments/cluster/eks.yaml
aws eks update-kubeconfig --name imachines-tt

# deploy clickhouse
kubectl create namespace clickhouse
kubens clickhouse
kubectl apply -f ./deployments/clickhouse/deployment.yaml

# deploy kafka
kubectl create namespace confluent
kubens confluent
helm repo add confluentinc https://packages.confluent.io/helm
helm repo update
helm upgrade --install confluent-operator confluentinc/confluent-for-kubernetes
kubectl apply -f ./deployments/kafka/confluent-platform-singlenode.yaml

# build API container
docker login
cd app/
docker build . -t mrmtonio/captcha-api:latest
docker push mrmtonio/captcha-api:latest

# deploy API
kubectl create namespace captcha-api
kubens captcha-api
cd ..
kubectl apply -f ./deployments/app/deployment.yaml
```

## Setup
```sh
# port forward services to localhost
kubectl port-forward -n confluent service/controlcenter 9021:9021 &
kubectl port-forward -n clickhouse service/myclickhouse 8123:8123 &
kubectl port-forward -n captcha-api service/captcha-api 8000:8000 &

## Create a Kafka Topic
open http://localhost:9021
# Home > Cluster > Topics > Add Topic
# create a topic named `captcha`
# Topics > captcha > Schema > Set a Schema > JSON Schema
# paste the contents of the file ./utils/schema.json

## Create Kafka table on Clickhouse
# use the command below to go on the clickhouse UI
# run all the commands on ./utils/create_table.sql

#############################
```
## Testing
```sh
# Now you can go ahead and test the API

cd app/
export API_URL='http://localhost:8000/v1/'
pytest tests

# curl commands that might be useful
curl localhost:8000/v1/

# get a report
curl 'http://localhost:8000/v1/report?site_id=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa' -H 'Content-Type: application/json'

# send a captcha event
curl -X POST localhost:8000/v1/event -d $json -H 'Content-Type: application/json'

# send many captcha events from a json file
while read -r $json
do
  curl -X POST localhost:8000/v1/event -d $json -H 'Content-Type: application/json'
done < data.ndjson

:)
```
