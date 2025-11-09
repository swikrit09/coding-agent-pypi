from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file

def main():
    # working_directory = "dummy"
    # root_contents = get_files_info(working_directory)
    # print("Root Directory Contents:\n", root_contents)
    # package_contents = get_files_info(working_directory, "test_folder")
    # print("test_folder Contents:\n", package_contents)
    # outside_contents = get_files_info("dummy",'../')
    # print("Outside Directory Attempt:\n", outside_contents)
    
    # working_directory = "dummy/test_folder"
    
    # file_content = get_file_content(working_directory, "test.py")
    # print("File Content:\n", file_content)
    # truncated_file_content = get_file_content(working_directory, "lore.html")
    # print("Truncated Content:\n", truncated_file_content)
    
    # working_directory = "dummy"
    # print(write_file(working_directory, "hello/new_hello.txt", "This is a new file created by the write_file function."))
    # print(write_file(working_directory, "../outside_file.txt", "This should fail due to directory traversal."))
    
    
    # working_directory = "dummy"
    # run_result = run_python_file(working_directory, "test_folder/test.py")
    # print("Run Result:\n", run_result)
    
    working_directory = ""
    run_result = run_python_file(working_directory, "main.py", args=["what is 1+1 give in 1 token"])
    print("Run Result:\n", run_result)
    
    
    
if __name__ == "__main__":
    main()
    