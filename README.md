# Bulk Extractor AI

An AI tool that uses Large Language Models (LLMs) to automate the process of extracting valuable information from large sets of files, such as emails or documents, into a structured format like JSON.

This project provides two ways to interact with the extraction engine: a **Command-Line Interface (CLI)** for local development and scripting, and a **Web API** built with FastAPI, ready for integration with web frontends.

---

### What it Does

This tool automates the tedious process of extracting specific information from a large number of similar files (e.g., emails, documents). You provide a folder of files, tell the AI what you're looking for in plain English, and it generates structured JSON output for you.

**Example Use Case**

You want to analyze your grocery habits over the last three years but your data is buried in hundreds of order confirmation emails. Manually copying and pasting would take hours. Instead, you can download the relevant `.eml` files, provide them to Bulk Extractor AI, and use a simple prompt: “For each email, extract the grocery items I have purchased, including their name, quantity, and price.” The tool then processes each email and generates clean JSON file(s) containing exactly the data you requested.

### Getting Started

Follow these instructions to set up the application on your local machine. These steps are required for both the CLI and the Web API.

#### 1. Prerequisites

*   Python 3.8+
*   Git

#### 2. Installation & Setup

First, clone the repository to your local machine:
```bash
git clone <YOUR_AZURE_DEVOPS_REPO_URL>
cd bulk-extractor-ai
```

Next, create and activate a virtual environment using `uv`. If you don't have `uv`, install it first with `pip install uv`.
```bash
# Create the virtual environment
uv venv

# Activate the environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows (PowerShell):
.venv\Scripts\activate
```

Now, install the required dependencies from the `requirements.txt` file:
```bash
uv pip install -r requirements.txt
```

---

### How to Use

You can run the extractor in two ways:

### Option 1: Using the Command-Line Interface (CLI)

The CLI is ideal for local batch processing and scripting.

#### CLI Configuration

The CLI reads your API key(s) from a local environment file.

1.  Create a file named `.env` in the root of the project directory.
2.  Add your Gemini API key(s) and desired model(s) to the `.env` file. You can add multiple keys (comma-separated) for automatic rotation and multiple models for fallback. Get a free key here: [Google AI Studio](https://aistudio.google.com/apikey).

    ```env
    # .env file
    GEMINI_API_KEYS="YOUR_GEMINI_API_KEY_1,YOUR_GEMINI_API_KEY_2"
    GEMINI_MODELS="gemini-2.5-pro,gemini-2.5-flash,gemini-2.5-flash-lite,gemini-2.0-flash,gemini-2.0-flash-lite,gemini-1.5-flash,gemini-1.5-flash-8b"
    ```

#### Running the CLI Extractor

1.  Place all your `.eml` files into a directory (e.g., `input_data`).
2.  Create an empty directory for the results (e.g., `output_data`).
3.  Write your extraction instructions in a text file (e.g., `prompt.txt`).

Execute the application with the following command:
```bash
python src/cli.py --input-folder input_data --output-folder output_data --prompt-file prompt.txt --output-method one_per_relevant_file
```

**Available Output Methods:**
*   `one_per_file`: Creates one JSON file for every input file, even if no relevant data was found.
*   `one_per_relevant_file`: Only creates a JSON file if the AI found relevant data.
*   `single_file`: Consolidates all extracted data from all relevant files into a single JSON file.

---

### Option 2: Using the Web API (FastAPI)

The Web API turns the extractor into a service that can be called from a web browser or another application. It uses a "Bring Your Own Key" (BYOK) model, where the API key is provided with each request.

#### Running the API Server

Start the web server from the project's root directory using Uvicorn:
```bash
uvicorn src.api:app --reload
```
The server will be running at `http://127.0.0.1:8000`. The `--reload` flag automatically restarts the server when you make code changes.

#### Interacting with the API

FastAPI provides automatic interactive documentation.
1.  Once the server is running, open your browser and navigate to **`http://127.0.0.1:8000/docs`**.
2.  You will see the Swagger UI interface. Expand the `POST /extract/` endpoint.
3.  Click the **"Try it out"** button.
4.  Fill in the parameters:
    *   `api_key`: Your personal Gemini API key(s), comma-separated.
    *   `prompt`: The plain-text instructions for the AI, [for example](prompt.txt)
    *   `output_method`: Choose one of the available methods from the dropdown.
    *   `files`: Click "Choose Files" and select one or more `.eml` files to upload.
5.  Click **"Execute"**.

The API will process your files and your browser will trigger a download for a `extraction_results.zip` file containing the structured JSON output.

### Future Vision

The long-term goal is to evolve this tool into a full-fledged SaaS application with:
*   A user-friendly web interface that interacts with our new FastAPI backend.
*   An LLM that translates a simple user natural language requests into an accurate extraction prompt that the backend can use.
*   Support for a wider variety of file types (e.g., `.pdf`, `.docx`, `.txt`).
*   Containerization with Docker and automated deployment via CI/CD pipelines.