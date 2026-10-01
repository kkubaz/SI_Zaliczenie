W pliku requirements.txt znajdują się niezbędne do instalacji biblioteki

# Uruchomienie Projektu

*docker compose up*
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
