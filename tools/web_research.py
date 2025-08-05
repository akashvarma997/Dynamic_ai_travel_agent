# tools/web_research.py

from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

class RealTimeRAGInput(BaseModel):
    query: str = Field(description="The question or topic to research on the web.")

class RealTimeRAGTool(BaseTool):
    name: str = "real_time_web_research"
    description: str = "Use this for subjective or knowledge-based questions that need up-to-date information from the web. The input must be a JSON object with a 'query' key."
    args_schema: type[BaseModel] = RealTimeRAGInput

    def _run(self, query: str) -> str:
        print(f"DEBUG: Performing RAG for query: {query}")
        try:
            # 1. Search, 2. Load, 3. Split, 4. Embed & Store, 5. Synthesize
            tavily_tool = TavilySearchResults(max_results=4)
            search_results = tavily_tool.invoke({"query": query})
            urls = [res['url'] for res in search_results]

            loader = WebBaseLoader(urls)
            docs = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)

            vectorstore = FAISS.from_documents(documents=splits, embedding=OpenAIEmbeddings())
            retriever = vectorstore.as_retriever()

            system_prompt = (
                '''You are an expert Q&A assistant that is designed to answer questions based on a given context.

                Your instructions are:
                1.  **Prioritize the Context:** First, carefully analyze the provided `Context` to find the answer. Your primary goal is to synthesize an answer exclusively from this text.
                2.  **Synthesize and Combine:** If the context contains relevant information but doesn't form a complete answer, you may supplement it with your own general knowledge to create a comprehensive response.
                3.  **Be Transparent:** When you use your general knowledge to supplement the context, you must explicitly state it. For example, say "According to the provided documents..." and then "To provide more detail..."
                4.  **Handle Irrelevant Context:** If the provided `Context` is not at all relevant to the question, state that the documents do not contain the answer, and then proceed to answer the question using your own knowledge.
                5.  **Cite Your Sources:** When you use information from the context, add a citation like `` at the end of the relevant sentence.
                6.  **If You Truly Don't Know:** If the question is about a topic you have no information on (neither in the context nor in your general knowledge), then it is appropriate to say that you don't know.
                
                below is the context:
                {context}
                '''
            )
            qa_prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{input}")])
            llm_qa = ChatOpenAI(model="gpt-4o", temperature=0)
            Youtube_chain = create_stuff_documents_chain(llm_qa, qa_prompt)
            rag_chain = create_retrieval_chain(retriever, Youtube_chain)

            response = rag_chain.invoke({"input": query})
            return response["answer"]
        except Exception as e:
            print(f"Error during RAG: {e}")
            return "An error occurred during web research."

    async def _arun(self, query: str) -> str:
        return self._run(query)