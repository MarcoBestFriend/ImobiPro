"""
================================================================================
IMOBIPRO - CONFIGURAÇÕES DA APLICAÇÃO WEB
================================================================================
Autor: Sistema ImobiPro
Data: Janeiro 2026
Descrição: Configurações centralizadas da aplicação Flask
================================================================================
"""

import os
from datetime import timedelta

class Config:
    """Configurações base da aplicação."""
    
    # Chave secreta para sessões (gerar uma aleatória em produção)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'imobipro-dev-secret-key-2026'
    
    # Configuração do banco de dados
    DATABASE_PATH = 'database/imobipro.db'
    
    # Configuração de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    SESSION_COOKIE_SECURE = False  # True quando usar HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuração de upload (para fotos futuras)
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    # Configuração de paginação
    ITEMS_PER_PAGE = 20
    
    # Formato de data brasileiro
    DATE_FORMAT = '%d/%m/%Y'
    DATE_FORMAT_SQL = '%Y-%m-%d'
    
    # Moeda
    CURRENCY_SYMBOL = 'R$'
    
    # Validações de formulários (baseadas na planilha)
    FORMAS_PAGAMENTO_IPTU = ['Anual', 'Mensal']
    SITUACOES_PESSOA = ['Inquilino', 'Fiador', 'Ambos']
    ESTADOS_CIVIS = ['Solteiro', 'Casado', 'Divorciado', 'Viúvo']
    TIPOS_GARANTIA = ['antecipado', 'nenhuma', 'fiança', 'caução']
    STATUS_CONTRATO = ['Ativo', 'Prorrogado', 'Encerrado', 'Rescindido']
    TIPOS_DESPESA = ['Manutenção', 'Condomínio', 'Reforma', 'IPTU', 'Outros']
    STATUS_PAGAMENTO = ['Pendente', 'Recebido', 'Atrasado', 'Cancelado']
    
    # Configuração de desenvolvimento/produção
    DEBUG = True
    TESTING = False
    
    # Fuso horário
    TIMEZONE = 'America/Campo_Grande'

    # Configuração de login
    # Para alterar a senha, modifique a variável abaixo
    LOGIN_USERNAME = 'admin'
    LOGIN_PASSWORD = 'imobipro2026'  # Altere esta senha!


class DevelopmentConfig(Config):
    """Configurações para ambiente de desenvolvimento."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configurações para ambiente de produção."""
    DEBUG = False
    TESTING = False
    # Em produção, usar variáveis de ambiente
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'CHANGE-THIS-IN-PRODUCTION'


class TestingConfig(Config):
    """Configurações para testes."""
    DEBUG = True
    TESTING = True
    DATABASE_PATH = 'database/imobipro_test.db'


# Configuração padrão
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env='default'):
    """Retorna a configuração apropriada."""
    return config.get(env, config['default'])