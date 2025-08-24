import streamlit as st
from functions import (
    process_file,
    get_vector_store,
    add_to_vector_store,
    ask_question,
    save_message_to_db,
    load_messages_from_db,
    init_db,
)

init_db()  

st.set_page_config(page_title='Chatbot de IA', page_icon='./esig.ico')
st.header('🤖 Bem-vindo ao Chatbot ESIG')

if 'messages' not in st.session_state:

    st.session_state['messages'] = load_messages_from_db()

if 'vector_store' not in st.session_state:

    st.session_state['vector_store'] = get_vector_store()

with st.sidebar:
    st.header('📂 Upload de Arquivos')
    uploaded_files = st.file_uploader(
        label='Faça o upload do seu arquivo',
        type=['pdf', 'doc', 'docx'],  
        accept_multiple_files=True
    )

    if uploaded_files:
        with st.spinner('Processando arquivo(s)...'):
            all_chunks = []
            for uploaded_file in uploaded_files:
                chunks = process_file(uploaded_file)
                all_chunks.extend(chunks)
            st.session_state['vector_store'] = add_to_vector_store(all_chunks, st.session_state['vector_store'])
            st.success(f'{len(uploaded_files)} arquivo(s) processado(s) e adicionado(s)! ✅')

    model_options = [
        'gpt-3.5-turbo',
        'gpt-4',
        'gpt-4-turbo',
        'gpt-4o-mini',
        'gpt-4o'
    ]
    selected_model = st.selectbox('Selecione o modelo LLM', model_options)

question = st.chat_input('Digite sua pergunta...')

for msg in st.session_state.messages:
    st.chat_message(msg['role']).write(msg['content'])

if question:
    st.chat_message('user').write(question)
    st.session_state.messages.append({'role': 'user', 'content': question})
    save_message_to_db('user', question)

    with st.spinner('Buscando resposta...'):
        response = ask_question(
            model=selected_model,
            query=question,
            vector_store=st.session_state['vector_store'],
            messages=st.session_state.messages
        )
        st.chat_message('ai').write(response)
        st.session_state.messages.append({'role': 'ai', 'content': response})
        save_message_to_db('ai', response)

