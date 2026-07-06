import os  # Imports the operating system module to interact with files and folders

# We define the ONLY file extensions we actually care about reading
allowed_extensions = [".py", ".html", ".css", ".js", ".ts"]


def combine_code_final(output_filename="all_code.txt"):
    # Opens the output text file in write mode
    with open(output_filename, "w", encoding="utf-8") as outfile:

        # Starts a loop that walks through every folder and subfolder
        for root, dirs, files in os.walk("."):

            # Convert the current path to lowercase to prevent capitalization bypasses
            root_lowered = root.lower()

            # SYSTEM GUARD: If the current path contains ANY of these phrases, skip the entire folder instantly
            if (
                "node_modules" in root_lowered
                or "venv" in root_lowered
                or ".git" in root_lowered
                or "__pycache__" in root_lowered
                or "src-tauri/target" in root_lowered
            ):
                continue

            # Loop through the individual files in the safe folder
            for file in files:
                file_lowered = file.lower()

                # Skip lockfiles, environment configuration data, and compiled Python files
                if (
                    "lock.json" in file_lowered
                    or ".env" in file_lowered
                    or file_lowered.endswith(".pyc")
                ):
                    continue

                # Check if the file matches one of our allowed source code extensions
                if any(file_lowered.endswith(ext) for ext in allowed_extensions):
                    filepath = os.path.join(root, file)

                    try:
                        # Open and read the raw source code
                        with open(filepath, "r", encoding="utf-8") as infile:
                            content = infile.read()

                        # Write a clear separation header into the final document
                        outfile.write(
                            f"\n\n{'='*40}\nFILE: {filepath}\n{'='*40}\n\n"
                        )
                        outfile.write(content)

                    except Exception as e:
                        # Log any unreadable files gracefully without crashing the pipeline
                        outfile.write(f"\nCould not read file {filepath}: {e}\n")


if __name__ == "__main__":
    combine_code_final()
    print("Success! Your streamlined 'all_code.txt' is ready.")