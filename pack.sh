#!/bin/bash

# Script to combine content of text files in a directory recursively.
# Usage: ./combine_files.sh <directory> [pattern1] [pattern2] ...
# Example: ./combine_files.sh . '*.rs' '*.md'
# Example: ./combine_files.sh /path/to/project

# --- Configuration ---
OUTPUT_FILENAME="combined_content.txt"

# --- Function: Print usage ---
usage() {
  echo "Usage: $0 <directory> [file_pattern ...]"
  echo "  <directory>: The directory to search recursively."
  echo "  [file_pattern ...]: Optional shell patterns (e.g., '*.txt', 'main.*')."
  echo "                      If no patterns are given, all non-binary files (excluding .git) are included."
  echo
  echo "Output:"
  echo "  Combines content into a single file in a temporary directory."
  echo "  Excludes binary files and files within any '.git' directory."
  exit 1
}

# --- Argument Validation ---
if [ "$#" -lt 1 ]; then
  echo "Error: Directory argument is missing."
  usage
fi

TARGET_DIR="$1"
shift # Remove directory from arguments, patterns remain in $@

if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: '$TARGET_DIR' is not a valid directory."
  exit 1
fi

# --- Dependency Check ---
if ! command -v file &> /dev/null; then
    echo "Error: 'file' command not found. Please install it (usually part of 'file' package)."
    exit 1
fi
if ! command -v mktemp &> /dev/null; then
    echo "Error: 'mktemp' command not found. Cannot create secure temporary directory."
    exit 1
fi


# --- Prepare Output ---
# Create a secure temporary directory
OUTPUT_DIR=$(mktemp -d)
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Error: Could not create temporary directory."
    exit 1
fi
OUTPUT_FILE="$OUTPUT_DIR/$OUTPUT_FILENAME"

# Ensure output file is empty/created before starting
# Use > redirection which truncates or creates the file
: > "$OUTPUT_FILE" || { echo "Error: Could not create or clear output file: $OUTPUT_FILE"; exit 1; }


# --- Normalize Target Directory Path ---
# Remove trailing slash if present for consistent relative path calculation later
# Using parameter expansion for portability (instead of realpath)
TARGET_DIR_CLEAN="${TARGET_DIR%/}"


# --- Build find command arguments ---
# Use an array to handle spaces and special characters safely
find_args=("$TARGET_DIR_CLEAN") # Start find in the target directory

# Prune .git directories:
# -path '*/.git' matches any path ending in /.git
# -prune stops find from descending into matched directories
# We need parenthesis for correct precedence with -o (OR)
find_args+=( \( -path '*/.git' -prune \) -o )

# Add pattern matching if patterns are provided
if [ "$#" -gt 0 ]; then
    find_args+=( \( ) # Start OR group for patterns
    first_pattern=true
    for pattern in "$@"; do
        if [ "$first_pattern" = false ]; then
            find_args+=( -o ) # OR between patterns
        fi
        # Use -name for simple globbing within find
        find_args+=( -name "$pattern" )
        first_pattern=false
    done
    find_args+=( \) ) # End OR group
    find_args+=( -a ) # AND with the type check below
fi

# We only want regular files (-type f) and print them null-separated for safety
find_args+=( -type f -print0 )

# --- Inform User ---
echo "Searching in: '$TARGET_DIR_CLEAN'"
if [ "$#" -gt 0 ]; then
    echo "Matching patterns: $@"
else
    echo "Matching all non-binary files (no specific patterns given)."
fi
echo "Ignoring files in '.git' directories and binary files."
echo "Output file will be: $OUTPUT_FILE"
echo "Processing..."

# --- Process Files ---
# Use find with the constructed arguments.
# Pipe the null-separated output to a while loop reading null-separated records.
# This correctly handles filenames with spaces, newlines, or special characters.
processed_count=0
skipped_binary_count=0
while IFS= read -r -d $'\0' file; do
    # Check if the file is binary using 'file --mime-type -b'
    # '-b' prevents printing the filename
    mime_type=$(file --mime-type -b "$file")

    # Consider text files or empty files (inode/x-empty) as non-binary
    if [[ ! "$mime_type" == text/* && ! "$mime_type" == "inode/x-empty" ]]; then
        # Uncomment the following line for debugging binary skips
        # echo "  Skipping binary file: $file (MIME: $mime_type)" >&2
        ((skipped_binary_count++))
        continue # Skip this file
    fi

    # Calculate relative path from the original TARGET_DIR_CLEAN
    # Remove the TARGET_DIR_CLEAN prefix, plus the leading '/' if it exists
    relative_path="${file#"$TARGET_DIR_CLEAN"/}"

    # Add header and content to the output file
    echo ">>>> $relative_path" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
    # Add a blank line after each file's content for readability
    echo "" >> "$OUTPUT_FILE"
    ((processed_count++))

done < <(find "${find_args[@]}") # Execute find with constructed args via Process Substitution

# --- Completion Message ---
echo "Done."
echo "Processed $processed_count file(s)."
if [ "$skipped_binary_count" -gt 0 ]; then
    echo "Skipped $skipped_binary_count binary file(s)."
fi
echo "Combined content written to: $OUTPUT_FILE"

exit 0
