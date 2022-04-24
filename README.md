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

## Setup

```sh
# create k8s cluster on AWS
eksctl create cluster -f ./deployments/cluster/eks.yaml
aws eks update-kubeconfig --name imachines-tt

# deploy clickhouse
kubens clickhouse
kubectl apply -f ./deployments/clickhouse/deployment.yaml

# deploy kafka
kubens confluent
helm repo add confluentinc https://packages.confluent.io/helm
helm repo update
helm upgrade --install confluent-operator confluentinc/confluent-for-kubernetes
kubectl apply -f ./deployments/kafka/confluent-platform-singlenode.yaml

# deploy API
# (I already built and pushed the image)
kubens captcha-api
kubectl apply -f ./deployments/app/deployment.yaml

####### MANUAL STEPS #########
## Create Kafka Topic
# use the command below to go on the kafka control center
kubectl port-forward -n confluent service/controlcenter 9021:9021
# create a topic named `captcha`
# after creating go on `schema`, select Jsonschema and paste the contents of ./utils/schema.json

## Create Kafka table on Clickhouse
# use the command below to go on the clickhouse UI
kubectl port-forward -n clickhouse service/myclickhouse 8123:8123
# run all the commands on ./utils/create_table.sql

#############################
# Now you can go ahead and test the API
kubectl port-forward -n captcha-api service/captcha-api 8000:8000

curl localhost:8000/v1/

:)
```
