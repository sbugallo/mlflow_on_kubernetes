# Setup your Kubernetes cluster

## Introduction

The very first thing we must do is have our Kubernetes cluster up and running. In order tu achieve 
that, we are going to use 2 tools:

- `minikube`: utility used to deploy a kubernetes cluster on your local machine. It can be deployed
  using different drivers like Docker containers, virtual machines...
- `kubectl`: command line tool used to manage kubernetes clusters.
- `docker`: runtime used for running containers.
- `mlflow`: command line tool used to run experiments.

## Installation guides

- `minikube`: [link](https://minikube.sigs.k8s.io/docs/start/)
- `kubectl`: [link](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
- `docker`: [link](https://docs.docker.com/engine/install/ubuntu/)
- `mlflow`: [link](https://www.mlflow.org/docs/latest/quickstart.html)

## Prepare storage

We have to create a few folders to persist the data in our cluster:

```bash
$ sudo mkdir -p /mnt/data/{postgres,minio/mlflow}
$ sudo chown -R 1001 /mnt/data/
```

## Create cluster

Once we have all the necessary tools installed and the storage prepared, we are ready to create
the cluster:

```bash
$ minikube start --driver docker --mount --mount-string /mnt/data:/mnt/data
```

Remember that minikube deploys the cluster using containers, virtual machines... That means that
when we use persistent volumes and services, those are goint to apply to the k8s host, which is 
in fact the container or VM. 

To use local folders, we have to mount them using 
`--mount --mount-string <local/folder>/<container/folder>`.

To access services (NodePorts) we have to use the cluster IP address, which can be retrieved with:

```bash
$ minikube ip
```

## Navigation

- Previous: [README](../README.md)
- Next: [Set up MinIO](setup_minio.md)
