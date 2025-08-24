import os
import tempfile
from decouple import config
import psycopg2
from psycopg2 import OperationalError
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.vectorstores.pgvector import PGVector

os.environ['OPENAI_API_KEY'] = config('OPENAI_API_KEY')

CONNECTION_STRING = f"postgresql+psycopg2://{config('PG_USER')}:{config('PG_PASSWORD')}@{config('PG_HOST')}:{config('PG_PORT')}/{config('PG_DBNAME')}"
COLLECTION_NAME = "docs_rag"

embeddings = OpenAIEmbeddings()

def init_db():
    try:
        conn = psycopg2.connect(
            host=config('PG_HOST'),
            port=config('PG_PORT'),
            user=config('PG_USER'),
            password=config('PG_PASSWORD'),
            dbname=config('PG_DBNAME')
        )
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id SERIAL PRIMARY KEY,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except OperationalError as e:
        print("⚠️ Erro ao conectar no banco:", e)


def process_file(file):
    filename = file.name.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as temp_file:
        temp_file.write(file.read())
        temp_file_path = temp_file.name

    if filename.endswith('.pdf'):
        loader = PyPDFLoader(temp_file_path)
    elif filename.endswith(('.doc', '.docx')):
        loader = UnstructuredWordDocumentLoader(temp_file_path)
    else:
        raise ValueError("Formato de arquivo não suportado.")

    docs = loader.load()
    os.remove(temp_file_path)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400)
    chunks = text_splitter.split_documents(docs)
    return chunks


def get_vector_store():
    try:
        return PGVector(
            connection_string=CONNECTION_STRING,
            embedding_function=embeddings,
            collection_name=COLLECTION_NAME,
        )
    except Exception as e:
        print("⚠️ Não foi possível conectar ao PGVector:", e)
        return None  # para não quebrar a interface

def add_to_vector_store(chunks, vector_store):
    if vector_store:
        vector_store.add_documents(chunks)
    return vector_store


def ask_question(model, query, vector_store, messages):
    llm = ChatOpenAI(model=model)

    context = ""
    if vector_store:
        retriever = vector_store.as_retriever()
        docs = retriever.get_relevant_documents(query)
        context = "\n".join([d.page_content for d in docs])

    system_prompt = f"""
        Use apenas o contexto fornecido para responder.
        Se não encontrar informação no contexto, diga claramente que não sabe.
        Responda em markdown.
        Contexto: {context}
        """

    chat_messages = [('system', system_prompt)]
    for msg in messages:
        chat_messages.append((msg['role'], msg['content']))
    chat_messages.append(('human', '{input}'))

    prompt = ChatPromptTemplate.from_messages(chat_messages)

    question_answer_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)

    if vector_store:
        chain = create_retrieval_chain(retriever=vector_store.as_retriever(), combine_docs_chain=question_answer_chain)
        response = chain.invoke({'input': query})
        return response.get('answer')
    else:
        response = question_answer_chain.invoke({'input': query, 'context': context})
        return response.get('output_text', '⚠️ Sem banco ativo, resposta gerada apenas com contexto vazio.')


def save_message_to_db(role, content):
    try:
        conn = psycopg2.connect(
            host=config('PG_HOST'),
            port=config('PG_PORT'),
            user=config('PG_USER'),
            password=config('PG_PASSWORD'),
            dbname=config('PG_DBNAME')
        )
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_history (role, content) VALUES (%s, %s)",
            (role, content)
        )
        conn.commit()
        cur.close()
        conn.close()
    except OperationalError as e:
        print("⚠️ Erro ao salvar mensagem no banco:", e)


def load_messages_from_db():
    try:
        conn = psycopg2.connect(
            host=config('PG_HOST'),
            port=config('PG_PORT'),
            user=config('PG_USER'),
            password=config('PG_PASSWORD'),
            dbname=config('PG_DBNAME')
        )
        cur = conn.cursor()
        cur.execute("SELECT role, content FROM chat_history ORDER BY id")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{'role': row[0], 'content': row[1]} for row in rows]
    except OperationalError as e:
        print("⚠️ Erro ao carregar mensagens do banco:", e)
        return []

    