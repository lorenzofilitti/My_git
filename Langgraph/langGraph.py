import os
from langchain_core.tools import tool, Tool, StructuredTool
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import  SystemMessage

from googlesearch import search

os.environ["OPENAI_API_KEY"] = ""
llm = ChatOpenAI(model="gpt-4o-mini")

class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

#------------------------------------------------------------------------


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers.

    Args:
        a: First integer
        b: Second integer

    Returns:
        the product of the two integers
    """
    return a * b

@tool
def g_search(query: str) -> str:

    """
    Performs a web search on the web.
    
    Args:
        a string that will be searched on the web.

    Returns:
        the web search result
    """
    result = search(query, num_results=2, advanced=True)
    for i in result:
        return i



tools = [multiply, g_search]

llm_with_tools = llm.bind_tools(tools)

#------------------------------------------------------------------------

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition)

# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = MemorySaver()

graph = graph_builder.compile(checkpointer=memory)

#------------------------------------------------------------------------

prompt = """ You are an expert assistant. 
You must follow this example as a procedure to build your answer. Use the provided tools if you need them.

Given the user input: who is the current president of the USA?

Thought 1: Do I have the information to answer or do I need additional ones? I need additional information
Action 1: select the appropriate tool and start the web search
Observation 1: A web search is what I need to answer

Thought 1: I must search on the web the current date
Action 1: perform the web search with the provided tool
Observation 1: Currently it's december 2024

Thought 2: I need to look for the latest election results
Action 2: perform the web search with the provided tool 
Observation 2: the winner of the 2024 election is Donald Trump

Result: the current president is Donald Trump

Reply by giving just the final answer you formulated. Don't add the thought process
"""

new_system_message = SystemMessage(content=prompt)


#------------------------------------------------------------------------

config = {"configurable": {"thread_id": "1"}}

user_input = "how do you know the answer?"

graph.update_state(config, {"messages": [new_system_message ]})

# The config is the **second positional argument** to stream() or invoke()!
events = graph.stream(
    {"messages": [("user", user_input)]}, config, stream_mode="values"
)
for event in events:
    event["messages"][-1].pretty_print()