from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
llm = init_chat_model(model_provider="openai", model="gpt-4.1-nano")


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

grpah = graph_builder.compile()


def main():
    user_query = input(">")
    result = grpah.invoke({
        "messages": [{"role": "user", "content": user_query}]
    })
    print(result)
