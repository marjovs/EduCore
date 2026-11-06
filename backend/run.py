import os

from app import create_app
from database.database import inicializar_banco

app = create_app()

inicializar_banco(app)

if __name__ == "__main__":
    # Ative o modo debug apenas em desenvolvimento: FLASK_DEBUG=1 no .env
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
