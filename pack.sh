#!/bin/bash

# Script to combine content of text files in a directory recursively.
# Usage: ./combine_files.sh <directory> [pattern1] [pattern2] ...
# Example: ./combine_files.sh . '*.rs' '*.md'
# Example: ./combine_files.sh /path/to/project
# Example: ./combine_files.sh . | less
# Example: ./combine_files.sh . > combined.txt

# --- Configuration ---
OUTPUT_FILENAME="combined_content.txt" # Only used when outputting to terminal

# --- Function: Print usage ---
usage() {
  # Print usage message to stderr
  echo "Usage: $0 <directory> [file_pattern ...]" >&2
  echo "  <directory>: The directory to search recursively." >&2
  echo "  [file_pattern ...]: Optional shell patterns (e.g., '*.txt', 'main.*')." >&2
  echo "                      If no patterns are given, all non-binary files (excluding .git) are included." >&2
  echo >&2
  echo "Output:" >&2
  echo "  If stdout is a terminal, combines content into a temporary file and prints its path." >&2
  echo "  If stdout is piped or redirected, prints the combined content directly to stdout." >&2
  echo "  Excludes binary files and files within any '.git' directory." >&2
  exit 1
}

# --- Argument Validation ---
if [ "$#" -lt 1 ]; then
  echo "Error: Directory argument is missing." >&2
  usage
fi

TARGET_DIR="$1"
shift # Remove directory from arguments, patterns remain in $@

if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: '$TARGET_DIR' is not a valid directory." >&2
  exit 1
fi

# --- Dependency Check ---
if ! command -v file &> /dev/null; then
    echo "Error: 'file' command not found. Please install it (usually part of 'file' package)." >&2
    exit 1
fi
if ! command -v mktemp &> /dev/null && [ -t 1 ]; then
    # mktemp is only strictly needed if we're writing to a temp file (terminal output)
    echo "Error: 'mktemp' command not found. Cannot create secure temporary directory for terminal output." >&2
    exit 1
fi


# --- Determine Output Method ---
OUTPUT_TARGET="" # Will be stdout or a temporary file path
TEMP_DIR=""      # Store temp dir path if created

# Check if stdout is connected to a terminal
if [ -t 1 ]; then
  # Outputting to terminal: Use a temporary file
  echo "Outputting to terminal. Creating temporary file..." >&2
  TEMP_DIR=$(mktemp -d)
  if [ ! -d "$TEMP_DIR" ]; then
      echo "Error: Could not create temporary directory." >&2
      exit 1
  fi
  OUTPUT_TARGET="$TEMP_DIR/$OUTPUT_FILENAME"
  # Ensure output file is empty/created before starting
  : > "$OUTPUT_TARGET" || { echo "Error: Could not create or clear output file: $OUTPUT_TARGET" >&2; rm -rf "$TEMP_DIR"; exit 1; }
else
  # Outputting to pipe/redirect: Use stdout
  # No file needs to be created here. Informational messages go to stderr.
  echo "Outputting directly to stdout (pipe or redirection detected)." >&2
  OUTPUT_TARGET="/dev/stdout" # Conceptually, we're writing to stdout
fi


# --- Normalize Target Directory Path ---
TARGET_DIR_CLEAN="${TARGET_DIR%/}"


# --- Build find command arguments ---
find_args=("$TARGET_DIR_CLEAN")
find_args+=( \( -path '*/.git' -prune \) -o )

if [ "$#" -gt 0 ]; then
    find_args+=( \( )
    first_pattern=true
    for pattern in "$@"; do
        if [ "$first_pattern" = false ]; then
            find_args+=( -o )
        fi
        find_args+=( -name "$pattern" )
        first_pattern=false
    done
    find_args+=( \) )
    find_args+=( -a )
fi

find_args+=( -type f -print0 )

# --- Inform User (Redirected to stderr) ---
echo "Searching in: '$TARGET_DIR_CLEAN'" >&2
if [ "$#" -gt 0 ]; then
    echo "Matching patterns: $@" >&2
else
    echo "Matching all non-binary files (no specific patterns given)." >&2
fi
echo "Ignoring files in '.git' directories and binary files." >&2
if [ -n "$TEMP_DIR" ]; then # Only show temp file path if we created one
    echo "Temporary file will be: $OUTPUT_TARGET" >&2
fi
echo "Processing..." >&2

# --- Process Files ---
processed_count=0
skipped_binary_count=0

# Define where to send the combined content based on the earlier check
# If OUTPUT_TARGET is /dev/stdout, commands write directly to stdout.
# If OUTPUT_TARGET is a file path, commands append (>>) to that file.
output_command() {
    if [ "$OUTPUT_TARGET" = "/dev/stdout" ]; then
        cat # Read from stdin (pipe), write to stdout
    else
        cat >> "$OUTPUT_TARGET" # Read from stdin (pipe), append to file
    fi
}

while IFS= read -r -d $'\0' file; do
    mime_type=$(file --mime-type -b "$file")

    if [[ ! "$mime_type" == text/* && ! "$mime_type" == "inode/x-empty" ]]; then
        # Uncomment the following line for debugging binary skips
        # echo "  Skipping binary file: $file (MIME: $mime_type)" >&2
        ((skipped_binary_count++))
        continue
    fi

    relative_path="${file#"$TARGET_DIR_CLEAN"/}"

    # Add header, content, and blank line, piping through output_command
    {
        echo ">>>> $relative_path"
        cat "$file"
        echo ""
    } | output_command

    ((processed_count++))

done < <(find "${find_args[@]}")

# --- Completion Message (Redirected to stderr) ---
echo "Done." >&2
echo "Processed $processed_count file(s)." >&2
if [ "$skipped_binary_count" -gt 0 ]; then
    echo "Skipped $skipped_binary_count binary file(s)." >&2
fi

# --- Final Output ---
if [ -n "$TEMP_DIR" ]; then
    # If we created a temp file (outputting to terminal),
    # print the path of the temp file to standard output.
    echo "$OUTPUT_TARGET"
else
    # If we wrote to stdout directly, there's nothing more to print here.
    # The content has already been streamed.
    : # No-op
fi

exit 0
