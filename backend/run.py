import os

from app import create_app
from database.database import inicializar_banco

# Também usado pelos comandos do Flask, ex.: flask --app run db upgrade
app = create_app()

if __name__ == "__main__":
    inicializar_banco(app)
    # Ative o modo debug apenas em desenvolvimento: FLASK_DEBUG=1 no .env
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
