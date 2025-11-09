import os
from google.genai import types

def write_file(working_directory, file_path, content):

    absolute_working_dir = os.path.abspath(working_directory)
    absolute_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not absolute_file_path.startswith(absolute_working_dir):
        return f"Error: The file {absolute_file_path} is outside the working directory {absolute_working_dir}."
    
    parent_dir = os.path.dirname(absolute_file_path)
    if not os.path.exists(parent_dir):
        try:
            os.makedirs(parent_dir, exist_ok=True)
        except Exception as e:
            return f"Error creating directories for {absolute_file_path}: {str(e)}"
            
    try:
        with open(absolute_file_path, 'w') as file:
            file.write(content)
        return f"Successfully wrote to file {file_path} {len(content)} characters."
    
    except Exception as e:
        return f"Error writing to file {file_path}: {str(e)}"
    
    
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="overwrite content to a exiting file or create a new file or folder if not present previously and then write to the file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type= types.Type.STRING,
                description= "The path to the file, relative to the working directory.",
            ),
            "content": types.Schema(
                type= types.Type.STRING,
                description= "The content to write to the file.",
            ),
        },
        required=["file_path", "content"]
    )
)