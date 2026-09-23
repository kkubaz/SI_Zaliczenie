import json
from pathlib import Path
import gradio as gr
from src.rag.vector_store import VectorStore
from src.rag.explainer import AnomalyExplainer

DATA_FILE = Path("data/anomalies.jsonl")
store = VectorStore()
explainer = AnomalyExplainer()

def load_anomalies():

    anomalies = []

    if not DATA_FILE.exists():
        return anomalies

    with DATA_FILE.open("r", encoding="utf-8") as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            try:
                anomaly = json.loads(line)
                anomalies.append(anomaly)

            except json.JSONDecodeError:
                print("Pominięto niepoprawny wpis JSON.")

    anomalies.sort(
        key=lambda x: x.get("timestamp", ""),
        reverse=True
    )

    return anomalies

def format_timestamp(timestamp):

    if not timestamp:
        return "-"

    return timestamp.replace("T", " ")[:19]


def find_previous_anomalies(anomaly):

    query = (
        f"Miasto: {anomaly.get('city', '')}. "
        f"Stacja: {anomaly.get('station_id', '')}. "
        f"PM2.5: {anomaly.get('pm25', '')}. "
        f"PM10: {anomaly.get('pm10', '')}. "
        f"Temperatura: {anomaly.get('temperature', '')}. "
        f"Wilgotność: {anomaly.get('humidity', '')}. "
        f"Ciśnienie: {anomaly.get('pressure', '')}."
    )
    print(query)

    results = store.search_similar(
        query,
        limit=10
    )

    previous = []

    current_timestamp = anomaly.get("timestamp")

    for result in results:

        payload = result.payload or {}

        if (
            current_timestamp
            and payload.get("timestamp") == current_timestamp
        ):
            continue

        previous.append(result)

        if len(previous) >= 3:
            break

    print(f"Podobnych anomalii: {len(previous)}")

    return previous

def explain_anomaly(anomaly):

    if not anomaly:
        return "Nie wybrano anomalii."

    print("Analizowana anomalia:")
    print(anomaly)

    try:

        previous_anomalies = find_previous_anomalies(anomaly)
        explanation = explainer.explain(
            anomaly,
            previous_anomalies
        )
        return explanation

    except Exception as error:

        print("!!! BŁĄD PODCZAS ANALIZY !!!")
        print(error)

        return (
            "### Wystąpił błąd podczas generowania analizy.\n\n"
            f"`{error}`"
        )


def create_explain_function(anomaly):

    def explain():

        return explain_anomaly(anomaly)

    return explain


with gr.Blocks(
    title="Detekcja anomalii jakości powietrza"
) as demo:

    gr.Markdown(
        """
Kliknij **Wyjaśnij**, aby przeanalizować wybraną anomalię
z wykorzystaniem wcześniejszych podobnych zdarzeń
znajdujących się w bazie Qdrant.
"""
    )

    refresh_button = gr.Button(
        "Odśwież listę anomalii"
    )

    analysis_output = gr.Markdown(
        "Wybierz anomalię i kliknij **Wyjaśnij**.",
        label="Analiza",
        height=250
    )

    gr.Markdown("## Historia anomalii")

    @gr.render(inputs=refresh_button)
    def render_anomalies(_=None):

        anomalies = load_anomalies()

        if not anomalies:

            gr.Markdown(
                "### Brak wykrytych anomalii."
            )

            return

        # Nagłówki tabeli
        with gr.Row():

            gr.Markdown("**Data i czas**")
            gr.Markdown("**Miasto**")
            gr.Markdown("**PM2.5**")
            gr.Markdown("**PM10**")
            gr.Markdown("**Temperatura**")
            gr.Markdown("**Wilgotność**")
            gr.Markdown("**Ciśnienie**")
            gr.Markdown("**Akcja**")

        # Wiersze tabeli
        for anomaly in anomalies:

            with gr.Row():

                gr.Markdown(
                    format_timestamp(
                        anomaly.get("timestamp")
                    )
                )

                gr.Markdown(
                    str(anomaly.get("city", "-"))
                )

                gr.Markdown(
                    str(anomaly.get("pm25", "-"))
                )

                gr.Markdown(
                    str(anomaly.get("pm10", "-"))
                )

                gr.Markdown(
                    str(anomaly.get("temperature", "-"))
                )

                gr.Markdown(
                    str(anomaly.get("humidity", "-"))
                )

                gr.Markdown(
                    str(anomaly.get("pressure", "-"))
                )

                explain_button = gr.Button(
                    "Wyjaśnij",
                    size="sm"
                )
                explain_button.click(
                    fn=create_explain_function(anomaly),
                    inputs=[],
                    outputs=analysis_output
                )

if __name__ == "__main__":

    demo.launch(
        server_name="127.0.0.1",
        server_port=7860
    )