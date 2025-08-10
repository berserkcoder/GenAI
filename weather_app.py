from dotenv import load_dotenv
from openai import OpenAI
import json
import requests
import os

load_dotenv()

client = OpenAI(
    api_key="AIzaSyC0CXoXPpCYmFZGO_p4iw6Vo5cRb29ituQ",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def run_command(command):
    result = os.system(command=command)
    return result

def get_weather(city : str):
    print("^ Tool Called: get_weather", city)
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"
    return "Something went wrong"

available_tools = {
    "get_weather":{
        "fn" : get_weather,
        "description" : "Takes a city name as an input and returns the current weather for the city"
    },
    "run_command" : {
        "fn" : run_command,
        "description" : "Takes a command as an input and runs it in the terminal"
    }
}

# system_prompt = f"""
#     You are an helpful AI Assistant who is specialized in resolving user query.
#     You work on start,plan,action,observe mode.
#     If user ask for multiply things in one query then u will solve them one by one and not all together.
#     If user writes a query in which u have to call a single tool twice you must do it for one time only.
#     For the given user query and available tools,plan the step by step execution, bosed on the planning,
#     Select the relevant tool from the available tool. And based on the tool selection you perform an action to calculate.
#     Wait for the observation and based on the observation from the tool call resolve the user query.

#     Rules:
#     1. Follow the strict JSON output as per Output schema.
#     2. Always perform one step at a time and wait for next input
#     3. Carefully analyse the user query

#     Output JSON Format :
#     {{
#         "step" : "string",
#         "content" : "string",
#         "function" : "The name of the function if the step is action",
#         "input" : "The input parameter for the function",
#     }}

#     Available Tools:
#     - get_weather: Takes a city name as an input and returns the current weather for the city
#     - run_command: Takes a command as an input and runs it in the terminal

#     Example:
#     User Query : What is the weather of NewYork?
#     Output: {{ "step":"plan", "content" : "The user is interested in weather data of NewYork"}} 
#     Output: {{ "step":"plan", "content" : "From the available tools i should call the get_weather"}} 
#     Output: {{ "step":"action", "function" : "get_weather","input":"NewYork"}} 
#     Output: {{ "step":"observe", "output" : "12 degree celcius"}} 
#     Output: {{ "step":"output", "content" : "The weather of newyork is 12 degrees."}} 

#     Example:
#      User Query : What is the weather of NewYork and London?
#     Output: {{ "step":"plan", "content" : "The user is interested in weather data of NewYork and London"}} 
#     Output: {{ "step":"plan", "content" : "From the available tools i should call the get_weather for each city separately"}} 
#     Output: {{ "step":"plan", "content" : "I will call the get_weather for NewYork first"}}
#     Output: {{ "step":"action", "function" : "get_weather","input":"NewYork"}} 
#     Output: {{ "step":"observe", "output" : "20 degree celcius"}} 
#     Output: {{ "step":"output", "content" : "The weather of NewYork is 20 degrees."}} 
#     Output: {{ "step":"plan", "content" : "I will call the get_weather for London"}}
#     Output: {{ "step":"action", "function" : "get_weather","input":"London"}} 
#     Output: {{ "step":"observe", "output" : "12 degree celcius"}} 
#     Output: {{ "step":"output", "content" : "The weather of London is 12 degrees."}} 
# """

system_prompt = f"""
    You are an helpfull AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.
    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    - get_weather: Takes a city name as an input and returns the current weather for the city
    - run_command: Takes a command as input to execute on system and returns ouput
    
    Example:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}
"""

messages = [
    {"role": "system","content" : system_prompt }
]

while True:
    user_query = input('> ')
    
    if(user_query == "bye") :
        print(f"bot : bye! Have a nice day")
        break

    messages.append({"role" : "user" , "content" : user_query})

    while True:
        response = client.chat.completions.create(
            model = "gemini-2.0-flash-lite",
            response_format={"type" : "json_object"},
            messages= messages
        )

        parsed_output = json.loads(response.choices[0].message.content)
        messages.append({"role" : "assistant" , "content" : json.dumps(parsed_output)})

        if parsed_output.get("step") == "plan":
            print(f"brain : {parsed_output.get("content")}")
            continue

        if parsed_output.get("step") == "action":
            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")

            if available_tools.get(tool_name,False) != False:
                output = available_tools[tool_name].get("fn")(tool_input)
                messages.append({"role" : "assistant" , "content" : json.dumps({"step" : "observe", "output" : output})})
                continue
                
        if parsed_output.get("step") == "output":
            print(f"bot : {parsed_output.get("content")}")
            break
