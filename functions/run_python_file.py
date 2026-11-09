import os
import subprocess
from openai.types.chat import ChatCompletionToolUnionParam

schema_run_python_file: ChatCompletionToolUnionParam = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Run a specified python file. Returns process' return code and stderr and stdout, if exists.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "File path of python file to run, relative to the working directory (default is the working directory itself)",
                },
                "args": {
                    "type": "array",
                    "items": {
                        "type": "str", 
                    },
                    "description": "List of arguments to call the given python function with",
                },
            },
        },
    },
}

def resolve_target_file(working_dir: str, file_path: str) -> str:
    working_abs_path = os.path.abspath(working_dir)
    target_path = os.path.normpath(os.path.join(working_abs_path, file_path))

    if os.path.commonpath([working_abs_path, target_path]) != working_abs_path:
        raise ValueError(f'Cannot execute "{file_path}" as it is outside the permitted working directory')
    if not os.path.isfile(target_path):
        raise ValueError(f'"{file_path}" does not exist or is not a regular file')
    if target_path[-3:] != ".py":
        raise ValueError(f'Error: "{file_path}" is not a Python file')
    return target_path


def run_python_file(
    working_dir: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        target = resolve_target_file(working_dir, file_path)
        command = ["python", target]
        if args:
            command.extend(args)

        result = subprocess.run(command, capture_output=True, cwd=working_dir, text=True, timeout=30)
        output = ""
        if result.returncode:
            output += "Process exited with code X"
        if not result.stderr and not result.stdout:
            output += "No output produced"
        if result.stdout:
            output += f"STDOUT: {result.stdout}"
        if result.stderr:
            output += f"STDERR: {result.stderr}"
    
        return output
    except Exception as e:
        return f"Error: executing Python file: {e}"
    