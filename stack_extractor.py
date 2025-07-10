#!/usr/bin/env python

import argparse
import os
import re

def main():
    """
    Main function to parse command-line arguments, read the stack trace,
    extract local file paths, and print file contents.
    """
    parser = argparse.ArgumentParser(
        description="Extracts local file contents from a Chrome crash stack trace. "
                    "It prints the stack trace first, then the content of each "
                    "identified file that is within or beneath the current working directory."
    )
    parser.add_argument(
        "stack_trace_file",
        help="Path to the Chrome crash stack trace file (e.g., a .txt or .log file)."
    )
    args = parser.parse_args()

    stack_trace_content = ""
    try:
        # Read the entire stack trace content from the specified file
        with open(args.stack_trace_file, 'r', encoding='utf-8') as f:
            stack_trace_content = f.read()
    except FileNotFoundError:
        print(f"Error: The stack trace file '{args.stack_trace_file}' was not found.")
        return
    except Exception as e:
        print(f"Error reading stack trace file '{args.stack_trace_file}': {e}")
        return

    # Print the full stack trace content first, as requested
    print(stack_trace_content)

    # Get the current working directory's absolute path
    cwd = os.getcwd()
    cwd_abspath = os.path.abspath(cwd)

    # Ensure the current working directory path ends with a directory separator
    # This helps in robustly checking if a file path is beneath this directory
    # For example, '/a/b' becomes '/a/b/'
    if cwd_abspath != os.sep: # Check to avoid adding double slash for root
        cwd_abspath = os.path.join(cwd_abspath, '')

    # Set to store unique absolute paths of relevant files to avoid duplicates
    found_files = set()

    # Regular expression to find file paths in the new format:
    # It looks for a sequence of non-whitespace characters that is
    # preceded by a space and immediately followed by a colon and a digit (line number).
    # This pattern effectively captures the 'Path/to/file.ext' part.
    path_regex = re.compile(r'\s(\S+?):\d+')

    # Iterate through each line of the stack trace to find file paths
    for line in stack_trace_content.splitlines():
        match = path_regex.search(line)
        if match:
            raw_path = match.group(1).strip()

            # Skip paths that are clearly not local file system paths
            # (e.g., browser internal URLs, network paths, unknown sources)
            if raw_path.startswith(('http://', 'https://', 'chrome://', 'file://', '<unknown>')):
                continue

            # Construct the potential absolute path for the extracted raw_path.
            # os.path.join(cwd, raw_path) handles both relative and absolute raw_paths correctly:
            # - If raw_path is relative (e.g., 'src/main.js'), it's joined with cwd.
            # - If raw_path is absolute (e.g., '/home/user/project/file.js'), join ignores cwd.
            potential_full_path = os.path.join(cwd, raw_path)
            
            # Normalize the path to resolve '..', '.', and ensure consistent separators
            absolute_normalized_path = os.path.normpath(os.path.abspath(potential_full_path))

            # Check if the identified path exists on the file system and is a regular file.
            # Also, verify if this file is located within or is the current working directory.
            if os.path.exists(absolute_normalized_path) and os.path.isfile(absolute_normalized_path):
                # Ensure the file is beneath the current working directory.
                # This check uses `startswith` because `cwd_abspath` already includes a trailing separator.
                # This ensures '/a/b/file.js' is matched by '/a/b/' but '/a/banana.js' is not.
                if absolute_normalized_path.startswith(cwd_abspath) or \
                   absolute_normalized_path == os.path.normpath(os.path.abspath(cwd)):
                    found_files.add(absolute_normalized_path)

    # Now, iterate through the unique, relevant files and print their contents
    for file_path in sorted(list(found_files)): # Sort paths for consistent output order
        print(f"\n>>> {file_path}") # Separator followed by the file name
        try:
            # Read and print the file content.
            # 'errors='ignore'' is used to prevent UnicodeDecodeError for non-UTF-8 files.
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                print(f.read())
        except FileNotFoundError:
            # This should ideally not happen due to the os.path.exists check, but good for robustness
            print(f"Warning: File '{file_path}' was identified but could not be found when trying to read.")
        except Exception as e:
            print(f"Error reading content of file '{file_path}': {e}")

if __name__ == "__main__":
    main()
