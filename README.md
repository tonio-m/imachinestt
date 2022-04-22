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
