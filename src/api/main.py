from fastapi import FastAPI
from pydantic import BaseModel

from src.rag.vector_store import VectorStore
from src.rag.explainer import AnomalyExplainer


app = FastAPI(
    title="Air Quality Anomaly RAG API",
    description="API do wyjaśniania anomalii jakości powietrza",
    version="1.0.0"
)

store = None
explainer = None


class AirQualityMeasurement(BaseModel):
    city: str
    station_id: str
    timestamp: str
    pm25: float
    pm10: float
    temperature: float
    humidity: float
    pressure: float


@app.on_event("startup")
def startup_event():
    global store, explainer

    print("Inicjalizacja Qdrant...")
    store = VectorStore()

    print("Inicjalizacja modelu językowego...")
    explainer = AnomalyExplainer()


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Air Quality Anomaly RAG API działa"
    }


@app.post("/explain")
def explain_anomaly(measurement: AirQualityMeasurement):
    anomaly = measurement.model_dump()

    query = (
        f"Anomalia jakości powietrza w mieście {anomaly['city']}. "
        f"PM2.5: {anomaly['pm25']}. "
        f"PM10: {anomaly['pm10']}. "
        f"Temperatura: {anomaly['temperature']}."
    )

    similar_anomalies = store.search_similar(
        query,
        limit=3
    )

    explanation = explainer.explain(
        anomaly,
        similar_anomalies
    )

    return {
        "anomaly": anomaly,
        "similar_anomalies_count": len(similar_anomalies),
        "explanation": explanation
    }