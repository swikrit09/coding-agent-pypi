import os
from coding_agent.constants import MAX_CHARS
from google.genai import types

def get_file_content(working_directory, file_path):
    absolute_working_dir = os.path.abspath(working_directory)
    absolute_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not absolute_file_path.startswith(absolute_working_dir):
        return f"Error: The file {absolute_file_path} is outside the working directory {absolute_working_dir}."
    
    if not os.path.isfile(absolute_file_path):
        return f"Error: The path {absolute_file_path} is not a valid file."
    
    file_content_string = ""
    try:
        with open(absolute_file_path, 'r') as file:
            file_content_string += file.read(MAX_CHARS) 
            truncate_value = MAX_CHARS - 20
            if len(file_content_string) >= truncate_value:
                file_content_string+=f"\n...FILE {file_path} TRUNCATED after {truncate_value} characters..."
        return file_content_string
    
    except Exception as e:
        return f"Error reading file {absolute_file_path}: {str(e)}"
    
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Get the content of a file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type= types.Type.STRING,
                description= "The path to the file, relative to the working directory.",
            ),
        },
        required=["file_path"]
    )
)
    