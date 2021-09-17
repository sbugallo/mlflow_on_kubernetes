# Set up PostgreSQL

> You can find some sample files for this section in `mlflow_on_kubernetes/manifests/postgres`.

## What is PostgreSQL?

> PostgreSQL is a powerful, open source object-relational database system that uses and extends the 
  SQL language combined with many features that safely store and scale the most complicated data 
  workloads.

We are going to use PostgreSQL as our backend store where experiments, params and metrics will be
saved to.

## ConfigMap

Non sensitive variables will be injected using a ConfigMap. In this case, the only value we are 
going to set is where the database is going to be created inside the pod.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config
  labels:
    app: postgres
data:
  PGDATA: /var/lib/postgresql/mlflow/data
```

## PersistentVolume

Same as with MinIO, we have to create a persistent volume and a claim to store our data. Note that 
we are going to use `/mnt/data/postgres`.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: postgres-pv
  labels:
    type: local
spec:
  storageClassName: postgres
  capacity:
    storage: 100Mi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: "/mnt/data/postgres"
```

## Secrets

The username, password and database are going to be injected through secrets. Remember that values
should be encoded in base 64.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
data:
  POSTGRES_USER: <POSTGRESS USERNAME>
  POSTGRES_PASSWORD: <POSTGRESS PASSWORD>
  POSTGRES_DB: <POSTGRESS DB NAME>
```

## StatefulSet

Same as with MinIO, PostgreSQL is a stateful app so we are going to deploy it using a StatefulSet
controller.

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  labels:
    app: postgres
spec:
  selector:
    matchLabels:
      app: postgres
  serviceName: "postgres-service"
  replicas: 1
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:11
        ports:
        - containerPort: 5432
          protocol: TCP
        envFrom:
        - configMapRef:
            name: postgres-config
        - secretRef:
            name: postgres-secret
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
        volumeMounts:
        - name: pvc
          mountPath: /var/lib/postgresql/mlflow
  volumeClaimTemplates:
  - metadata:
      name: pvc
    spec:
      storageClassName: postgres
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 100Mi
```

## Service

In order to allow MLflow access Postgress, we have to define a ClusterIP service. 

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  labels:
    svc: postgres-service
spec:
  type: ClusterIP
  ports:
  - port: 5432
    targetPort: 5432
    protocol: TCP
  selector:
    app: postgres
```

## Navigation

- Previous: [Set up MinIO](setup_minio.md)
- Next: [Set up MLflow server](setup_mlflow_server.md)
