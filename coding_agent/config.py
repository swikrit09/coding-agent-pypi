from google.genai.types import GenerateContentConfig, Tool
from .functions.get_files_info import schema_get_files_info
from .functions.get_file_content import schema_get_file_content
from .functions.write_file import schema_write_file
from .functions.run_python_file import schema_run_python_file


system_prompt =  '''
You are a helpful ai coding assistant. 

When user asks a question or make a requst, do function calls to help the user.
You have access to the following functions:
1. get_files_info: Get information about files in a directory.
2. get_file_content: Get the content of a file.
3. write_file: Write content to a file.
4. run_python_file: Run a python file and return the output.

All paths are relative to the working directory.
You do not have to specify the working directory in the function calls as it will automatically be set due to security reasons.
'''


available_functions = Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)


gemini_config = GenerateContentConfig(
    tools=[available_functions],
    system_instruction=system_prompt,
    max_output_tokens=1024,
)

