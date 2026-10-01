import pandas as pd
from sklearn.ensemble import IsolationForest
FEATURES = [
    "pm25",
    "pm10",
    "temperature",
    "humidity",
    "pressure"
]
class AnomalyDetector:

    def __init__(self):
        self.model = IsolationForest(
            contamination=0.05,
            random_state=42
        )

    def fit(self, df: pd.DataFrame):
        self.model.fit(df[FEATURES])

    def predict(self, df: pd.DataFrame):
        predictions = self.model.predict(df[FEATURES])
        return predictions == -1