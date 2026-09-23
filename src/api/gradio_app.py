import json
from pathlib import Path

import gradio as gr

from src.rag.vector_store import VectorStore
from src.rag.explainer import AnomalyExplainer


DATA_FILE = Path("data/anomalies.jsonl")


print("Uruchamianie Gradio...")
print("Ładowanie Qdrant...")
store = VectorStore()

print("Ładowanie modelu językowego...")
explainer = AnomalyExplainer()

print("Gradio jest gotowe.")


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

    print()
    print("========================================")
    print("Wyszukiwanie podobnych anomalii...")
    print(query)

    results = store.search_similar(
        query,
        limit=10
    )

    previous = []

    current_timestamp = anomaly.get("timestamp")

    for result in results:

        payload = result.payload or {}

        # bez aktualnie analizowanej anomalii
        if (
            current_timestamp
            and payload.get("timestamp") == current_timestamp
        ):
            continue

        previous.append(result)

        if len(previous) >= 3:
            break

    print(f"Znaleziono podobnych anomalii: {len(previous)}")
    print("========================================")

    return previous


def explain_anomaly(anomaly):

    print()
    print("========================================")
    print("KLIKNIĘTO PRZYCISK WYJAŚNIJ")
    print("========================================")

    if not anomaly:
        print("Brak anomalii.")
        return "Nie wybrano anomalii."

    print("Analizowana anomalia:")
    print(anomaly)

    try:

        previous_anomalies = find_previous_anomalies(anomaly)

        print("Uruchamianie modelu Qwen...")

        explanation = explainer.explain(
            anomaly,
            previous_anomalies
        )

        print("Analiza została wygenerowana.")

        return explanation

    except Exception as error:

        print()
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
# Detekcja anomalii jakości powietrza

Historia wykrytych anomalii w strumieniu danych IoT.

Kliknij **Wyjaśnij**, aby przeanalizować wybraną anomalię
z wykorzystaniem wcześniejszych podobnych zdarzeń
znajdujących się w bazie Qdrant.
"""
    )

    refresh_button = gr.Button(
        "🔄 Odśwież listę anomalii"
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

                # Najważniejsza zmiana:
                # funkcja przechowuje konkretną anomalię
                explain_button.click(
                    fn=create_explain_function(anomaly),
                    inputs=[],
                    outputs=analysis_output
                )

    gr.Markdown("---")

    gr.Markdown(
        """
### Jak działa analiza?

1. System wybiera anomalię z historii.
2. Dane anomalii są zamieniane na wektor.
3. Qdrant wyszukuje podobne zdarzenia.
4. Podobne anomalie są przekazywane jako kontekst RAG.
5. Model **Qwen2.5-1.5B-Instruct** analizuje aktualną anomalię.
6. Wynik jest wyświetlany powyżej tabeli.

Model językowy jest wcześniej wytrenowany i nie jest
trenowany ponownie w ramach projektu.
"""
    )


if __name__ == "__main__":

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860
    )