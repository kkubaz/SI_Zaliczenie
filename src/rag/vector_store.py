from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)
from sentence_transformers import SentenceTransformer

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "air_quality_anomalies"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
VECTOR_SIZE = 384

class VectorStore:

    def __init__(self):
        self.client = QdrantClient(
            url=QDRANT_URL
        )

        self.embedding_model = SentenceTransformer(
            EMBEDDING_MODEL_NAME
        )

        self.create_collection()

    def create_collection(self):

        collections = self.client.get_collections()

        collection_names = [
            collection.name
            for collection in collections.collections
        ]

        if COLLECTION_NAME not in collection_names:

            self.client.create_collection(
                collection_name=COLLECTION_NAME,

                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )

            print(
                f"Utworzono kolekcje: "
                f"{COLLECTION_NAME}"
            )

        else:
            print(
                f"Kolekcja {COLLECTION_NAME} "
                "juz istnieje."
            )

    def create_embedding(self, text: str):

        vector = self.embedding_model.encode(
            text
        )

        return vector.tolist()

    def save_anomaly(self, anomaly: dict):

        description = self.create_description(
            anomaly
        )

        vector = self.create_embedding(
            description
        )

        point = PointStruct(
            id=self.generate_id(anomaly),
            vector=vector,
            payload={
                **anomaly,
                "description": description
            }
        )

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[point]
        )

    def create_description(self, anomaly: dict):

        return (
            f"Miasto: {anomaly['city']}. "
            f"Stacja: {anomaly['station_id']}. "
            f"PM2.5: {anomaly['pm25']}. "
            f"PM10: {anomaly['pm10']}. "
            f"Temperatura: {anomaly['temperature']}. "
            f"Wilgotnosc: {anomaly['humidity']}. "
            f"Cisnienie: {anomaly['pressure']}. "
            f"Opis: {anomaly.get('description', '')}"
        )

    def generate_id(self, anomaly: dict):

        timestamp = anomaly["timestamp"]

        return abs(hash(timestamp)) % (2**63)

    def search_similar(
        self,
        text: str,
        limit: int = 5
    ):

        vector = self.create_embedding(text)

        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=limit
        )

        return results.points