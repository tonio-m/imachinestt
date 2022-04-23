# Create an EKS Cluster
```sh
eksctl create cluster -f deployments/cluster/eks.yaml
aws eks update-kubeconfig --name imachines-tt

# (optional) install k8s dashboard and See UI
kubens kubernetes-dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml
kubectl port-forward -n kubernetes-dashboard service/kubernetes-dashboard 8080:443 > /dev/null 2>&1 &
aws eks get-token --cluster-name imachines-tt | jq -r '.status.token'
```

# Install Clickhouse
```sh
kubens clickhouse
kubectl apply -f deployments/clickhouse/deployment.yaml

# see UI
kubectl port-forward service/myclickhouse 8123:8123 > /dev/null 2>&1 &
open http://localhost:8123
```

# Install Kafka
```sh
kubens confluent

# install confluent platform
helm repo add confluentinc https://packages.confluent.io/helm
helm upgrade --install confluent-operator confluentinc/confluent-for-kubernetes
kubectl apply -f deployments/kafka/confluent-platform-singlenode.yaml

# see UI
kubectl port-forward service/controlcenter 9021:9021 > /dev/null 2>&1 &
open http://localhost:9021
```

# load data on kafka
```sh
# Go on the ControlCenter UI
kubectl port-forward service/controlcenter 9021:9021 > /dev/null 2>&1 &
open http://localhost:9021
# create a topic named `captcha`
# go inside the topic, on `schema`, paste the contents of utils/schema.json

# generate data
python utils/generate_data.py data.ndjson

# copy data to the kafka pod and load it on the topic 
kubectl cp data.ndjson kafka-0:/tmp/
kubectl exec -it kafka-0 -- bash
cd /tmp/
kafka-console-producer \
  --bootstrap-server localhost:9071 \
  --topic captcha < data.ndjson
```

# Read data on clickhouse
```
# go on clickhouse UI
kubens clickhouse
kubectl port-forward service/myclickhouse 8123:8123 > /dev/null 2>&1 &
open http://localhost:8123
```

```sql
-- create table
CREATE TABLE captcha
(
    site_id UUID,
    time DateTime,
    correlation_id UUID,
    event_type Enum('serve' = 1, 'solve' = 2)
) ENGINE = MergeTree ORDER BY (event_type, correlation_id, time)

-- create kafka streaming table
CREATE TABLE default.captcha_queue
(
    site_id UUID,
    time DateTime,
    correlation_id UUID,
    event_type Enum('serve' = 1, 'solve' = 2)
)
   ENGINE = Kafka('kafka.confluent.svc.cluster.local:9071', 'captcha', 'clickhouse',
            'JSONEachRow') settings kafka_thread_per_consumer = 0, kafka_num_consumers = 1;

-- create materialized view to table
CREATE MATERIALIZED VIEW default.captcha_mv TO default.captcha AS
SELECT *
FROM default.captcha_queue;

-- test
SELECT count() FROM default.captcha;
```

