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
    