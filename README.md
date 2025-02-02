# Clippy: Your AI Command-Line Assistant

**Clippy** is a simple command-line utility that allows you to interact with various AI models (currently supporting OpenAI, Google, and potentially Anthropic compatible APIs) directly from your terminal.  Ask questions, get quick answers, and boost your productivity without leaving the command line!

## Features

*   **Ask AI Models from the Command Line:**  Quickly get answers to your questions using powerful AI models.
*   **Multi-Provider Support:**  Currently supports:
    *   **OpenAI:**  Utilize models like `gpt-4o`, `gpt-3.5-turbo`, and more.
    *   **Google:** Access Gemini models (via OpenAI compatible endpoint).
    *   **Anthropic (Experimental):**  Potentially compatible with Anthropic models via OpenAI-compatible endpoints (further testing and configuration may be required).
*   **Configuration File:**  Stores your API keys and model preferences securely in your home directory (`~/.clippy/config.json`).
*   **Simple Setup:** Easy to configure with a single command to set your model and API key.
*   **Clean Output:**  Provides formatted and readable AI responses in your terminal.

## Prerequisites

*   **Python 3.6 or higher:** Make sure you have Python 3 installed on your system.
*   **OpenAI Python Library:**  This utility uses the `openai` Python library to interact with AI APIs. It will be installed during the installation process.
*   **API Keys:** You will need API keys from the AI providers you wish to use:
    *   **OpenAI API Key:** Get one from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys).
    *   **Google API Key (for Gemini):**  You may need a Google Cloud project and API key enabled for the PaLM API (which is used for Gemini models via the OpenAI compatible endpoint). Refer to Google's documentation for details.
    *   **Anthropic API Key (if using Anthropic via OpenAI endpoint):**  If you intend to use Anthropic models via an OpenAI compatible endpoint, you will need the corresponding API key and potentially the endpoint URL.  **Note:** Direct and officially supported Anthropic integration might require using Anthropic's own SDK and API, not the OpenAI library.

## Installation

1.  **Clone the repository (or download the script):**

    ```bash
    git clone <repository_url>  # Replace <repository_url> with the actual repository URL if you have one.
    cd clippy
    ```

    If you downloaded the script directly (e.g., `clippy.py`), navigate to the directory where you saved it in your terminal.

2.  **Make the script executable:**

    ```bash
    chmod +x clippy.py
    ```

3.  **Optional: Move to your PATH (for global access):**

    To use `clippy` from anywhere in your terminal, you can move it to a directory in your system's `PATH` environment variable, such as `/usr/local/bin` or `~/bin`.

    ```bash
    mv clippy.py /usr/local/bin/clippy  # You might need sudo for /usr/local/bin
    # OR
    mv clippy.py ~/bin/clippy
    ```

    Make sure `~/bin` or `/usr/local/bin` is in your `PATH` environment variable. You can usually add `export PATH="$HOME/bin:$PATH"` to your `~/.bashrc` or `~/.zshrc` file and then `source ~/.bashrc` or `source ~/.zshrc`.

4.  **Install the `openai` library:**

    ```bash
    pip install openai
    ```

## Configuration

Before you can use `clippy`, you need to set your desired AI model and API key.

**Set Model and API Key:**

Use the `set_model` command followed by the model name and your API key in the format `<model_name>:<api_key>`.

```bash
clippy set_model gpt-4o:YOUR_OPENAI_API_KEY
