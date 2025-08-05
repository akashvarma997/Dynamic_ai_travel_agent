# agent/factory.py

from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.hub import pull
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferWindowMemory
from datetime import date
from langchain.prompts import PromptTemplate

from tools.hotel_search import HotelSearchTool
from tools.web_research import RealTimeRAGTool

# This dictionary will live here, in the 'agent' module
session_agents: Dict[str, AgentExecutor] = {}

def get_session_agent(session_id: str) -> AgentExecutor:
    """Creates a new agent executor for a session if it doesn't exist."""
    current_date = date.today()
    if session_id not in session_agents:
        print(f"DEBUG: Creating new agent for session_id: {session_id}")
        
        # Pull the prompt from the hub
        prompt = pull("hwchase17/react-chat")
        prompt_template_new = """
        You are a smart, and adaptable AI Travel Agent. Your goal is to provide helpful, up-to-date travel recommendations.

        The current date is {current_date}. Always use this to understand time-related queries.

        **Date Interpretation Rules:**
        - When a user gives a vague date reference, interpret it logically. For example, "mid-November" implies a check-in date between November 10th and 20th.
        - If the user does not specify the duration of the trip, assume a default of 3 days.
        - If a user provides a date that is in the past, you must ask for a future date or suggest one two days from the current date.

        **Tool Usage Rules:**
        - Your primary tool for research (itineraries, recommendations) is the real_time_web_research. You MUST use it first to gather up-to-date information.
        - After providing an itinerary, proactively suggest relevant accommodations using the hotel search tool.

        TOOLS:
        ------

        Assistant has access to the following tools:

        {tools}

        To use a tool, please use the following format:

        Thought: Do I need to use a tool? Yes
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action

        When you have gathered all the information required for the user's request, you MUST use the format below. Do not just output the raw results from a tool. Synthesize all the gathered information into a single, comprehensive, and friendly response for the user.
        Thought: Do I need to use a tool? No
        Final Answer: [your response here]

        Note: When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format below. Do not just output the raw results from a tool. Synthesize all the gathered information into a single, comprehensive, and friendly response for the user.

        Thought: Do I need to use a tool? No
        Final Answer: [your final, comprehensive response here]

        **Final Answer Structure:**
        When you provide your `Final Answer`, you must structure your response in the following order:
        1.  **Itinerary and Recommendations:** First, present the detailed itinerary or recommendations you found using the web search tool.
        2.  **Accommodation Suggestions:** After the itinerary, add a clear section titled "Hotel Suggestions" and list the relevant hotels you found. Make the response conversational and helpful.

        **--- END OF NEW INSTRUCTION ---**

        Previous conversation history:
        {chat_history}

        New input: {input}
        {agent_scratchpad}

        """
        prompt_template = PromptTemplate.from_template(prompt_template_new)

        current_date_str = date.today().strftime("%A, %B %d, %Y")

        # 4. Injecting the date into the template
        prompt_with_date = prompt_template.partial(current_date=current_date_str)
        
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        tools = [HotelSearchTool(), RealTimeRAGTool()]
        
        agent = create_react_agent(llm, tools, prompt_with_date)
        
        memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", return_messages=True)
        
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True
        )
        session_agents[session_id] = executor
        
    return session_agents[session_id]