import asyncio
from azure.cosmos.aio import CosmosClient
from azure.core.exceptions import AzureError
from config import CONFIG
from typing import Dict, Any

class CosmosDbService:
    """
    Serviço para interagir com o Azure CosmosDB.
    Assume-se que existe um documento de configuração (ID: 'library_config')
    no container 'Regras' para armazenar as regras de negócio.
    """

    def __init__(self):
        """Inicializa o cliente assíncrono do CosmosDB."""
        self.client = CosmosClient(
            CONFIG.COSMOS_ENDPOINT, 
            CONFIG.COSMOS_KEY
        )
        self.database_name = CONFIG.COSMOS_DATABASE_ID
        self.container_name = CONFIG.COSMOS_CONTAINER_ID
        self.config_document_id = "library_config"

    async def get_library_config(self) -> Dict[str, Any]:
        """
        Recupera o documento de configuração principal do container de Regras.

        Se o documento não existir, ele é criado com um conteúdo mock inicial
        para garantir que o bot funcione mesmo com um DB vazio.
        """
        try:
            database = self.client.get_database_client(self.database_name)
            container = database.get_container_client(self.container_name)

            # Tenta ler o documento de configuração
            config_doc = await container.read_item(
                item=self.config_document_id,
                # Assume que o ID é a chave de partição. Se a chave for diferente, ajuste aqui.
                partition_key=self.config_document_id 
            )
            print("CosmosDB: Documento de configuração recuperado com sucesso.")
            return config_doc

        except AzureError as e:
            # Documento não encontrado ou erro de conexão, cria um documento mock
            print(f"CosmosDB Error: Falha ao ler documento de regras. Tentando criar mock ou o documento está ausente: {e}")
            return await self._create_mock_config()
        except Exception as e:
            print(f"Erro inesperado no CosmosDB: {e}")
            return {}

    async def _create_mock_config(self) -> Dict[str, Any]:
        """Cria e insere um documento mock de configuração no CosmosDB (para testes iniciais)."""
        mock_data = {
            "id": self.config_document_id,
            "horarios": {
                "dias_uteis": "08:00 às 22:00",
                "finais_de_semana": "Sábados: 09:00 às 13:00. Domingos: Fechado."
            },
            "emprestimo": {
                "renovacao_passos": "A renovação deve ser feita pelo Portal do Aluno. Procure a seção 'Meus Empréstimos'.",
                "condicoes_negativas": [
                    "Livro em atraso: Multa pendente, procure o balcão de atendimento.",
                    "Livro reservado por outra pessoa: Não é possível renovar, devolva-o na data limite."
                ]
            },
            "reserva": {
                "passos": "A reserva de livros é feita exclusivamente pelo sistema online no Portal do Aluno, na página de detalhes do livro.",
                "integracao_status": "O sistema verifica a disponibilidade em tempo real."
            }
        }
        try:
            database = self.client.get_database_client(self.database_name)
            container = database.get_container_client(self.container_name)
            
            # Upsert (cria ou substitui) o documento mock
            await container.upsert_item(mock_data)
            print("CosmosDB: Documento mock criado e inserido com sucesso (se o DB estiver acessível).")
            return mock_data
        except Exception as e:
            print(f"Erro ao criar documento mock no CosmosDB. Verifique a chave e o endpoint: {e}")
            return {}

# O serviço de DB é inicializado como singleton
cosmos_db_service = CosmosDbService()