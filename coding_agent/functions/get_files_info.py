import os
from google.genai import types

def get_files_info(working_directory, directory=None):
    absolute_working_dir = os.path.abspath(working_directory)
    if directory is None:
        absolute_directory = absolute_working_dir
    else:
        absolute_directory = os.path.abspath(os.path.join(working_directory, directory))
    if not absolute_directory.startswith(absolute_working_dir):
        return f"Error: The directory {absolute_directory} is outside the working directory {absolute_working_dir}."

    final_response = ""
    contents = os.listdir(absolute_directory)
    for content in contents:
        content_path = os.path.join(absolute_directory, content)
        is_dir = os.path.isdir(content_path)
        size = os.path.getsize(content_path)

        final_response += f"- {content}: file size {size} bytes, is_directory: {is_dir}\n"
    return final_response

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Get information about files in a directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type= types.Type.STRING,
                description= "The directory to list files from, relative to the working directory. If not provided, lists files in the working directory.",
            ),
        }
    )
)

