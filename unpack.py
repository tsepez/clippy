#!/usr/bin/env python

import os
import sys
import re

def unpack_file(source_stream):
    """
    Unpacks content from a stream (like stdin or a file) into individual files
    based on the '>>>> filename' format.

    Args:
        source_stream: The input stream to read from (e.g., sys.stdin or an opened file object).
    """
    print(f"Starting to unpack from {'stdin' if source_stream is sys.stdin else source_stream.name}...")

    try:
        content = source_stream.read()

        # Regular expression to find file markers and capture content
        # Pattern: >>>> (filename) (content) >>>> or EOF
        # [^>] specifies any character that is not '>'
        # +? for non-greedy match of filename
        # \s*\n to match potential whitespace and the newline after the filename
        # (.*?) for non-greedy match of file content (including newlines due to re.DOTALL)
        # (?=\n>>>>|\Z) is a positive lookahead to stop matching content
        # at the start of the next '>>>>' block (preceded by a newline)
        # or at the end of the string (\Z)
        pattern = r'>>>>\s*([^>]+?)\s*\n(.*?)(?=\n>>>>|\Z)'

        # We need to find all matches, including those that might not be at the very start
        matches = re.finditer(pattern, content, re.DOTALL)

        if not matches:
            print("No file markers ('>>>> filename') found in the input.")
            return

        unpacked_count = 0
        for match in matches:
            filename = match.group(1).strip()
            # MODIFICATION: Removed .strip() from file_content to preserve internal newlines
            file_content = match.group(2)

            if not filename:
                print("Warning: Found an empty filename. Skipping this block.")
                continue

            # Split original filename into path components, filter out '..' and absolute paths.
            # This is a simplified sanitization; a more comprehensive one might use pathlib.
            output_path_parts = filename.split(os.sep)
            clean_path_parts = [part for part in output_path_parts if part not in ['', '.', '..']]

            if not clean_path_parts:
                print(f"Warning: Filename '{filename}' resulted in no valid path components. Skipping.")
                continue

            # The actual file name is the last part
            final_filename = clean_path_parts[-1]

            # The directory path is everything before the final filename
            output_dir_parts = clean_path_parts[:-1]

            # Construct the full output directory path
            output_directory = os.path.join(*output_dir_parts) if output_dir_parts else "."

            # --- MODIFICATION START ---
            # Do not create the directory. Instead, check if it exists and warn if not.
            if output_directory != "." and not os.path.exists(output_directory):
                print(f"Warning: Directory '{output_directory}' for file '{filename}' does not exist. Skipping this file.")
                continue # Skip to the next file in the archive
            # --- MODIFICATION END ---

            # Construct the full path to the output file
            full_output_filepath = os.path.join(output_directory, final_filename)

            try:
                with open(full_output_filepath, 'w', encoding='utf-8') as outfile:
                    # MODIFICATION: Ensure file_content ends with a newline, if it doesn't already
                    if not file_content.endswith('\n'):
                        outfile.write(file_content + '\n')
                    else:
                        outfile.write(file_content)
                print(f"Successfully unpacked '{full_output_filepath}'")
                unpacked_count += 1
            except IOError as e:
                print(f"Error writing file '{filename}' to '{full_output_filepath}': {e}")
            except Exception as e:
                print(f"An unexpected error occurred while processing '{filename}': {e}")

        print(f"\nUnpacking complete. {unpacked_count} files unpacked.")

    except Exception as e:
        print(f"An error occurred while reading input: {e}")

if __name__ == "__main__":
    # If a filename is provided as a command-line argument, read from that file.
    # Otherwise, read directly from standard input (stdin).
    if len(sys.argv) > 1:
        pack_file_path = sys.argv[1]
        try:
            with open(pack_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                unpack_file(f)
        except FileNotFoundError:
            print(f"Error: The file '{pack_file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred while opening/reading '{pack_file_path}': {e}")
    else:
        # No argument, read from stdin
        unpack_file(sys.stdin)

    # --- How to create a dummy 'example.pack' for testing ---
    # Create a file named 'example.pack' with the following content:
    """
    This is some introductory text that should be skipped.
    It can contain anything and span multiple lines.

    >>>> file1.txt
    Hello, this is the content of file 1.
    This line is also part of file 1.
    >>>> non_existent_dir/file2.txt
    Content for the second file, which will be skipped if 'non_existent_dir' doesn't exist.
    It demonstrates content for file2.
    >>>> another_file.log
    Log entry 1: Something happened.
    Log entry 2: Something else happened.
    This is the final line of another_file.log.
    """
    # You can test this by piping the content of example.pack:
    # cat example.pack | python unpack_script.py
    # Or, for Windows:
    # type example.pack | python unpack_script.py
    # Or, for direct input (type content then Ctrl+D / Ctrl+Z+Enter):
    # python unpack_script.py
