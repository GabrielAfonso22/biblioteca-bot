📚 Chatbot de Biblioteca Inteligente (BibliotecaCLU)

Este projeto implementa um sistema conversacional inteligente para dar suporte aos usuários de uma biblioteca universitária. O bot foi desenvolvido com o Microsoft Bot Framework em Python, utilizando o Azure Cognitive Services para entender a linguagem natural e o Azure CosmosDB para persistência das regras de negócio.

Arquitetura do Projeto

A solução segue um modelo Serverless e orientada a serviços, utilizando a stack do Azure para inteligência e dados.

| Componente | Função | Tecnologia | | Interface | Interação com o usuário via Bot Framework Emulator | Microsoft Bot Framework (Python) | | Inteligência | Classificação da intenção do usuário (ex: "Consultar Horário") | Azure Conversational Language Understanding (CLU) | | Persistência | Armazenamento das regras de negócio (horários, condições de renovação) | Azure CosmosDB (API SQL) | | Automação | Garante a integridade do código e o processo de entrega contínua | GitHub Actions |

✨ Funcionalidades

O chatbot foi treinado para lidar com as seguintes intenções (Intents) do domínio da biblioteca:

| Intent (CLU) | Descrição | Dados Usados (CosmosDB) | | Consultar_Horario | Informa os horários de funcionamento em dias úteis e finais de semana. | Horários | | Renovar_Emprestimo | Explica o procedimento de renovação e lista as condições que impedem a ação (atraso, reserva). | Passos e Condições | | Reservar_Livro | Orienta o usuário sobre o processo de reserva de livros. | Passos de Reserva |

🚀 Como Rodar o Projeto Localmente

Para testar o bot no seu ambiente local (via Bot Framework Emulator), siga estas etapas:

1. Pré-requisitos

Python 3.8+ instalado.

Bot Framework Emulator instalado.

Acesso aos recursos Azure Language Service e Azure CosmosDB.

2. Configuração de Segurança (Variáveis de Ambiente)

Para proteger suas chaves secretas, o projeto usa um arquivo .env para carregar as variáveis de ambiente.

Crie um arquivo chamado .env na raiz do projeto e insira suas credenciais (não use aspas):

# Arquivo .env
CLU_ENDPOINT=https://seuservico.cognitiveservices.azure.com/
CLU_KEY=SUA_CHAVE_REAL_DO_CLU
CLU_PROJECT_NAME=BibliotecaCLU
CLU_DEPLOYMENT_NAME=Producao

COSMOS_ENDPOINT=https://seudb.documents.azure.com:443/
COSMOS_KEY=SUA_CHAVE_REAL_DO_COSMOS
COSMOS_DATABASE_ID=BibliotecaDB
COSMOS_CONTAINER_ID=Regras
⚠️ Segurança: O arquivo .env está listado no .gitignore e NUNCA deve ser enviado para o GitHub.

3. Instalação de Dependências

Instale todas as bibliotecas necessárias usando o requirements.txt:

pip install -r requirements.txt

4. Execução do Bot

Inicie o servidor do bot:

python app.py

O bot será inicializado e estará escutando na porta 9000.

5. Teste no Emulator

Abra o Bot Framework Emulator.

Clique em "Open Bot" e use o endereço: http://localhost:9000/api/messages.

Teste as intenções, por exemplo: Que horas a biblioteca abre?

🔁 GitHub Actions (Build e CI)

O projeto inclui um fluxo de trabalho de Integração Contínua (CI) que garante que o código está sempre íntegro e que todas as dependências podem ser instaladas em um ambiente de produção.

O workflow build_check.yml é executado em cada push para a branch main, validando o ambiente e a sintaxe do código.
