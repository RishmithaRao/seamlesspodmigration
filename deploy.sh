#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.

# Check if we're in the correct directory
if [ ! -d "project-manager" ] || [ ! -d "addition-container" ] || [ ! -d "mul-div-container" ]; then
    echo "Error: Make sure you're in the seamlessmigration directory and all subdirectories are present."
    exit 1
fi

# Build and push Docker images
echo "Building and pushing Docker images..."
# For project-manager
docker build -t rishmitha88/project-manager:latest -f project-manager/Dockerfile .
docker push rishmitha88/project-manager:latest

# For addition-container
docker build -t rishmitha88/addition-container:latest -f addition-container/Dockerfile .
docker push rishmitha88/addition-container:latest

# For mul-div-container
docker build -t rishmitha88/mul-div-container:latest -f mul-div-container/Dockerfile .
docker push rishmitha88/mul-div-container:latest

# Apply Kubernetes configurations
echo "Applying Kubernetes configurations..."
kubectl apply -f project-service.yaml
kubectl apply -f service-account.yaml
kubectl apply -f project_manager-sa.yaml
kubectl apply -f role-and-binding.yaml
kubectl apply -f rbac.yaml
kubectl apply -f project-configmap.yaml
kubectl apply -f new-pv.yaml
kubectl apply -f new-pvc.yaml

# Run a temporary pod to verify PVC binding
kubectl run temp-pod --image=busybox --restart=Never -it --overrides='
{
  "apiVersion": "v1",
  "kind": "Pod",
  "spec": {
    "containers": [{
      "name": "temp-pod",
      "image": "busybox",
      "volumeMounts": [{
        "mountPath": "/data",
        "name": "project-pvc"
      }],
      "command": ["/bin/sh"]
    }],
    "volumes": [{
      "name": "project-pvc",
      "persistentVolumeClaim": {
        "claimName": "project-pvc"
      }
    }]
  }
}' -- /bin/sh

# Apply remaining Kubernetes configurations
kubectl apply -f project-pod.yaml
kubectl apply -f pod-distruption-budget.yaml
kubectl apply -f network-policy.yaml

echo "Deployment script executed successfully."

