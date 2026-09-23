W pliku requirements.txt znajdują się niezbędne do instalacji biblioteki

Uruchomienie Projektu
docker compose up

[Terminal_1]
  python -m src.producer.main
Produkcja przykładowych pomiarów

[Terminal_2]
  python -m src.consumer.main
Przechwytywanie danych pomiarowych 

[Terminal_3]
  python -m uvicorn src.api.main:app --reload
Uruchomienie API

[Terminal_4]
  python -m src.api.gradio_app
Uruchomienie UI

Dostępy
Aplikacja (Gradio) - localhost:7860
