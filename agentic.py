# from agno.agent import Agent
# from agno.embedder.google import GeminiEmbedder
# from dotenv import load_dotenv
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.team import Team

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
#     urls=[],
#     vector_db=vector_db,
# )

# # knowledge_base.load(recreate=True)

# researcher = Agent(
#     name="Searcher",
#     model=Nvidia(),
#     role="Searches the top URLs for a topic",
#     instructions=[
#         "Given a topic, first generate a list of 3 search terms related to that topic.",
#         "For each search term, search the web and analyze the results. Return the 5 most relevant URLs to the topic.",
#     ],
#     tools=[DuckDuckGoTools()],
#     add_datetime_to_instructions=True,
# )

# writer = Agent(
#     name="Writer",
#     model=Nvidia(),
#     role="Writes a high-quality article or response",
#     description=(
#         "You are a senior scholar for Muslims. Given a topic and a list of URLs, "
#         "your goal is to write a high-quality response to answer the query with all the proper and needed sources."
#     ),
#     instructions=[
#         "First read all urls using `read_article`."
#         "Then write a high-quality response to answer the query.",
#         "The response should be well-structured, informative, engaging and catchy.",
#         "Ensure the response is well-researched and backed by credible sources.",
#         "Ensure you provide a nuanced and balanced opinion, quoting facts where possible.",
#         "Focus on clarity, coherence, and overall quality.",
#         "Never make up facts. Always provide proper attribution.",
#         "Remember: you are writing as an Islamic scholar and many people depend on your sermon, so the quality of the article is important.",
#     ],
#     tools=[Newspaper4kTools()],
#     add_datetime_to_instructions=True,
# )

# knowledgdeScholar = Agent(
#     name="Islamic Scholar",
#     model=Nvidia(),
#     knowledge=knowledge_base,
#     role="Writes a high-quality article or response",
#     description=(
#         "You are a senior scholar for Muslims that has all the knowlegde about the authentic books."
#         "your goal is to search your knowledge base of the authentic texts and provide the answer to the query with proper citation."
#     ),
#     instructions=[
#         "First search for the query in your knowledge base.",
#         "Then write a high-quality response to answer the query.",
#         "The response should be well-structured, informative, engaging and catchy.",
#         "Ensure the response is well-researched and backed by credible sources.",
#         "Ensure you provide a nuanced and balanced opinion, quoting facts where possible.",
#         "Focus on clarity, coherence, and overall quality.",
#         "Never make up facts. Always provide proper attribution.",
#         "Remember: you are writing as an Islamic scholar and many people depend on your sermon, so the quality of the article is important.",
#     ],
#     add_datetime_to_instructions=True,
# )

# editor = Team(
#     name="Editor",
#     mode="coordinate",
#     model=Nvidia(),
#     members=[researcher, writer],
#     description="You are a senior Ullema. Given a topic, your goal is to write a high-quality article or response for the masses.",
#     instructions=[
#         "First ask the researcher to search for the most relevant URLs for that topic.",
#         "Then ask the writer to get an engaging response from the URLs.",
#         "Ask the knowledgebase scholar to provide the answer from the authentic texts.",
#         "Edit, proofread, and refine the article to ensure it meets the high standards of the Islamic community.",
#         "The article should be extremely articulate and well written. "
#         "Focus on clarity, coherence, and overall quality.",
#         "Do not provide any not needed information, just the answer to the query.",
#         "Remember: you are the final gatekeeper before the response is shown to the public, so make sure the article is perfect.",
#     ],
#     add_datetime_to_instructions=True,
#     # send_team_context_to_members=True,
#     markdown=True,
#     show_members_responses=True,
# )
# # finalAgent = Agent(
# #     model=Nvidia(),
# #     knowledge=knowledge_base,
# #     read_chat_history=True,
# #     show_tool_calls=True,
# # )
# prompt = "How can a muslim clean themselves in the absence of water?"
# response = editor.run(prompt, markdown=True)
# print(response.content)
# # editor.print_response(prompt)

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
        self.researcher = Agent(
            name="Searcher",
            model=Nvidia(),
            role="Searches the top URLs for a topic",
            instructions=[
                "Given a topic, first generate a list of 3 search terms related to that topic.",
                "For each search term, search the web and analyze the results. Return the 5 most relevant URLs to the topic.",
            ],
            tools=[DuckDuckGoTools(fixed_max_results=5)],
            add_datetime_to_instructions=True,
        )

        self.writer = Agent(
            name="Writer",
            model=Nvidia(),
            role="Writes a high-quality article or response",
            description=(
                "You are a senior scholar for Muslims. Given a topic and a list of URLs, "
                "your goal is to write a high-quality response to answer the query with all the proper and needed sources."
            ),
            instructions=[
                "First read all urls using `read_article`."
                "Then write a high-quality response to answer the query.",
                "The response should be well-structured, informative, engaging and catchy.",
                "Ensure the response is well-researched and backed by credible sources.",
                "Ensure you provide a nuanced and balanced opinion, quoting facts where possible.",
                "Focus on clarity, coherence, and overall quality.",
                "Never make up facts. Always provide proper attribution.",
                "Remember: you are writing as an Islamic scholar and many people depend on your sermon, so the quality of the article is important.",
            ],
            tools=[Newspaper4kTools()],
            add_datetime_to_instructions=True,
        )

        self.knowledgdeScholar = Agent(
            name="Islamic Scholar",
            model=Nvidia(),
            knowledge=self.knowledge_base,
            role="Writes a high-quality article or response",
            description=(
                "You are a senior scholar for Muslims that has all the knowlegde about the authentic books."
                "your goal is to search your knowledge base of the authentic texts and provide the answer to the query with proper citation."
            ),
            instructions=[
                "First search for the query in your knowledge base.",
                "Then write a high-quality response to answer the query.",
                "The response should be well-structured, informative, engaging and catchy.",
                "Ensure the response is well-researched and backed by credible sources.",
                "Ensure you provide a nuanced and balanced opinion, quoting facts where possible.",
                "Focus on clarity, coherence, and overall quality.",
                "Never make up facts. Always provide proper attribution.",
                "Remember: you are writing as an Islamic scholar and many people depend on your sermon, so the quality of the article is important.",
            ],
            add_datetime_to_instructions=True,
        )

        self.editor = Team(
            name="Editor",
            mode="coordinate",
            model=Nvidia(),
            members=[self.researcher, self.writer, self.knowledgdeScholar],
            description="You are a senior Ullema. Given a topic, your goal is to write a high-quality article or response for the masses.",
            instructions=[
                "First ask the researcher to search for the most relevant URLs for that topic.",
                "Then ask the writer to get an engaging response from the URLs.",
                "Ask the knowledgebase scholar to provide the answer from the authentic texts.",
                "Edit, proofread, and refine the article to ensure it meets the high standards of the Islamic community.",
                "The article should be extremely articulate and well written. "
                "Focus on clarity, coherence, and overall quality.",
                "Do not provide any not needed information, just the answer to the query.",
                "Remember: you are the final gatekeeper before the response is shown to the public, so make sure the article is perfect.",
            ],
            add_datetime_to_instructions=True,
            # send_team_context_to_members=True,
            markdown=True,
            show_members_responses=True,
        )

    #         # Initialize the knowledge base (uncomment to reload)
    #         # This should only be done once or when updating the knowledge base
    #         # self.knowledge_base.load(recreate=True)

    def answer_question(self, query):
        """Process a user question and return the agent's response"""
        try:
            # Get response from agent
            query = (
                query
                + "Search the knowledge base for the answer, if you dont find it then prepare a solid response."
            )
            response = self.editor.run(query, markdown=True)
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
