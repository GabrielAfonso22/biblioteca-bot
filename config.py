import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

@dataclass
class Config:
    """
    Configuração que lê variáveis de ambiente.
    """
    # Azure CLU
    CLU_ENDPOINT: str = os.getenv("CLU_ENDPOINT", "")
    CLU_KEY: str = os.getenv("CLU_KEY", "")
    CLU_PROJECT_NAME: str = os.getenv("CLU_PROJECT_NAME", "BibliotecaCLU")
    CLU_DEPLOYMENT_NAME: str = os.getenv("CLU_DEPLOYMENT_NAME", "Producao")

    # Azure CosmosDB
    COSMOS_ENDPOINT: str = os.getenv("COSMOS_ENDPOINT", "")
    COSMOS_KEY: str = os.getenv("COSMOS_KEY", "")
    COSMOS_DATABASE_ID: str = os.getenv("COSMOS_DATABASE_ID", "BibliotecaDB")
    COSMOS_CONTAINER_ID: str = os.getenv("COSMOS_CONTAINER_ID", "Regras")

    # Bot Framework
    APP_ID: str = os.getenv("MicrosoftAppId", "")
    APP_PASSWORD: str = os.getenv("MicrosoftAppPassword", "")

CONFIG = Config()