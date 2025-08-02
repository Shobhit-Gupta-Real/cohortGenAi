from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()


client = OpenAI()


class ClassifyMessageResponse(BaseModel):
    is_coding_question: bool


class State(TypedDict):
    user_query: str
    llm_result: str | None
    # accuracy_percentage: str | None
    # is_coding_question: bool | None


def classify_message(state: State):
    query = state["user_query"]
    SYSTEM_PROMPT = """
    You are an AI Assistant. Your job is to detect if the user's query is
    related to coding question or not.
    Return the response in specified JSON boolean only."""

    response = client.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=ClassifyMessageResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
    )
    is_coding_question = response.choices[0].message.parsed.is_coding_question
    state["llm_result"] = is_coding_question
    return state


graph_builder = StateGraph(State)
graph_builder.add_node("classify_message", classify_message)
graph_builder.add_edge(START, "classify_message")
graph_builder.add_edge("classify_message", END)

graph = graph_builder.compile()


def main():
    user = input(">")
    state = {
        "user_query": user,
        "llm_result": None
    }
    graph_result = graph.invoke(state)
    print("graph result: ", graph_result)


main()
