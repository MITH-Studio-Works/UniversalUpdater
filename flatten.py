import os  # Imports the operating system module to interact with files and folders

# We define the ONLY file extensions we actually care about reading at the module level
allowed_extensions = [".py", ".html", ".css", ".js", ".ts", ".rs", ".toml", ".json", ".md"]

# Define the exact directory names we want to completely ignore at the module level
ignored_dirs = {"node_modules", "venv", ".venv", ".git", "__pycache__", "target", "dist", "build", ".vscode"}


def is_valid_file(file_name):
    # Convert the filename to lowercase to make our checks case-insensitive
    file_lowered = file_name.lower()
    
    # Check if the file is a lockfile, environment config, or compiled Python file
    if ".lock" in file_lowered or ".env" in file_lowered or file_lowered.endswith(".pyc"):
        # Return False immediately so the file is skipped
        return False
        
    # Check if the file ends with any of our allowed source code extensions
    # Returns True if a match is found, otherwise returns False
    return any(file_lowered.endswith(ext) for ext in allowed_extensions)


def append_file_content(filepath, outfile):
    try:
        # Open and read the raw source code of the individual file
        with open(filepath, "r", encoding="utf-8") as infile:
            # Read the entire file content into a variable
            content = infile.read()
            
        # Write a clear separation header into the final document so it is easy to read
        outfile.write(f"\n\n{'='*40}\nFILE: {filepath}\n{'='*40}\n\n")
        
        # Write the actual code content into the final document
        outfile.write(content)
        
    except Exception as e:
        # Log any unreadable files gracefully into the text document without crashing the script
        outfile.write(f"\nCould not read file {filepath}: {e}\n")


def combine_code_final(output_filename="all_code.txt"):
    # Opens the output text file in write mode with utf-8 encoding to handle all characters safely
    with open(output_filename, "w", encoding="utf-8") as outfile:
        
        # Starts a loop that walks through every folder and subfolder in the current directory
        for root, dirs, files in os.walk("."):
            
            # Modify the 'dirs' list in-place so os.walk ignores restricted folders entirely
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            
            # Loop through the individual files in the current safe folder
            for file in files:
                
                # Pass the filename to our helper function to see if it should be included
                if is_valid_file(file):
                    
                    # Join the folder path and the filename together to get the full, correct file path
                    filepath = os.path.join(root, file)
                    
                    # Pass the valid file path and the open output file to our writing helper function
                    append_file_content(filepath, outfile)


# This ensures the script only runs if executed directly, not if imported somewhere else
if __name__ == "__main__":
    # Call the main function to start the process
    combine_code_final()
    
    # Print a success message to the console so we know it finished successfully
    print("Success! Your streamlined 'all_code.txt' is ready.")