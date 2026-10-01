import json
import random
import time
from datetime import datetime, timezone
from confluent_kafka import Producer

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "air_quality"

producer = Producer({
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS
})


def generate_measurement():
    measurement = {
        "city": "Gdansk",
        "station_id": "GDN_001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pm25": round(random.uniform(5, 35), 2),
        "pm10": round(random.uniform(10, 60), 2),
        "temperature": round(random.uniform(5, 25), 2),
        "humidity": round(random.uniform(40, 85), 2),
        "pressure": round(random.uniform(990, 1030), 2)
    }

    return measurement

def delivery_report(err, msg):
    if err is not None:
        print(f"Blad dostarczenia: {err}")
    else:
        print(
            f"Wyslano: topic={msg.topic()} "
            f"partition={msg.partition()} "
            f"offset={msg.offset()}"
        )


def main():
    try:
        while True:
            measurement = generate_measurement()

            producer.produce(
                KAFKA_TOPIC,
                key=measurement["station_id"],
                value=json.dumps(measurement),
                callback=delivery_report
            )

            producer.poll(0)

            print(json.dumps(measurement, indent=2))

            time.sleep(2)

    finally:
        producer.flush()


if __name__ == "__main__":
    main()