import asyncio
import sys
import traceback
from aiohttp import web
from botbuilder.core import (
    ActivityHandler,
    TurnContext,
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    MessageFactory,
)
from botbuilder.schema import Activity, ActivityTypes, ChannelAccount
from azure.ai.language.conversations.aio import ConversationAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError
from typing import Dict, Any

from config import CONFIG
from data_access import cosmos_db_service

# --- Dependências Necessárias ---
# pip install botbuilder-core aiohttp azure-ai-language-conversations azure-cosmos

class LibraryBot(ActivityHandler):
    """
    Chatbot principal da biblioteca. Lida com interações, chama o Azure CLU e roteia intenções.
    """
    def __init__(self):
        print("Inicializando o cliente Azure CLU...")
        credential = AzureKeyCredential(CONFIG.CLU_KEY)
        self.clu_client = ConversationAnalysisClient(
            CONFIG.CLU_ENDPOINT, credential
        )
        self.project_name = CONFIG.CLU_PROJECT_NAME
        self.deployment_name = CONFIG.CLU_DEPLOYMENT_NAME
        print(f"CLU Configurado: Projeto='{self.project_name}', Deployment='{self.deployment_name}'")

    async def on_message_activity(self, turn_context: TurnContext):
        user_text = turn_context.activity.text
        if not user_text:
            return

        # 1. Carregar Regras do CosmosDB
        config_data = await cosmos_db_service.get_library_config()
        if not config_data or not isinstance(config_data, dict):
            await turn_context.send_activity(
                "Desculpe, não consegui carregar as regras de negócio da biblioteca (CosmosDB)."
            )
            return

        # 2. Chamar o Azure CLU
        try:
            response = await self.clu_client.analyze_conversation(
                task={
                    "kind": "Conversation",
                    "analysisInput": {
                        "conversationItem": {
                            "text": user_text,
                            "id": "1",
                            "participantId": "user_1"
                        }
                    },
                    "parameters": {
                        "projectName": self.project_name,
                        "deploymentName": self.deployment_name,
                        "isLoggingEnabled": False
                    }
                }
            )

            # Lógica robusta para extrair a intenção (suporta Dict ou Objeto)
            top_intent = ""
            confidence = 0.0

            if isinstance(response, dict):
                result_data = response.get("result", response)
                prediction = result_data.get("prediction", {})
                top_intent = prediction.get("topIntent") or prediction.get("top_intent")
                intents = prediction.get("intents", [])
                if intents:
                    first = intents[0]
                    confidence = first.get("confidenceScore") or first.get("confidence_score") or 0.0
            else:
                result_obj = getattr(response, "result", response)
                prediction_obj = getattr(result_obj, "prediction", None)
                if prediction_obj:
                    top_intent = getattr(prediction_obj, "top_intent", None) or getattr(prediction_obj, "topIntent", None)
                    intents_list = getattr(prediction_obj, "intents", [])
                    if intents_list:
                        confidence = getattr(intents_list[0], "confidence_score", 0.0)

            print(f"CLU Retornou: Intent='{top_intent}', Confidence={confidence:.2f}")

            # 3. Roteamento de Intenções
            if confidence < 0.7:
                await self.handle_unrecognized_intent(turn_context, user_text, "Confiança baixa.")
                return

            # --- CORREÇÃO FINAL: Nomes exatos conforme sua imagem do Azure ---
            
            if top_intent == "Consultar_Horario": 
                await self.handle_consultar_horario(turn_context, config_data)
            
            elif top_intent == "Renovar_Emprestimo":
                await self.handle_renovar_emprestimo(turn_context, config_data)
            
            elif top_intent == "Reservar_Livro": # Corrigido de 'Reservar_Livros' para 'Reservar_Livro' (Singular)
                await self.handle_reservar_livros(turn_context, config_data)
            
            else:
                await self.handle_unrecognized_intent(turn_context, user_text, f"Intenção '{top_intent}' não mapeada.")

        except Exception as err:
            print(f"Erro Geral: {err}")
            traceback.print_exc()
            await turn_context.send_activity(f"Ocorreu um erro técnico: {type(err).__name__}")

    # --- Handlers ---

    async def handle_consultar_horario(self, turn_context: TurnContext, config: Dict):
        horarios = config.get("horarios", {})
        msg = (
            "✅ **Horários de Funcionamento:**\n\n"
            f"- Dias Úteis: {horarios.get('dias_uteis', 'ND')}\n"
            f"- Finais de Semana: {horarios.get('finais_de_semana', 'ND')}"
        )
        await turn_context.send_activity(MessageFactory.text(msg))

    async def handle_renovar_emprestimo(self, turn_context: TurnContext, config: Dict):
        emp = config.get("emprestimo", {})
        condicoes = "\n".join([f"- {c}" for c in emp.get("condicoes_negativas", [])])
        msg = (
            "📚 **Renovação de Livros**\n\n"
            f"Como fazer: {emp.get('renovacao_passos', 'ND')}\n\n"
            f"Condições:\n{condicoes}"
        )
        await turn_context.send_activity(MessageFactory.text(msg))

    async def handle_reservar_livros(self, turn_context: TurnContext, config: Dict):
        res = config.get("reserva", {})
        msg = (
            "📖 **Reserva de Livros**\n\n"
            f"Passos: {res.get('passos', 'ND')}\n"
            f"Status: {res.get('integracao_status', 'ND')}"
        )
        await turn_context.send_activity(MessageFactory.text(msg))

    async def handle_unrecognized_intent(self, turn_context: TurnContext, user_text: str, reason: str = ""):
        print(f"Não reconhecido: {user_text} ({reason})")
        msg = (
            f"Desculpe, não entendi '{user_text}'.\n"
            "Tente perguntar: 'Qual o horário?', 'Como renovar?' ou 'Quero reservar'."
        )
        await turn_context.send_activity(MessageFactory.text(msg))

    async def on_members_added_activity(self, members_added: [ChannelAccount], turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Olá! Sou o Chatbot da Biblioteca.")

# --- Configuração do Servidor ---
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)
ADAPTER.on_turn_error = lambda c, e: print(f"Erro não tratado: {e}") or c.send_activity("Erro crítico no bot.")
BOT = LibraryBot()

async def messages(req: web.Request) -> web.Response:
    if "application/json" not in req.headers.get("Content-Type", ""): return web.Response(status=415)
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")
    await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    return web.Response(status=200)

if __name__ == "__main__":
    APP = web.Application()
    APP.router.add_post("/api/messages", messages)
    web.run_app(APP, host="localhost", port=9000)