# Clippy: Your Command-Line AI Assistant

**Clippy** is a simple yet powerful command-line interface (CLI) tool that lets you interact with various AI models like OpenAI's GPT series, Google's Gemini, and Anthropic's Claude directly from your terminal. Ask questions, get explanations, summarize text, and more – all without leaving your command line!

## Features

*   **Multi-Model Support:**  Works with OpenAI (gpt-4o, gpt-3.5-turbo, etc.), Google Gemini (gemini-pro), and Anthropic Claude models (and potentially others compatible with the OpenAI API endpoint).
*   **Easy Setup:**  Simple configuration to set your preferred AI model and API key.
*   **Ask Questions:**  Pose questions to the AI model and receive insightful responses directly in your terminal.
*   **Piping Input:**  Seamlessly feed file content to Clippy using pipes, allowing you to analyze and process files with AI.
*   **Configuration File:** Stores your model and API key securely in a configuration file in your home directory (`~/.clippy/config.json`).

## Getting Started

### Prerequisites

*   **Python 3.6 or higher:** Make sure you have Python installed on your system.
*   **OpenAI Python Library:** Install the `openai` library using pip:
    ```bash
    pip install openai
    ```

### Installation

1.  **Download the `clippy` script:** Save the provided Python script as `clippy` (or any name you prefer).
2.  **Make it executable:**  Give the script execute permissions:
    ```bash
    chmod +x clippy
    ```
3.  **Move to your PATH (Optional):** For easier access from anywhere in your terminal, you can move the `clippy` script to a directory in your system's PATH, such as `/usr/local/bin/` or `~/bin/`.
    ```bash
    # Example for /usr/local/bin (may require sudo)
    sudo mv clippy /usr/local/bin/
    ```
    or
    ```bash
    # Example for ~/bin (ensure ~/bin is in your PATH)
    mv clippy ~/bin/
    ```

### Configuration

Before you can start asking questions, you need to configure Clippy with your desired AI model and API key. Use the `set_model` command:

```bash
clippy set_model <model_name>:<your_api_key>
```


### Example

```bash
$ clippy set_model gemini-2.0-flash-thinking-exp-01-21:<gemini-api-key>
$ clippy ask "what is the capital of France?"
Sending prompt to model 'gemini-2.0-flash-thinking-exp-01-21'...

AI Response:

The capital of France is **Paris**.
```

If you install the [yek utility](https://github.com/bodo-run/yek), then you can
do the following:

```bash
$ git clone https://github.com/karpathy/cryptos
$ yek cryptos/ | clippy ask "Give me a high level overview of this project"
Sending prompt to model 'gemini-2.0-flash-thinking-exp-01-21'...

AI Response:

Okay, let's break down this `cryptos` project based on the provided README and code snippets.  Here's a high-level overview:

This project is a **pure Python implementation of Bitcoin**, designed for **educational purposes**.  It's built from scratch with **zero dependencies**, meaning it doesn't rely on any external libraries. The primary goal is to demonstrate and understand the inner workings of Bitcoin and its underlying cryptographic primitives.

Here's a feature-by-feature breakdown:
*   **Core Crypto Primitives:**
    *   **SHA-256:**  A fundamental cryptographic hash function used extensively in Bitcoin. The project includes a pure Python implementation (`cryptos/sha256.py`) that closely follows the NIST specification.  It's explicitly stated as being slow and for educational use only, showcasing how SHA-256 works at a code level.  Example usage is provided comparing its output to `shasum`.
    *   **RIPEMD-160:** Another hash function, used in Bitcoin addresses. While SHA-256 is implemented from scratch, RIPEMD-160 (`cryptos/ripemd160.py`) reuses an existing Python implementation with some cleanups, likely due to its greater complexity.
    ....
```
