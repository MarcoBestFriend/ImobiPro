"""
================================================================================
IMOBIPRO - PONTO DE ENTRADA PARA PRODUÇÃO (Gunicorn)
================================================================================
Este arquivo é usado pelo Gunicorn para iniciar o servidor em produção.

Comando para iniciar em produção:
    gunicorn --workers 2 --bind 0.0.0.0:8000 wsgi:app

Normalmente o Nginx repassa as requisições para a porta 8000,
e o Gunicorn entrega ao Flask.

Em desenvolvimento, continue usando:
    python3 app.py
================================================================================
"""

from dotenv import load_dotenv
load_dotenv()

from app import app

if __name__ == '__main__':
    app.run()
