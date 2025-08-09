from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
# import requests
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.types import interrupt, Command
import json
load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


@tool
def human_assistance(query: str) -> str:
    """Request assistance from human and provide a human intervention"""
    human_response = interrupt({  # This saves the state in db and kills the graph
        "query": query
    })
    return human_response["data"]


tools = [human_assistance]
llm = init_chat_model(model_provider="openai", model="gpt-4.1-nano")
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    print(response.content)
    return {"messages": [response]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition
)
graph_builder.add_edge("tools", "chatbot")


def compile_graph_with_checkpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)


def main():
    DB_URI = "mongodb://admin:admin@mongodb:27017"
    config = {
        "configurable": {"thread_id": "3"}
    }
    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)

        user_query = input(">")
        state = State(
            messages=[{"role": "user", "content": user_query}]
        )
        for event in graph_with_mongo.stream(state, config=config,
                                             stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()


main()


def admin_call():
    DB_URI = "mongodb://admin:admin@mongodb:27017"
    config = {
        "configurable": {"thread_id": "3"}
    }
    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)

        state = graph_with_mongo.get_state(config=config)
        last_message = state.values['messages'][-1]
        tool_calls = last_message.additional_kwargs.get("tool_calls", [])
        user_query = None
        for call in tool_calls:
            if call.get("function", {}).get("name") == "human_assistance":
                args = call["function"].get("arguments", "{}")
                try:
                    args_dict = json.loads(args)
                    user_query = args_dict.get("query")
                except json.JSONDecodeError:
                    print("Failed to decode function arguments.")

        print("User Has A Query ", user_query)
        solution = input(">")
        resume_command = Command(resume={"data": solution})
        for event in graph_with_mongo.stream(resume_command, config=config, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()


# admin_call()
