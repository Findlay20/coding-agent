import os
from openai.types.chat import ChatCompletionToolUnionParam

schema_write_file: ChatCompletionToolUnionParam = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write to the specified file. Replaces existing text",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "File path of file to write content to, relative to the working directory (default is the working directory itself)",
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the specified file",
                },
            },
        },
    },
}

def resolve_target_file(working_dir: str, file_path: str) -> str:
    working_abs_path = os.path.abspath(working_dir)
    target_path = os.path.normpath(os.path.join(working_abs_path, file_path))

    if os.path.commonpath([working_abs_path, target_path]) != working_abs_path:
        raise ValueError(f'Cannot write to "{file_path}" as it is outside the permitted working directory')
    if os.path.isdir(target_path):
        raise ValueError(f'Cannot write to "{file_path}" as it is a directory')
    return target_path

def write_file(working_dir: str, file_path: str, content: str) -> str:
    try:
        target = resolve_target_file(working_dir, file_path)

        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, mode="w") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f"Error: {e}"