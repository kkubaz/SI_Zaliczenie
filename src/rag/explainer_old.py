from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class AnomalyExplainer:
    def __init__(self):
        self.model_name = "google/flan-t5-small"

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name
        )

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_name
        )

    def build_prompt(self, anomaly: dict, similar_anomalies: list) -> str:
        context = ""

        for index, item in enumerate(similar_anomalies, start=1):
            payload = item.payload or {}

            context += (
                f"\nPodobna anomalia {index}:\n"
                f"Miasto: {payload.get('city')}\n"
                f"PM2.5: {payload.get('pm25')}\n"
                f"PM10: {payload.get('pm10')}\n"
                f"Temperatura: {payload.get('temperature')}\n"
                f"Wilgotność: {payload.get('humidity')}\n"
                f"Ciśnienie: {payload.get('pressure')}\n"
                f"Opis: {payload.get('description')}\n"
            )

        prompt = f"""
Jesteś analitykiem jakości powietrza.
Przeanalizuj anolamię pogodową o parametrach:

Miasto: {anomaly.get('city')}
Stacja: {anomaly.get('station_id')}
PM2.5: {anomaly.get('pm25')}
PM10: {anomaly.get('pm10')}
Temperatura: {anomaly.get('temperature')}
Wilgotność: {anomaly.get('humidity')}
Ciśnienie: {anomaly.get('pressure')}

Opisz anomalie w nastepujący sposób:
1. Wskaż możliwe przyczyny.
2. Zaproponuj działania kontrolne.

Nie wymyślaj faktów, których nie ma w danych.

Podobne zdarzenia podobne do anomalii (traktuj je jako kontekst, a skup sie na poprawnej analizie danych):
{context}


"""

        return prompt

    def explain(self, anomaly: dict, similar_anomalies: list) -> str:
        prompt = self.build_prompt(
            anomaly,
            similar_anomalies
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=250,
            min_new_tokens=40,
            do_sample=False,
            num_beams=4,
            repetition_penalty=1.2,
            early_stopping=True
        )

        explanation = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        if len(explanation.strip()) < 30:
            return (
                f"Wykryto nietypowy pomiar: "
                f"Miasto: {anomaly.get('city')}. "
                f"PM2.5: {anomaly.get('pm25')}, "
                f"PM10: {anomaly.get('pm10')}. "
            )

        return explanation