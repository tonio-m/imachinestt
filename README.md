# Create an EKS Cluster
```sh
eksctl create cluster -f cluster/eks.yaml
aws eks update-kubeconfig --name imachines-tt

# (optional) install k8s dashboard and See UI
kubens kubernetes-dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml
kubectl port-forward -n kubernetes-dashboard service/kubernetes-dashboard 8080:443 > /dev/null 2>&1 &
aws eks get-token --cluster-name imachines-tt | jq -r '.status.token'
```

# Install Clickhouse
```
kubens clickhouse
kubectl apply -f clickhouse/deployment.yaml

# see UI
kubectl port-forward service/myclickhouse 8123:8123 > /dev/null 2>&1 &
open http://localhost:8123
```

# Install Kafka
```
kubens confluent

# install confluent platform
helm repo add confluentinc https://packages.confluent.io/helm
helm upgrade --install confluent-operator confluentinc/confluent-for-kubernetes
kubectl apply -f ./kafka/confluent-platform-singlenode.yaml

# see UI
kubectl port-forward service/controlcenter 9021:9021 > /dev/null 2>&1 &
open http://localhost:9021
```

# load data on kafka
```
python generate_data.py data.ndjson
kubectl cp data.ndjson kafka-0:/tmp/
kubectl exec -it kafka-0 -- bash
kafka-console-producer \
  --bootstrap-server localhost:9071 \
  --topic github < data.ndjson
```

# read kafka data on clickhouse
```
CREATE TABLE default.github_queue
(
    file_time DateTime,
    event_type Enum('CommitCommentEvent' = 1, 'CreateEvent' = 2, 'DeleteEvent' = 3, 'ForkEvent' = 4, 'GollumEvent' = 5, 'IssueCommentEvent' = 6, 'IssuesEvent' = 7, 'MemberEvent' = 8, 'PublicEvent' = 9, 'PullRequestEvent' = 10, 'PullRequestReviewCommentEvent' = 11, 'PushEvent' = 12, 'ReleaseEvent' = 13, 'SponsorshipEvent' = 14, 'WatchEvent' = 15, 'GistEvent' = 16, 'FollowEvent' = 17, 'DownloadEvent' = 18, 'PullRequestReviewEvent' = 19, 'ForkApplyEvent' = 20, 'Event' = 21, 'TeamAddEvent' = 22),
    actor_login LowCardinality(String),
    repo_name LowCardinality(String),
    created_at DateTime,
    updated_at DateTime,
    action Enum('none' = 0, 'created' = 1, 'added' = 2, 'edited' = 3, 'deleted' = 4, 'opened' = 5, 'closed' = 6, 'reopened' = 7, 'assigned' = 8, 'unassigned' = 9, 'labeled' = 10, 'unlabeled' = 11, 'review_requested' = 12, 'review_request_removed' = 13, 'synchronize' = 14, 'started' = 15, 'published' = 16, 'update' = 17, 'create' = 18, 'fork' = 19, 'merged' = 20),
    comment_id UInt64,
    path String,
    ref LowCardinality(String),
    ref_type Enum('none' = 0, 'branch' = 1, 'tag' = 2, 'repository' = 3, 'unknown' = 4),
    creator_user_login LowCardinality(String),
    number UInt32,
    title String,
    labels Array(LowCardinality(String)),
    state Enum('none' = 0, 'open' = 1, 'closed' = 2),
    assignee LowCardinality(String),
    assignees Array(LowCardinality(String)),
    closed_at DateTime,
    merged_at DateTime,
    merge_commit_sha String,
    requested_reviewers Array(LowCardinality(String)),
    merged_by LowCardinality(String),
    review_comments UInt32,
    member_login LowCardinality(String)
)
   ENGINE = Kafka('kafka-0-internal.confluent.svc.cluster.local:9071', 'github', 'clickhouse',
            'JSONEachRow') settings kafka_thread_per_consumer = 0, kafka_num_consumers = 1;
```



# create topic and schema on the controlcenter
# Go on topics > +add topic
# Then click on the topic you just created > Schema > JSON-Schema and paste the json below:
# {"$schema":"http://json-schema.org/schema#","properties":{"action":{"type":"string"},"actor_login":{"type":"string"},"assignee":{"type":"string"},"closed_at":{"type":"string"},"comment_id":{"type":"string"},"created_at":{"type":"string"},"creator_user_login":{"type":"string"},"event_type":{"type":"string"},"file_time":{"type":"string"},"member_login":{"type":"string"},"merge_commit_sha":{"type":"string"},"merged_at":{"type":"string"},"merged_by":{"type":"string"},"number":{"type":"integer"},"path":{"type":"string"},"ref":{"type":"string"},"ref_type":{"type":"string"},"repo_name":{"type":"string"},"review_comments":{"type":"integer"},"state":{"type":"string"},"title":{"type":"string"},"updated_at":{"type":"string"}},"required":["action","actor_login","assignee","closed_at","comment_id","created_at","creator_user_login","event_type","file_time","member_login","merge_commit_sha","merged_at","merged_by","number","path","ref","ref_type","repo_name","review_comments","state","title","updated_at"],"title":"auto-generated - github","type":"object"}

# install jdbc driver
# add the line below on the spec.containers.command section
confluent-hub install confluentinc/kafka-connect-jdbc:latest --no-prompt &&   
# like this:
# spec:
#   affinity: {}
#   containers:
#   - args:
#     - /mnt/config/connect/bin/run
#     command:
#     - confluent-hub install confluentinc/kafka-connect-jdbc:latest --no-prompt &&   
#     - /bin/sh
#     - -xc

# scale the connect statefulset to apply changes
k scale sts connect --replicas=0
k scale sts connect --replicas=1
confluent-hub install confluentinc/kafka-connect-jdbc:latest --no-prompt 
wget https://github.com/ClickHouse/clickhouse-jdbc/releases/download/v0.3.2-patch8/clickhouse-jdbc-0.3.2-patch8-shaded.jar

curl -s -H "Content-Type: application/json" -X POST -d '
{
  "name": "clickhouse-jdbc-sink",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
    "tasks.max": "1",
    "topics": "github",
    "connection.url": "jdbc:clickhouse://myclickhouse.default.svc.cluster.local:8123/default",
    "auto.create": "true",
    "value.converter": "io.confluent.connect.json.JsonSchemaConverter",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "schema.registry.url": "http://schemaregistry.confluent.svc.cluster.local:8081"
  }
}
' http://localhost:8083/connectors/ | jq .
curl -X DELETE http://localhost:8083/connectors/clickhouse-jdbc-sink | jq .
```

# sample producer






