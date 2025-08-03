from typing_extensions import TypedDict
from typing import Annotated
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()


class ChatContinueResponse(BaseModel):
    is_chat_continue: bool


class State(TypedDict):
    messages: Annotated[list, add_messages]
    latest_query: str
    is_chat_continue: bool


llm = init_chat_model(model_provider="openai", model="gpt-4.1-nano")


def chat_node(state: State):
    response = llm.invoke(state["messages"])
    print("Jarvis -- ", response.content)
    query = input(">")
    state["latest_query"] = query
    state["messages"] = [{"role": "user", "content": query}, response]
    return state


def chat_continue(state: State):
    SYSTEM_PROMPT = """
    You are conversation analyzer and you have to tell that the user is
    trying to continue with the conversation or is trying to end the
    conversation.
    Phases like "bye" or "it was nice taking to you" are the only examples for
    the end of a conversation.
    and you should look for these phases only in a statement for getting to the
    conclusion.
    return with a boolean value the is to continue the chat or to end it.
    If chat needs to be continued the True else False
    """
    lastest_query = state["latest_query"]
    llm.with_structured_output(ChatContinueResponse)
    result = llm.invoke([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": lastest_query}
        ]
    )
    is_chat_continue = result.content
    state["is_chat_continue"] = is_chat_continue
    return state


def router(state: State) -> Literal["chat_node", END]:
    print("routing -- ")
    is_chat_continue = state["is_chat_continue"]
    if str(is_chat_continue).lower() == "true":
        return "chat_node"
    return END


graph_builder = StateGraph(State)
graph_builder.add_node("chat_continue", chat_continue)
graph_builder.add_node("chat_node", chat_node)
graph_builder.add_node("router", router)
graph_builder.add_edge(START, "chat_continue")
graph_builder.add_conditional_edges("chat_continue", router)
graph_builder.add_edge("chat_node", "chat_continue")
graph_builder.add_edge("router", END)

graph = graph_builder.compile()


def main():
    query = input(">")
    graph.invoke({
        "messages": [
            {"role": "user", "content": query}
        ],
        "latest_query": query
    })
    print("Your Chat Is Over Now And The Context Is Gone!")


main()
