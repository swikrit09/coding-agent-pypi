import os
import subprocess
from google.genai import types

def run_python_file(working_directory, file_path : str, args = []):
    absolute_working_dir = os.path.abspath(working_directory)
    absolute_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not absolute_file_path.startswith(absolute_working_dir):
        return f"Error: The file {absolute_file_path} is outside the working directory {absolute_working_dir}."
    
    if not os.path.isfile(absolute_file_path):
        return f"Error: The path {absolute_file_path} is not a valid file."
        
    if not absolute_file_path.endswith('.py'):
        return f"Error: The file {absolute_file_path} is not a Python (.py) file."
    import sys
    try:
        final_args = [sys.executable, absolute_file_path]
        final_args.extend(args)
        result = subprocess.run(
            final_args, 
            timeout=30, 
            capture_output=True, 
            text=True,
            cwd=working_directory,  
            # env=os.environ.copy(),  
        )
        final_string = f'''STDOUT:\n{result.stdout}STDERR:\n{result.stderr}'''
        # if result.returncode != 0:
        #     final_string += f"\nProcess exited with non-zero return code: {result.returncode}"
        
        if result.stdout == "" and result.stderr == "":
            final_string = "\nNote: The script produced no output."
        
        return final_string
    
    
    except Exception as e:
        return f"Error running file {file_path}: {str(e)}"
    
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Run a Python (.py) file accepting a list of args from the cli argument and return its output.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type= types.Type.STRING,
                description= "The path to the Python file, relative to the working directory.",
            ),
            "args": types.Schema(
                type= types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description= "A list of command-line arguments to pass to the Python script.",
            ),
        },
        required=["file_path"]
    )
)