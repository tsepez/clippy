#!/usr/bin/env python

import sys
import os
import re

def read_file_content(filepath):
    """
    Reads the content of a file.

    Args:
        filepath (str): The path to the file.

    Returns:
        str: The content of the file, or None if the file is not found.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except FileNotFoundError:
        sys.stderr.write(f"Warning: File not found: {filepath}\n")
        return None
    except Exception as e:
        sys.stderr.write(f"Error reading file {filepath}: {e}\n")
        return None

def extract_non_system_includes(content):
    """
    Extracts paths from non-system #include directives (e.g., #include "filename").

    Args:
        content (str): The content of a file.

    Returns:
        list: A list of paths found in the #include directives.
    """
    # Regular expression to find #include "..."
    # Group 1 captures the path inside the double quotes.
    return re.findall(r'#include\s+"([^"]+)"', content)

def main():
    """
    Main function to parse command-line arguments and create the archive.
    """
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python archive_cpp.py <main_cpp_file>\n")
        sys.stderr.write("Example: python archive_cpp.py src/main.cpp\n")
        sys.exit(1)

    main_cpp_file_arg = sys.argv[1]
    
    # Store absolute paths of processed files to avoid duplicates
    processed_files_abs_paths = set()
    output_parts = []

    # 1. Process the main .cpp file first
    # Resolve the main .cpp file path relative to the current working directory
    # for reading, but use the original argument for the archive header.
    main_cpp_abs_path = os.path.abspath(main_cpp_file_arg)
    main_cpp_content = read_file_content(main_cpp_abs_path)

    if main_cpp_content is None:
        sys.stderr.write(f"Error: Could not read the main C++ file: {main_cpp_file_arg}\n")
        sys.exit(1)

    # Add the main C++ file to the archive output
    output_parts.append(f">>>>{main_cpp_file_arg}\n{main_cpp_content}")
    processed_files_abs_paths.add(main_cpp_abs_path)

    # 2. Scan the main .cpp file for non-system includes
    included_files_paths = extract_non_system_includes(main_cpp_content)

    # 3. Process each found included file (one level deep)
    for include_path_from_cpp in included_files_paths:
        # Resolve the include path relative to the Current Working Directory (CWD)
        # This is based on the requirement "The relative path for those files
        # should be used relative to CWD to find the contents."
        full_include_abs_path = os.path.abspath(os.path.join(os.getcwd(), include_path_from_cpp))

        # Check if the file has already been processed to avoid duplicates
        if full_include_abs_path in processed_files_abs_paths:
            sys.stderr.write(f"Warning: Skipping duplicate or already processed include: {include_path_from_cpp}\n")
            continue

        included_content = read_file_content(full_include_abs_path)

        if included_content is not None:
            # Add the included file to the archive output, using its original
            # relative path from the #include directive for the header.
            output_parts.append(f">>>>{include_path_from_cpp}\n{included_content}")
            processed_files_abs_paths.add(full_include_abs_path)
        # else: A warning is already printed by read_file_content

    # Write the complete archive to stdout
    sys.stdout.write("\n".join(output_parts))
    # Ensure a final newline if the last file content doesn't end with one,
    # or just for consistency if concatenating parts.
    if output_parts and not output_parts[-1].endswith('\n'):
        sys.stdout.write('\n')


if __name__ == "__main__":
    main()
