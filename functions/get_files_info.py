import os
from openai.types.chat import ChatCompletionToolUnionParam

schema_get_files_info: ChatCompletionToolUnionParam = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": "Lists files in a specified directory relative to the working directory, providing file size and directory status",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "String path of directory to list files from, relative to the working directory (default is the working directory itself)",
                },
            },
        },
    },
}

def resolve_target_dir(working_dir: str, directory: str) -> str:
    working_abs_path = os.path.abspath(working_dir)
    target_path = os.path.normpath(os.path.join(working_abs_path, directory))

    if os.path.commonpath([working_abs_path, target_path]) != working_abs_path:
        raise ValueError( f'Cannot list "{directory}" as it is outside the permitted working directory')
    if not os.path.isdir(target_path):
        raise ValueError(f'"{directory}" is not a directory')
    return target_path

def format_entry(directory: str, file_name: str) -> str:
    file_path = os.path.join(directory, file_name)
    return f"- {file_name}: file_size={os.path.getsize(file_path)} bytes, is_dir={os.path.isdir(file_path)}"


def get_files_info(working_dir: str, directory: str = ".") -> str:
    try:
        # validate path exists and allowed access. return error string if not.
        target_path = resolve_target_dir(working_dir, directory)
        return "\n".join(format_entry(target_path, name) for name in os.listdir(target_path))
    except Exception as e:
        return f"Error: {e}"
    