# deleting all statefulsets
kubectl delete statefulsets.apps ml-train
kubectl delete statefulsets.apps ml-api
kubectl delete statefulsets.apps ml-hyper

# deleting all services
kubectl delete service ml-api
kubectl delete service ml-train
kubectl delete service ml-hyper

# deleting all pods
kubectl delete pods -l app=ml-api
kubectl delete pods -l app=ml-train
kubectl delete pods -l app=ml-hyper

# re-apply everything
kubectl apply -f ./ml.yaml
kubectl apply -f ./ml-hyper.yaml

# watching pods
kubectl get pods -w
