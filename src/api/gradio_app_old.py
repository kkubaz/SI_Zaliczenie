import gradio as gr
from src.rag.vector_store import VectorStore
from src.rag.explainer import AnomalyExplainer
store = VectorStore()
explainer = AnomalyExplainer()

def explain_measurement(
    city,
    station_id,
    pm25,
    pm10,
    temperature,
    humidity,
    pressure
):
    anomaly = {
        "city": city,
        "station_id": station_id,
        "timestamp": "2026-09-18T12:00:00+00:00",
        "pm25": float(pm25),
        "pm10": float(pm10),
        "temperature": float(temperature),
        "humidity": float(humidity),
        "pressure": float(pressure)
    }

    query = (
        f"Anomalia jakości powietrza w {city}. "
        f"PM2.5: {pm25}. PM10: {pm10}. "
        f"Temperatura: {temperature}."
    )

    similar_anomalies = store.search_similar(
        query,
        limit=3
    )

    explanation = explainer.explain(
        anomaly,
        similar_anomalies
    )

    return explanation


with gr.Blocks(title="Air Quality RAG") as demo:
    gr.Markdown(
        "# System RAG do analizy jakości powietrza"
    )

    gr.Markdown(
        "Wprowadź dane pomiarowe, aby uzyskać wyjaśnienie anomalii."
    )

    with gr.Row():
        city = gr.Textbox(
            label="Miasto",
            value="Gdansk"
        )

        station_id = gr.Textbox(
            label="Identyfikator stacji",
            value="GDN_001"
        )

    pm25 = gr.Number(
        label="PM2.5",
        value=250
    )

    pm10 = gr.Number(
        label="PM10",
        value=400
    )

    temperature = gr.Number(
        label="Temperatura",
        value=22
    )

    humidity = gr.Number(
        label="Wilgotność",
        value=65
    )

    pressure = gr.Number(
        label="Ciśnienie",
        value=1012
    )

    button = gr.Button("Wyjaśnij anomalię")

    output = gr.Textbox(
        label="Wyjaśnienie",
        lines=10
    )

    button.click(
        fn=explain_measurement,
        inputs=[
            city,
            station_id,
            pm25,
            pm10,
            temperature,
            humidity,
            pressure
        ],
        outputs=output
    )


if __name__ == "__main__":
    demo.launch()