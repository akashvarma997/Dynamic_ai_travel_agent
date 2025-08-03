# agent/factory.py

from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.hub import pull
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferWindowMemory

# Import your tools from the new 'tools' package
from tools.hotel_search import HotelSearchTool
from tools.web_research import RealTimeRAGTool

# This dictionary will live here, in the 'agent' module
session_agents: Dict[str, AgentExecutor] = {}

def get_session_agent(session_id: str) -> AgentExecutor:
    """Creates a new agent executor for a session if it doesn't exist."""
    if session_id not in session_agents:
        print(f"DEBUG: Creating new agent for session_id: {session_id}")
        
        # Pull the prompt from the hub
        prompt = pull("hwchase17/react-chat")
        
        # Initialize the LLM and Tools
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        tools = [HotelSearchTool(), RealTimeRAGTool()]
        
        # Create the agent
        agent = create_react_agent(llm, tools, prompt)
        
        # Create the memory
        memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", return_messages=True)
        
        # Create the agent executor
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True
        )
        session_agents[session_id] = executor
        
    return session_agents[session_id]