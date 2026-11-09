import os
from config import MAX_CHAR_READ
from openai.types.chat import ChatCompletionToolUnionParam

schema_get_file_content: ChatCompletionToolUnionParam = {
    "type": "function",
    "function": {
        "name": "get_file_content",
        "description": "Reads a given file. Returns content truncated to first 10,000 characters.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "File path of file to read, relative to the working directory (default is the working directory itself)",
                },
            },
        },
    },
}

def resolve_target_file(working_dir: str, file_path: str) -> str:
    working_abs_path = os.path.abspath(working_dir)
    target_path = os.path.normpath(os.path.join(working_abs_path, file_path))

    if os.path.commonpath([working_abs_path, target_path]) != working_abs_path:
        raise ValueError(f'Cannot read "{file_path}" as it is outside the permitted working directory')
    if not os.path.isfile(target_path):
        raise ValueError(f'File not found or is not a regular file: "{file_path}"')
    return target_path

def get_file_content(working_dir: str, file_path: str) -> str:
    try:
        target = resolve_target_file(working_dir, file_path)
        file = open(target)
        content = file.read(MAX_CHAR_READ)
        # Try read one more character - if still chars then read was truncated
        if file.read(1):
            content += f'[...File "{file_path}" truncated at {MAX_CHAR_READ} characters]'
        return content
    except Exception as e:
        return f"Error: {e}"