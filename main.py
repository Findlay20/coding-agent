import os
from dotenv import load_dotenv
import argparse
import json
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageParam, ChatCompletion, ChatCompletionMessageToolCallUnion
from prompts import system_prompt
from call_function import available_functions, call_function

# Setup variables and argument parser

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")

if (api_key is None):
    raise RuntimeError("OPENROUTER_API_KEY is not set")

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()


# Create OpenAI Client

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

verbose = args.verbose
user_prompt = args.user_prompt
if (verbose):
    print(f"User prompt: {user_prompt}")

messages: list[ChatCompletionMessageParam] = [
    { "role": "system", "content": system_prompt },
    { "role": "user", "content": user_prompt },
]

def send_messages(messages: list[ChatCompletionMessageParam]) -> ChatCompletion: 
    return client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        tools=available_functions
    )

# Handles tool calls and appends results to messages array
def handle_tool_calls(tool_calls: list[ChatCompletionMessageToolCallUnion] | None ) -> None:
    if not tool_calls:
        return
    for tool_call in tool_calls:
            if (tool_call.type != "function"):
                continue
            function_args = json.loads(tool_call.function.arguments or "{}")
            result = call_function(tool_call, verbose)
            if not "content" in result:
                raise Exception("content missing from tool call response")
            if verbose:
                print(f"-> {result['content']}")
            messages.append(result)

def main():
    for _ in range(20):
        response = send_messages(messages)

        # if verbose:
        #     print(f"messages: {messages}")

        message = response.choices[0].message;
        messages.append(message)

        if message.tool_calls:
            handle_tool_calls(message.tool_calls)
        else:       
            # prints
            usage = response.usage
            if usage is None:
                raise RuntimeError("Failed response. Returned usage is None")
            if (verbose):
                print(f"Prompt tokens: {usage.prompt_tokens}")
                print(f"Response tokens: {usage.completion_tokens}")

            if message.content:
                print(message.content)
            
            return 0;
    print(f"Error: Maximum iterations hit before output generated. Too many tool calls")
    return 1;

main()