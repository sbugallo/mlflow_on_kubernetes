FROM python:3.8.2-slim

LABEL maintainer="Sergio Bugallo <sergiobugalloenjamio@gmail.com"

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir  mlflow[extras]==v1.20.2 PyMySQL psycopg2-binary
    
EXPOSE 5000

ENTRYPOINT ["mlflow", "server"]
