"""
Streamlit frontend for the FCPS Obstetrics & Gynaecology RAG trainer chatbot.

Wraps the original LangChain + OpenRouter + Chroma Cloud chatbot logic in a
styled chat UI, with a sidebar to enter your OpenRouter API key (and Chroma
Cloud credentials) at runtime instead of relying only on a .env file.

Setup:
    pip install streamlit langchain langchain-openai langchain-chroma chromadb python-dotenv

Run:
    streamlit run app.py

You can still keep a .env file with CHROMA_API_KEY / CHROMA_TENANT /
CHROMA_DATABASE / OPENROUTER_API_KEY as defaults -- anything typed into the
sidebar overrides them for the session.
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)

import chromadb
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
COLLECTION_NAME = "fcps_gyn_notes"
CHAT_MODEL = "openai/gpt-4o-mini"
EMBEDDING_MODEL = "openai/text-embedding-3-small"

TOP_K = 5
MAX_DISTANCE = 1.2  # L2 distance cutoff -- lower = more relevant, keep <= this

NO_CONTEXT_MESSAGE = "I don't have enough information in the notes to answer that."

SYSTEM_PROMPT = """You are an FCPS Gynaecology & Obstetrics trainer, teaching a trainee strictly from the provided CONTEXT (their study notes).
Explain concepts the way a trainer would in a teaching session: clearly, in a logical order, breaking down mechanisms, classifications, or steps where relevant, and highlighting key points a trainee would need for exams or clinical practice.
Only use the CONTEXT provided below -- do not bring in outside knowledge, even if you know more about the topic.
If the context does not contain enough information to answer the question, respond exactly with:
"{no_context_message}"
Keep the explanation focused and exam-relevant rather than padded. Cite the section name(s) the material comes from.

CONTEXT:
{context}"""

# ----------------------------------------------------------------------------
# Page setup + styling
# ----------------------------------------------------------------------------

st.set_page_config(
    page_title="FCPS Gynae & Obs Trainer",
    page_icon="\U0001FA7A",
    layout="centered",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

:root {
    --trainer-primary: #6d28d9;
    --trainer-primary-dark: #4c1d95;
    --trainer-accent: #14b8a6;
    --trainer-bg: #f7f5ff;
    --trainer-bubble-bot: #ffffff;
    --trainer-bubble-user: linear-gradient(135deg, #6d28d9 0%, #8b5cf6 100%);
}

.stApp {
    background: radial-gradient(circle at top left, #ede9fe 0%, #f7f5ff 35%, #f0fdfa 100%);
}

/* Hide default streamlit chrome we don't need */
#MainMenu, footer {visibility: hidden;}

/* Header banner */
.trainer-header {
    background: linear-gradient(135deg, var(--trainer-primary) 0%, #8b5cf6 55%, var(--trainer-accent) 100%);
    padding: 28px 30px;
    border-radius: 20px;
    margin-bottom: 22px;
    box-shadow: 0 10px 30px rgba(109, 40, 217, 0.25);
    color: white;
}
.trainer-header h1 {
    font-family: 'Poppins', sans-serif;
    font-size: 1.65rem;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.trainer-header p {
    margin: 6px 0 0 0;
    font-size: 0.92rem;
    opacity: 0.92;
    font-weight: 400;
}
.trainer-badge {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.35);
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    margin-top: 12px;
}

/* Chat bubbles */
.chat-row {
    display: flex;
    margin-bottom: 14px;
    align-items: flex-start;
    gap: 10px;
}
.chat-row.user { flex-direction: row-reverse; }

.avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.05rem;
    flex-shrink: 0;
    box-shadow: 0 2px 6px rgba(0,0,0,0.12);
}
.avatar.bot {
    background: linear-gradient(135deg, var(--trainer-accent), #0d9488);
    color: white;
}
.avatar.user {
    background: linear-gradient(135deg, #6d28d9, #8b5cf6);
    color: white;
}

.bubble {
    max-width: 78%;
    padding: 13px 17px;
    border-radius: 16px;
    font-size: 0.95rem;
    line-height: 1.55;
    box-shadow: 0 3px 10px rgba(76, 29, 149, 0.07);
}
.bubble.bot {
    background: var(--trainer-bubble-bot);
    border: 1px solid #ece7ff;
    color: #2c2140;
    border-top-left-radius: 4px;
}
.bubble.user {
    background: var(--trainer-bubble-user);
    color: white;
    border-top-right-radius: 4px;
}
.bubble.system-note {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    color: #9a3412;
    border-radius: 12px;
}

/* Sidebar tweaks */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2c1a5e 0%, #4c1d95 100%);
}
section[data-testid="stSidebar"] * {
    color: #f3f0ff !important;
}
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stNumberInput input {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.25);
    color: #ffffff !important;
    border-radius: 8px;
}
section[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(135deg, var(--trainer-accent), #0d9488);
    color: white !important;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    width: 100%;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15);
}

/* Chat input */
.stChatInput textarea, div[data-testid="stChatInput"] textarea {
    border-radius: 14px !important;
}

/* Section pill inside bot answers, if the model cites [Section Name] */
.bubble.bot code {
    background: #f0edff;
    color: #5b21b6;
    padding: 1px 6px;
    border-radius: 6px;
    font-size: 0.85em;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="trainer-header">
        <h1>&#129914; FCPS Gynae &amp; Obs Trainer</h1>
        <p>Ask about your FCPS Obstetrics &amp; Gynaecology notes and get a trainer-style, exam-focused explanation &mdash; grounded strictly in your uploaded notes collection.</p>
        <span class="trainer-badge">RAG &middot; Chroma Cloud &middot; OpenRouter</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### \U0001FA7A Session")
    st.caption("Credentials are read from your .env file, exactly like the terminal script.")
    st.markdown("---")
    if st.button("\U0001F5D1\uFE0F Clear chat"):
        st.session_state["messages"] = []
        st.rerun()

# ----------------------------------------------------------------------------
# Chain builder -- reads credentials from the environment, same as the
# original terminal chatbot.py, so behavior matches exactly.
# ----------------------------------------------------------------------------


@st.cache_resource(show_spinner=False)
def build_chain():
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    chroma_api_key = os.getenv("CHROMA_API_KEY")
    chroma_tenant = os.getenv("CHROMA_TENANT")
    chroma_database = os.getenv("CHROMA_DATABASE")

    if not openrouter_key:
        raise EnvironmentError("OPENROUTER_API_KEY not found -- check your .env file.")
    if not (chroma_api_key and chroma_tenant and chroma_database):
        raise EnvironmentError("Chroma Cloud credentials not found -- check your .env file.")

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=openrouter_key,
        openai_api_base=OPENROUTER_BASE_URL,
    )

    chroma_client = chromadb.CloudClient(
        tenant=chroma_tenant,
        database=chroma_database,
        api_key=chroma_api_key,
    )

    vectorstore = Chroma(
        client=chroma_client,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )

    llm = ChatOpenAI(
        model=CHAT_MODEL,
        openai_api_key=openrouter_key,
        openai_api_base=OPENROUTER_BASE_URL,
        temperature=0.2,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ])

    def format_docs(docs):
        if not docs:
            return "NO_RELEVANT_CONTEXT_FOUND"
        parts = []
        for d in docs:
            section = d.metadata.get("section_path", "Unknown section")
            parts.append(f"[{section}]\n{d.page_content}")
        return "\n\n---\n\n".join(parts)

    def get_context_and_question(input_dict):
        question = input_dict["question"]
        results = vectorstore.similarity_search_with_score(question, k=TOP_K)
        relevant = [doc for doc, distance in results if distance <= MAX_DISTANCE]
        return {
            "context": format_docs(relevant),
            "question": question,
            "no_context_message": NO_CONTEXT_MESSAGE,
        }

    chain = (
        RunnablePassthrough()
        | get_context_and_question
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "chain" not in st.session_state:
    st.session_state["chain"] = None
if "connect_error" not in st.session_state:
    st.session_state["connect_error"] = None

if st.session_state["chain"] is None and st.session_state["connect_error"] is None:
    try:
        st.session_state["chain"] = build_chain()
    except Exception as e:
        st.session_state["connect_error"] = str(e)

# ----------------------------------------------------------------------------
# Chat rendering helpers
# ----------------------------------------------------------------------------


def render_message(role, content):
    if role == "user":
        st.markdown(
            f"""
            <div class="chat-row user">
                <div class="avatar user">\U0001F9D1\u200D\U0001F393</div>
                <div class="bubble user">{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="chat-row bot">
                <div class="avatar bot">\U0001FA7A</div>
                <div class="bubble bot">{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ----------------------------------------------------------------------------
# Main chat area
# ----------------------------------------------------------------------------

if st.session_state["chain"] is None:
    st.markdown(
        f"""
        <div class="chat-row bot">
            <div class="avatar bot">\U0001FA7A</div>
            <div class="bubble system-note">
                Could not connect: {st.session_state.get("connect_error", "unknown error")}.
                Check your .env file (OPENROUTER_API_KEY, CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE)
                and restart the app.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    for msg in st.session_state["messages"]:
        render_message(msg["role"], msg["content"])

question = st.chat_input("Ask about a topic from your FCPS Gynae & Obs notes...")

if question:
    st.session_state["messages"].append({"role": "user", "content": question})
    render_message("user", question)

    if st.session_state["chain"] is None:
        answer = "The chatbot isn't connected -- check your .env credentials and restart the app."
    else:
        with st.spinner("Consulting your notes..."):
            try:
                answer = st.session_state["chain"].invoke({"question": question})
            except Exception as e:
                answer = f"Error while generating a response: {e}"

    st.session_state["messages"].append({"role": "assistant", "content": answer})
    render_message("assistant", answer)