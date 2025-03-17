# from agno.agent import Agent
# from agno.embedder.google import GeminiEmbedder
# from dotenv import load_dotenv

# load_dotenv()
# from agno.agent import Agent
# from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
# from agno.vectordb.chroma import ChromaDb
# from agno.models.nvidia import Nvidia

# vector_db = ChromaDb(
#     collection="hadith",
#     path="tmp/chromadb",
#     persistent_client=True,
#     embedder=GeminiEmbedder(),
# )
# knowledge_base = PDFUrlKnowledgeBase(
#     urls=[
#         "https://qqeanlpfsgowrbzukhie.supabase.co/storage/v1/object/public/holy//quran-in-modern-english.pdf",
#         "https://qqeanlpfsgowrbzukhie.supabase.co/storage/v1/object/public/holy//en_Sahih_Al-Bukhari.pdf",
#         "https://qqeanlpfsgowrbzukhie.supabase.co/storage/v1/object/public/holy//en_Sahih_Muslim.pdf",
#     ],
#     vector_db=vector_db,
# )

# knowledge_base.load(recreate=True)

# agent = Agent(model=Nvidia(), knowledge=knowledge_base, show_tool_calls=True)
# prompt = "Give me the recipe of any one dish."
# response = agent.run(prompt, markdown=True)
# print(response.content)

# # agent.py - Create this file to integrate your agent with the API

from agno.agent import Agent
from agno.embedder.google import GeminiEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.chroma import ChromaDb
from agno.models.nvidia import Nvidia
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class IslamicKnowledgeAgent:
    """Agent for Islamic knowledge retrieval and Q&A"""

    def __init__(self):
        """Initialize the agent with knowledge base and model"""
        # Create the vector database with Gemini embeddings
        self.vector_db = ChromaDb(
            collection="hadith",
            path="tmp/chromadb",
            persistent_client=True,
            embedder=GeminiEmbedder(),
        )

        # Define your knowledge sources - you would add Islamic PDFs here
        # For example: Quran translations, Hadith collections, Islamic texts
        self.knowledge_base = PDFUrlKnowledgeBase(
            urls=[
                # Add your Islamic knowledge PDFs here
                "https://agno-public.s3.amazonaws.com/quran/quran_english.pdf",
                "https://agno-public.s3.amazonaws.com/hadith/bukhari.pdf",
                # Add more resources as needed
            ],
            vector_db=self.vector_db,
        )

        # Create the agent with NVIDIA model
        self.agent = Agent(
            model=Nvidia(
                api_key="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"
            ),
            knowledge=self.knowledge_base,
            show_tool_calls=True,
        )

        # Initialize the knowledge base (uncomment to reload)
        # This should only be done once or when updating the knowledge base
        # self.knowledge_base.load(recreate=True)

    def answer_question(self, query):
        """Process a user question and return the agent's response"""
        try:
            # Get response from agent
            query = (
                query
                + "Search the knowledge base for the answer, if you dont find it then prepare a solid response."
            )
            response = self.agent.run(query, markdown=True)
            return {"status": "success", "response": response.content}
        except Exception as e:
            print(f"Error in agent processing: {str(e)}")
            return {
                "status": "error",
                "response": f"I encountered an error while processing your question: {str(e)}",
            }


# Singleton instance of the agent
# This ensures we only initialize it once to save resources
_agent_instance = None


def get_agent():
    """Get the singleton agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = IslamicKnowledgeAgent()
    return _agent_instance
