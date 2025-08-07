from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import requests
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
load_dotenv()
llm = init_chat_model(model_provider="openai", model="gpt-4.1-nano")


@tool()  # here we have given to decorator of the tool to our tool function
def get_weather(city: str):
    """This tool returns the weater data about the give city."""
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather is {city} is {response.text}"
    return "Something went wrong"


tools_available = [get_weather]
llm_with_tools = llm.bind_tools(tools_available)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    print(response.content)
    return {"messages": [response]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

grpah = graph_builder.compile()


def main():
    user_query = input(">")
    grpah.invoke({
        "messages": [{"role": "user", "content": user_query}]
    })


main()
