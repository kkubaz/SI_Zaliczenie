import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class AnomalyExplainer:
    """
    Wyjaśnianie anomalii przy użyciu gotowego,
    wcześniej wytrenowanego modelu Qwen2.5-1.5B-Instruct.

    Model nie jest trenowany w ramach projektu.
    Jest wykorzystywany wyłącznie do generowania
    opisu na podstawie danych i kontekstu RAG.
    """

    def __init__(self):
        print("Ładowanie modelu Qwen2.5-1.5B-Instruct...")

        self.model_name = "Qwen/Qwen2.5-1.5B-Instruct"

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto"
        )

        self.model.eval()

        print("Model Qwen2.5-1.5B-Instruct został załadowany.")

    def build_messages(self, anomaly: dict, similar_anomalies: list):

        similar_context = []

        for index, item in enumerate(similar_anomalies[:3], start=1):
            payload = item.payload or {}

            similar_context.append(
                f"""
Zdarzenie {index}:
PM2.5: {payload.get('pm25', 'brak')}
PM10: {payload.get('pm10', 'brak')}
Temperatura: {payload.get('temperature', 'brak')}
Wilgotność: {payload.get('humidity', 'brak')}
Ciśnienie: {payload.get('pressure', 'brak')}
""".strip()
            )

        similar_text = "\n\n".join(similar_context)

        system_message = """
Jesteś ekspertem analizującym dane dotyczące jakości powietrza.

Twoim zadaniem jest przygotowanie krótkiego, rzeczowego
wyjaśnienia wykrytej anomalii.

Nie wymyślaj faktów.
Nie twierdź, że znasz rzeczywistą przyczynę anomalii,
jeżeli nie wynika ona bezpośrednio z danych.

Możesz wskazać możliwe przyczyny jako hipotezy.

Odpowiadaj wyłącznie po polsku.
Nie powtarzaj całych danych wejściowych.
""".strip()

        user_message = f"""
Przeanalizuj następujący pomiar:

Miasto: {anomaly.get('city', 'brak')}
Stacja: {anomaly.get('station_id', 'brak')}
PM2.5: {anomaly.get('pm25', 'brak')}
PM10: {anomaly.get('pm10', 'brak')}
Temperatura: {anomaly.get('temperature', 'brak')}
Wilgotność: {anomaly.get('humidity', 'brak')}
Ciśnienie: {anomaly.get('pressure', 'brak')}

Podobne anomalie znalezione w bazie Qdrant:

{similar_text if similar_text else "Brak podobnych anomalii."}

Przygotuj krótką odpowiedź zawierającą:

1. Opis tego, co jest nietypowe.
2. Możliwe przyczyny, wyraźnie oznaczone jako możliwe.
3. Co warto sprawdzić.

Odpowiedź powinna mieć około 3-6 zdań.
""".strip()

        return [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

    def explain(self, anomaly: dict, similar_anomalies: list) -> str:

        messages = self.build_messages(
            anomaly,
            similar_anomalies
        )

        # Oficjalny sposób przygotowania rozmowy
        # dla modeli Qwen Instruct.
        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        )

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=180,
                do_sample=True,
                temperature=0.4,
                top_p=0.9,
                repetition_penalty=1.15
            )

        # Usuwamy tokeny odpowiadające promptowi.
        generated_tokens = outputs[0][
            inputs["input_ids"].shape[-1]:
        ]

        explanation = self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True
        ).strip()

        if not explanation:
            return self.fallback(anomaly)

        return explanation

    def fallback(self, anomaly: dict) -> str:

        return (
            f"Wykryto nietypowy pomiar jakości powietrza "
            f"w mieście {anomaly.get('city', 'nieznanym')}. "
            f"PM2.5 wynosi {anomaly.get('pm25', 'brak')}, "
            f"a PM10 {anomaly.get('pm10', 'brak')}. "
            f"Zalecane jest sprawdzenie kolejnych pomiarów "
            f"oraz poprawności działania stacji pomiarowej."
        )