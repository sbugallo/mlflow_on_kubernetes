# Run MLflow Project

> You can find some sample files for this section in `mlflow_on_kubernetes/manifests/mlflow_project`.

## What is MLflow Project

> An MLflow Project is a format for packaging data science code in a reusable and reproducible way, 
  based primarily on conventions. In addition, the Projects component includes an API and 
  command-line tools for running projects, making it possible to chain together projects into 
  workflows.

> At the core, MLflow Projects are just a convention for organizing and describing your code to let 
  other data scientists (or automated tools) run it. Each project is simply a directory of files, 
  or a Git repository, containing your code. MLflow can run some projects based on a convention for 
  placing files in this directory, but you can describe your project in more detail by adding a 
  MLproject file, which is a YAML formatted text file. 

## Docker environment

We are going to run these projects inside a Docker container. In order to do that, we are going
to create a base image with all the needed dependencies. This image must be accesible inside the
cluster. In this sample deployment we are going to use DockerHub as our registry, making all images
publicly available.

### Dockerfile

We are going to use the following Dockerfile to build the image:

```docker
FROM continuumio/miniconda3

RUN pip install --no-cache-dir \
        mlflow numpy Cython scipy pandas scikit-learn boto3 cloudpickle typer loguru
```

To build it, simply run `docker build -t <your DockerHub username>/<image name>:<versions> .` inside
the folder containing the Dockerfile. For
example:

```bash
$ docker build -t docker build -t sbugallo/mlflow-sample-env:0.0.1 .
```

Once the image is build, simply push it running 
`docker push <your DockerHub username>/<image name>:<versions>`. For example:

```bash
$ docker push sbugallo/mlflow-sample-env:0.0.1
```

## Project

Next, let's create the MLflow Project files.

### MLproject

In this file we are going the define the docker image to be used and the entry point parameters.

```yaml
name: docker-example

docker_env:
  image:  <Docker image to be used>

entry_points:
  main:
    parameters:
      alpha: float
      l1_ratio: {type: float, default: 0.1}
    command: "python train.py --alpha {alpha} --l1-ratio {l1_ratio}"
```

### Sample data

We can download the CSV from [here](https://archive.ics.uci.edu/ml/datasets/wine+quality). The
data looks like this:

```csv
"fixed acidity",  "volatile acidity", ...,  "quality"
7,                0.27,               ...,  6
6.3,              0.3,                ...,  6
8.1,              0.28,               ...,  6
```

### Experiment script

You can use the following script to train and evaluate the model and log everything to MLflow
Tracking.

```python
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
import typer

from loguru import logger
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


@logger.catch(reraise=True)
def main(alpha: float = typer.Option(...), l1_ratio: float = typer.Option(...)):
    np.random.seed(40)
    
    mlflow.set_tracking_uri("http://mlflow-service:5000")
    with mlflow.start_run():

        logger.info("Loading data")
        data_path = Path(__file__).parent / "wine-quality.csv"
        data = pd.read_csv(str(data_path))

        train, test = train_test_split(data)

        train_x = train.drop(["quality"], axis=1)
        test_x = test.drop(["quality"], axis=1)
        train_y = train[["quality"]]
        test_y = test[["quality"]]

        logger.info("Training model")
        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(train_x, train_y)

        mlflow.sklearn.log_model(lr, "model")

        logger.info("Evaluating model")
        predicted_qualities = lr.predict(test_x)

        rmse = np.sqrt(mean_squared_error(test_y, predicted_qualities))
        mae = mean_absolute_error(test_y, predicted_qualities)
        r2 = r2_score(test_y, predicted_qualities)
        
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)
        
        logger.info("Done")

if __name__ == "__main__":
    typer.run(main)
```

**Note**: we are setting MLflow's tracking URI to its service so the communications and traffic 
do not leave outside the cluster.

## Job

Once we have the MLflow Project prepared, we have to create a Job template describing the 
environment and resources. Note that we are injecting MinIO's values using its secrets.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: "{replaced with MLflow Project name}"
  namespace: default
spec:
  ttlSecondsAfterFinished: 100
  backoffLimit: 0
  template:
    spec:
      
      containers:
      - name: "{replaced with MLflow Project name}"
        image: "{replaced with URI of Docker image created during Project execution}"
        command: ["{replaced with MLflow Project entry point command}"]
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
      resources:
        limits:
          memory: 512Mi
        requests:
          memory: 256Mi
      restartPolicy: Never
```

## Kubernetes config file

Lastly, we have to create a config file so MLflow's CLI knows how to interact with the cluster:

```json
{
    "kube-context": "minikube",
    "kube-job-template-path": "<path/to/job/template.yml>",
    "repository-uri": "<run image to be created>"
}
```

For example:

```json
{
    "kube-context": "minikube",
    "kube-job-template-path": "/home/sbugallo/Projects/Personal/mlflow_on_kubernetes/manifests/mlflow_project/job.yaml",
    "repository-uri": "sbugallo/mlflow-k8s"
}
```

**Note**: MLflow, in order to run your project, creates a new Docker image on top the base image you
created before. Then it pushes it the registry so it can be pulled from the cluster. The name of 
this new image is the value that goes in `repository-uri`.

## Running the project 

The last step is to run the project inside the cluster and validate that everything runs and that
results are stored and displayed in MLflow's UI.

To run the project execute:

```bash
$ MLFLOW_TRACKING_URI=http://$(minikube ip):30500 mlflow run <path/to/the/project/folder> \
    --experiment-name sample-experiment \
    --backend kubernetes \
    --backend-config /home/sbugallo/Projects/Personal/mlflow_on_kubernetes/manifests/mlflow_project/kubernetes_config.json \
    -P alpha=1
```

For example:

```bash
$ MLFLOW_TRACKING_URI=http://$(minikube ip):30500 mlflow run manifests/mlflow_project/project \
    --experiment-name sample-experiment \
    --backend kubernetes \
    --backend-config /home/sbugallo/Projects/Personal/mlflow_on_kubernetes/manifests/mlflow_project/kubernetes_config.json \
    -P alpha=1
```
## Navigation

- Previous: [Set up MLflow server](setup_mlflow_server.md)