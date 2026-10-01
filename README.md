# Opis plików
requirements.txt - niezbędne biblioteki

docker-compose.yml - plik do 

src/producer.py - imituje urzadzenie do pomiaru parametrów powietrza i wysyła je do Kafki

src/consumer.py - odbiera dane z Kafki. Następnie trenuje *IsolationForest* za pomoca 50 pierwszych odczytów i na jego podstawie odróżnia normalne pomiary od anomalii. Następnie wykryte anomalie zapisuje lokalnie do pliku *data/anomalies.jsonl* i do bazy Qdrant.

src/api.py - FAST API

src/gradio_app.py - UI aplikacji stworzone za pomocą *gradio*. Korzysta z klasy VectorStore do wyszukiwania podobnych anomalii do wybranej i AnomalyExplainer do generacji wyjaśnienia anomalii.. 

src/rag/explainer.py - definicja klasy AnomalyExplainer odpowiedzialnej za obsługę pretrenowanego modelu Qwen2.5-1.5B-Instruct z Hugging Face.

src/rag/vector_store.py - definicja klasy VectorStore odpowiedzialnej za komunikację z quadrant i embedding. Korzysta z *sentence_transformers* z modelu *all-MiniLM-L6-v2*

# Uruchomienie Projektu

  >`docker compose up`
Uruchamia 3 kontenery w Docker Desktop
- qdrant: wektorowa baza danych
- kafka: broker wiadomości
- kafdrop: UI do kafki

## Terminal 1
  >`python -m src.producer`

Produkcja przykładowych pomiarów

## Terminal 2
  >`python -m src.consumer`

Przechwytywanie danych pomiarowych 

## Terminal 3
  >`python -m uvicorn src.api:app`

Uruchomienie API

## Terminal 4
  >`python -m src.gradio_app`

Uruchomienie UI

# Dostępy
- Widok Kafka poprzez Kafdrop - http://localhost:9000/
- Widok bazy Qdrant http://localhost:6333/dashboard
- Aplikacja (Gradio) - http://localhost:7860
