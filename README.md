# SI_Zaliczenie

Uruchomienie Projektu

>docker compose up
>.\.venv.\Scripts\Activate.ps1
>[T1]
>python -m src.producer.main
>[T2]
>python -m src.consumer.main
>[T3]
>uvicorn src.api.main:app --reload
>[T4]
>python -m src.api.gradio_app
>localhost:7860
