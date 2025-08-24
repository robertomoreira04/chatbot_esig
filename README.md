🤖 Chatbot RAG com LangChain, OpenAI e PostgreSQL (PGVector)

Este projeto implementa um chatbot de IA utilizando LangChain, OpenAI, Streamlit e PostgreSQL com PGVector.
Ele permite fazer upload de documentos (PDF, Word), extrair o conteúdo, criar embeddings e armazenar em um banco de dados vetorial para consultas posteriores.
Além disso, mantém o histórico de conversas no banco, permitindo retomar diálogos mesmo após reiniciar a aplicação.

🚀 Tecnologias Utilizadas

Python
Streamlit - Interface do chatbot
Langchain - Orquestração do RAG
OpenAI API - Seleção de algum modelo de linguagem (GPT-3.5, GPT-4, GPT-4o, etc.)
PostgreSQL e PGVector - Banco de dados vetorial

⚙️ Configuração do Ambiente

Antes de rodar o projeto, é necessário criar um ambiente virtual (venv) e instalar as dependências.

# LINUX / MAC OS

# Criar venv
python3 -m venv venv

# Ativar venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# WINDOWS

# Criar venv
python -m venv venv

# Ativar venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

🔑 Variáveis de Ambiente

Crie um arquivo .env na raiz do projeto com as seguintes variáveis:

OPENAI_API_KEY=your_openai_api_key

PG_HOST=host
PG_PORT=porta
PG_USER=seu_usuario
PG_PASSWORD=sua_senha
PG_DBNAME=seu_banco

▶️ Executando a Aplicação

Com o ambiente virtual ativado:

streamlit run interface.py

📂 Funcionalidades

- Upload de PDFs e Word para indexação.
- RAG (Retrieval-Augmented Generation) com PGVector.
- Persistência de histórico de conversas no PostgreSQL.
- Suporte a múltiplos modelos da OpenAI (GPT-3.5, GPT-4, GPT-4o, etc.).

