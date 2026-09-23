from src.rag.vector_store import VectorStore
import json
import os
import pandas as pd
from confluent_kafka import Consumer
from sklearn.ensemble import IsolationForest

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "air_quality"
KAFKA_GROUP_ID = "air_quality_anomaly_detector"

FEATURES = [
    "pm25",
    "pm10",
    "temperature",
    "humidity",
    "pressure"
]

MODEL_TRAINING_SIZE = 50
MODEL_CONTAMINATION = 0.05

OUTPUT_DIR = "data"
ANOMALIES_FILE = os.path.join(
    OUTPUT_DIR,
    "anomalies.jsonl"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_consumer():
    consumer = Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": KAFKA_GROUP_ID,
        "auto.offset.reset": "earliest"
    })

    consumer.subscribe([KAFKA_TOPIC])

    return consumer


def train_model(df):
    model = IsolationForest(
        contamination=MODEL_CONTAMINATION,
        random_state=42
    )

    model.fit(df[FEATURES])

    return model


def save_anomaly(data, score):
    anomaly = {
        "city": data["city"],
        "station_id": data["station_id"],
        "timestamp": data["timestamp"],
        "pm25": data["pm25"],
        "pm10": data["pm10"],
        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "pressure": data["pressure"],
        "anomaly_score": float(score),
        "description": (
            "Wykryto nietypowy pomiar jakości powietrza."
        )
    }

    with open(ANOMALIES_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(anomaly) + "\n")

    print(json.dumps(anomaly, indent=2, ensure_ascii=False))


def main():
    consumer = create_consumer()
    training_data = []
    model = None
    try:
        vector_store = VectorStore()
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                print(f"Blad Kafka: {msg.error()}")
                continue

            data = json.loads(
                msg.value().decode("utf-8")
            )

            row = {
                feature: data[feature]
                for feature in FEATURES
            }

            if model is None:
                training_data.append(row)

                print(
                    f"Training: "
                    f"{len(training_data)}/"
                    f"{MODEL_TRAINING_SIZE}"
                )

                if len(training_data) >= MODEL_TRAINING_SIZE:
                    df = pd.DataFrame(training_data)
                    model = train_model(df)

                continue

            df = pd.DataFrame([row])

            prediction = model.predict(df)[0]
            score = model.decision_function(df)[0]

            if prediction == -1:
                anomaly = {
                    **data,
                    "anomaly_score": float(score),
                    "description": (
                        "Wykryto nietypowy pomiar "
                        "jakosci powietrza."
                    )
                }
                save_anomaly(data, score)
                vector_store.save_anomaly(anomaly)

            else:
                print(
                    f"Normalny pomiar | "
                    f"PM2.5: {data['pm25']} | "
                    f"PM10: {data['pm10']}"
                )

    finally:
        consumer.close()


if __name__ == "__main__":
    main()