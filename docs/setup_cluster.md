# Setup your Kubernetes cluster

## Introduction

The very first thing we must do is have our Kubernetes cluster up and running. In order tu achieve 
that, we are going to use the following tools:

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

## (Optional) GPU support prerequisites

- NVIDIA GPU
- NVIDIA drivers: [link](https://github.com/NVIDIA/nvidia-docker/wiki/Frequently-Asked-Questions#how-do-i-install-the-nvidia-driver)
- `nvidia-container-toolkit`: allows users to build and run GPU accelerated containers.
  - Installation guide: [link](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#install-guide)
  - Set up nvidia as your default runtime as explained [here](https://docs.nvidia.com/dgx/nvidia-container-runtime-upgrade/index.html#using-nv-container-runtime)

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
# Without GPU support
$ minikube start --driver docker --mount --mount-string /mnt/data:/mnt/data

# With GPU support
$ minikube start --driver none
```

Remember that k8s binds volumes and ports of its host. When using `driver=docker`, minikube deploys 
the cluster inside a container... That means that
when we use persistent volumes and services, those are goint to bind to the container. 

To use local folders with `driver=docker`, we have to mount them using 
`--mount --mount-string <local/folder>/<container/folder>`.

To access services (NodePorts) we have to use the cluster IP address, which can be retrieved with:

```bash
$ minikube ip
```

> **Note**: when using `driver=none`, check that CoreDNS is up and running
  (`kubectl get deployments -n kube-system`). If its not and the logs 
  (`kubectl logs --namespace=kube-system -l k8s-app=kube-dns`) says something like
  _Still waiting on: "kubernetes"_, you may need to check if your firewall configuration is denying
  the communication.

## (Optional) Enable GPU support

To enable GPUs, simply deploy NVIDIA's device plugin:

```bash
$ kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/master/nvidia-device-plugin.yml
```

You can check that your GPU is available in your cluster with the script located at `tools/check_gpus.sh`

Finally, you can validate the installation deploying the sample app located at `manifests/gpu/pod.yml`:

```bash
$ kubectl apply -f manifests/gpu/pod.yml

  pod/cuda-vector-add configured


$ kubectl get pod/cuda-vector-add

  NAME              READY   STATUS      RESTARTS   AGE
  cuda-vector-add   0/1     Completed   0          48m


$ kubectl logs pod/cuda-vector-add   

  [Vector addition of 50000 elements]
  Copy input data from the host memory to the CUDA device
  CUDA kernel launch with 196 blocks of 256 threads
  Copy output data from the CUDA device to the host memory
  Test PASSED 
```


## Navigation

- Previous: [README](../README.md)
- Next: [Set up MinIO](setup_minio.md)
