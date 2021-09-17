# Set up MLflow Server

> You can find some sample files for this section in `mlflow_on_kubernetes/manifests/mlflow_server`.

## What is MLflow

> MLflow is an open source platform to manage the ML lifecycle, including experimentation, 
  reproducibility, deployment, and a central model registry. MLflow currently offers four components:
>  - MLflow Tracking: record and query experiments (code, data, config, and results).
>  - MLflow Projects: package data science code in a format to reproduce runs on any platform.
>  - MLflow Models: deploy machine learning models in diverse serving environments.
>  - Model Registry: store, annotate, discover, and manage models in a central repository.

In this sample deployment we are going to use MLflow Tracking and MLflow Registry to manage
experiments and models and MLflow Projects to launch experiment runs.

## Dockerfile

MLflow does not have an official Docker image. We provide the sample image 
`sbugallo/mlflow-server:1.20.2` and the Dockerfiles used (manifests/mlflow_server/Dockerfile).

## Deployment

This app does not have a state (it uses stateful apps like MinIO and PostgreSQL, though) so we
are going to deploy it using a Deployment controller.

Notice that we are using MinIO's and PostgreSQL's secrets and service to configure our app.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mlflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mlflow
  template:
    metadata:
      labels:
        app: mlflow
    spec:
      containers:
      - name: mlflow
        image: sbugallo/mlflow-server:1.20.2
        imagePullPolicy: Always
        args:
        - --host=0.0.0.0
        - --port=5000
        - --backend-store-uri=postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@postgres-service/$(POSTGRES_DB)
        - --default-artifact-root=s3://mlflow/
        - --workers=2
        env:
        - name: MLFLOW_S3_ENDPOINT_URL
          value: http://minio-service:9000/
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: minio-conf
              key: root_user
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: minio-conf
              key: root_password
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_PASSWORD
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_DB
        ports:
        - name: http
          containerPort: 5000
          protocol: TCP
```

## Service

Lastly, in order to give external access to MLflow, we are going to create a NodePort. Remember
that you are deploying Kubernetes on a container so you have to use the container's IP to access
MLflow. You can get the IP with `minikube ip`.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mlflow-service
spec:
  type: NodePort
  ports:
    - port: 5000
      targetPort: 5000
      nodePort: 30500
      protocol: TCP
      name: http
  selector:
    app: mlflow
```

## Navigation

- Previous: [Set up PostgreSQL](setup_postgres.md)
- Next: [Run MLflow project](run_mlflow_project.md)