from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough


DB_DIR = "chroma_db"

RAG_TEMPLATE = """
You are a customer support assistant for ShopEase, an e-commerce store.
Use the FAQ context below to answer the user's question helpfully and confidently.

FAQ Context:
{context}

User Question:
{question}

If the context partially answers the question, use your judgment to fill in natural details
(e.g., return steps, refund timelines, or policy summaries).
If the question clearly relates to returns, refunds, or orders, give a full helpful answer.
Never say "I'm not sure based on our policy." Instead, say "Based on our return policy..." or similar.
"""

class RagService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectordb = Chroma(persist_directory=DB_DIR, embedding_function=self.embeddings)
        self.retriever = self.vectordb.as_retriever(search_kwargs={"k": 4})
        self.prompt = PromptTemplate.from_template(RAG_TEMPLATE)

    def make_chain(self, llm):
        def format_docs(docs):
            return "\n\n".join([d.page_content for d in docs])

        retrieval = RunnableParallel({
            "context": self.retriever | format_docs,
            "question": RunnablePassthrough(),
        })
        return retrieval | self.prompt | llm | StrOutputParser()
