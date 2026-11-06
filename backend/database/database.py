from app import db

def inicializar_banco(app):
    with app.app_context():
        db.create_all()
        print("Banco de dados EduCore inicializado com sucesso!")