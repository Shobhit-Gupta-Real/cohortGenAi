from dotenv import load_dotenv
from openai import OpenAI
from json import dumps

load_dotenv()
client = OpenAI()

def get_weather(location: str):
    return "42 degree celsius" 

SYSTEM_PROMPT = f"""
You are a helpful assistant who is specialized in resolving user queries.
You work on start, plan, action and observe mode.
For the given user query and the given tools, plan step by step execution, and based on the plan,
select the relevent tool from the avaible tools, and based on the tool selection you perform the action to call the tool.

wait for the observation and based on the observation, you resolve the user query.

Rules:
- Follow the output JSON format strictly.
- Always perform one step at a time.
- carefully analyze the user query and the available tools.

Output JSON format:
{{
    "step": "plan" | "action" | "observe" | "output",
    "content": "your content here" | "the observation here",
    "function": "function_name" if the step is "action" else null,
    "input": "input to the function" | null
}}

Available tools:
- "get_weather(location: str)": Get the weather for a given location.

Example user query:
"What's the weather like in New York?"
 Output: {{"step": "plan", "content": "the user is interested in the weather data of new york"}}
 Output: {{"step": "plan", "content": "from available tools, i should get the get_weather('') tool to get the weather data"}}
 Output: {{"step": "action", "function": "get_weather(''), "input": "New York"}}
 Output: {{"step": "observe", "content": "42 degree celsius"}}
 Output: {{"step": "output", "content": "The weather in New York is 42 degree celsius"}}   
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={
        "type": "json_object"
    },
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": "What's the weather like in New York?"
        },
        {
            "role": "assistant",
            "content": dumps({
                "step": "plan",
                "content": "the user is interested in the weather data of new york",
                "function": None,
                "input": None
            })
        },
        {
            "role": "assistant",
            "content": dumps({
                "step": "plan",
                "content": "from available tools, i should get the get_weather('New York') tool to get the weather data",
                "function": None,
                "input": None
            })
        },
        {
            "role": "assistant",
            "content": dumps({
                "step": "action",
                "function": "get_weather",
                "input": "New York"
            })
        },
        {
            "role": "user",
            "content": dumps({
                "step": "observe",
                "content": "-10 degree celsius"
            })
        }
    ]
)

print(response.choices[0].message.content)  # Output the final response from the assistant