from typing import Any, Dict
from google.genai import types
import os

from .get_file_content import get_file_content
from .write_file import write_file
from .get_files_info import get_files_info
from .run_python_file import run_python_file


def call_function(function_name: str, arguments: Dict[str, Any], work_dir_path: str ,verbose: bool = False) -> types.Part:
    """
    Dispatch Gemini function calls and return a single Part(function_response=...).
    The main loop is responsible for wrapping multiple Parts into one Content(role="tool").
    """
    if verbose:
        print(f"Calling function: {function_name} with arguments: {arguments}")

    try:
        if function_name == "get_file_content":
            result = get_file_content(work_dir_path, **arguments)
        elif function_name == "write_file":
            result = write_file(work_dir_path, **arguments)
        elif function_name == "get_files_info":
            result = get_files_info(work_dir_path, **arguments)
        elif function_name == "run_python_file":
            result = run_python_file(work_dir_path, **arguments)
        else:
            return types.Part(
                function_response=types.FunctionResponse(
                    name=function_name,
                    response={"error": f"Function {function_name} not recognized."},
                )
            )

        # Always wrap under "Result" for consistency
        if not isinstance(result, dict):
            payload = {"Result": result}
        else:
            payload = {"Result": result}

        return types.Part(
            function_response=types.FunctionResponse(
                name=function_name,
                response=payload,
            )
        )

    except Exception as e:
        return types.Part(
            function_response=types.FunctionResponse(
                name=function_name,
                response={"error": str(e)},
            )
        )
