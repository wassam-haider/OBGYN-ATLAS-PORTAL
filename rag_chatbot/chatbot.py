"""
Simple RAG chatbot over the FCPS Gynae notes collection stored in Chroma Cloud.

Uses:
    - LangChain for orchestration
    - OpenRouter as the API gateway for both chat + embeddings
    - GPT-4o-mini as the chat model
    - Chroma Cloud as the vector store
    - similarity_score_threshold retrieval (only returns chunks above a
      relevance threshold -- if nothing qualifies, the bot says so instead
      of guessing from irrelevant context)

No conversation memory yet -- each question is answered independently.

Setup:
    pip install langchain langchain-openai langchain-chroma chromadb python-dotenv

.env file (same as your embedding script) needs:
    CHROMA_API_KEY=...
    CHROMA_TENANT=...
    CHROMA_DATABASE=...
    OPENROUTER_API_KEY=...

Usage:
    python chatbot.py
"""

import os
import sys

from dotenv import load_dotenv
import chromadb
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv(override=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

COLLECTION_NAME = "fcps_gyn_notes"
CHAT_MODEL = "openai/gpt-4o-mini"
EMBEDDING_MODEL = "openai/text-embedding-3-small"

# Retrieval settings
# NOTE: this collection uses Chroma's default L2 (Euclidean) distance, not cosine.
# For L2, LOWER = more similar (0 = identical vectors). We filter manually instead
# of using LangChain's built-in similarity_score_threshold retriever, which assumes
# a cosine-normalized 0-1 score and silently discards everything on an L2 collection.
TOP_K = 5
MAX_DISTANCE = 1.2   # keep only chunks with L2 distance <= this. Tune based on testing:
                      # observed distances for clearly relevant matches were ~0.99-1.09,
                      # so 1.2 gives a little headroom. Lower = stricter, higher = looser.

NO_CONTEXT_MESSAGE = "I don't have enough information in the notes to answer that."

SYSTEM_PROMPT = """You are an FCPS Gynaecology & Obstetrics trainer, teaching a trainee strictly from the provided CONTEXT (their study notes).
Explain concepts the way a trainer would in a teaching session: clearly, in a logical order, breaking down mechanisms, classifications, or steps where relevant, and highlighting key points a trainee would need for exams or clinical practice.
Only use the CONTEXT provided below -- do not bring in outside knowledge, even if you know more about the topic.
If the context does not contain enough information to answer the question, respond exactly with:
"{no_context_message}"
Keep the explanation focused and exam-relevant rather than padded. Cite the section name(s) the material comes from.

CONTEXT:
{context}"""


def build_chain():
    if not OPENROUTER_API_KEY:
        raise EnvironmentError("OPENROUTER_API_KEY not found -- check your .env file.")

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base=OPENROUTER_BASE_URL,
    )

    chroma_client = chromadb.CloudClient(
        tenant=os.getenv("CHROMA_TENANT"),
        database=os.getenv("CHROMA_DATABASE"),
        api_key=os.getenv("CHROMA_API_KEY"),
    )

    vectorstore = Chroma(
        client=chroma_client,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )

    llm = ChatOpenAI(
        model=CHAT_MODEL,
        openai_api_key=OPENROUTER_API_KEY,
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
        # L2 distance: lower = more relevant. Keep only chunks within MAX_DISTANCE.
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


def main():
    print("Building chatbot (connecting to Chroma Cloud + OpenRouter)...")
    chain = build_chain()
    print(f"Ready. Chatting against collection '{COLLECTION_NAME}'. Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            print("Exiting.")
            break

        try:
            answer = chain.invoke({"question": question})
        except Exception as e:
            print(f"Error: {e}")
            continue

        print(f"Bot: {answer}\n")


if __name__ == "__main__":
    main()