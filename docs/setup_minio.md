# Set up MinIO

> You can find some sample files for this section in `mlflow_on_kubernetes/manifests/minio`.

## What is MinIO?

> MinIO offers high-performance, S3 compatible object storage. Native to Kubernetes, MinIO is the 
  only object storage suite available on every public cloud, every Kubernetes distribution, the 
  private cloud and the edge. MinIO is software-defined and is 100% open source under GNU AGPL v3. 

We are going to use MinIO as our artifact store where models, plots and logs are going to be saved
to.

## PersistentVolume

The very first thing we are going to deploy is a persistent volume to store our data. Since this is
a dummy deployment, we are just going to use 100MiB as storage.

Note that the volume points to `/mnt/data/minio`.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: minio-pv
  labels:
    type: local
spec:
  storageClassName: minio
  capacity:
    storage: 100Mi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: "/mnt/data/minio"
```

## Secrets

To set up our credentials, we are going to use a secret. Change \<MINIO USERNAME\> and 
\<MINIO PASSWORD\> to any value you like encoded in based64. 

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: minio-conf
data:
  root_user: <MINIO USERNAME>
  root_password: <MINIO PASSWORD>
```

## StatefulSet

Once the secret, the persistent volume and the persistent volume clain are deployed, we can deploy 
MinIO. Since it needs using a StatefulSet controller instead of a Deployment because it is more
suited for stateful apps.

We are going to mount the volume inside the pod's `/data` folder. We also have to load the 
credentials defined in the secret.

Finally, we tell MinIO to serve `/data`.

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: minio
  labels:
    app: minio
spec:
  selector:
    matchLabels:
      app: minio
  serviceName: "minio-service"
  replicas: 1
  template:
    metadata:
      labels:
        app: minio
    spec:
      containers:
      - name: minio
        image: minio/minio:latest
        args:
        - server
        - /data
        volumeMounts:
        - name: pvc
          mountPath: '/data'
        env:
        - name: MINIO_ROOT_USER
          valueFrom:
            secretKeyRef:
              name: minio-conf
              key: root_user
        - name: MINIO_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: minio-conf
              key: root_password
        ports:
        - containerPort: 9000
  volumeClaimTemplates:
  - metadata:
      name: pvc
    spec:
      storageClassName: minio
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 100Mi
```

## Service

In order to connect MinIO with other pods in the cluster, we have to define a service. Since
it is only going to be accessed by pods and not externally, we are going to use a ClusterIP service.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: minio-service
spec:
  type: ClusterIP
  ports:
  - port: 9000
    targetPort: 9000
    protocol: TCP
  selector:
    app: minio
```

## Navigation

- Previous: [Set up cluster](setup_cluster.md)
- Next: [Set up PostgreSQL](setup_postgres.md)
