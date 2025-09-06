# Bulk Extractor AI

An AI tool that uses Large Language Models (LLMs) to automate the process of extracting valuable information from large sets of files, such as emails or documents, into a structured format like JSON.

---

### What it Does

This tool automates the tedious process of extracting specific information from a large number of similar files (e.g., emails, documents). You provide a folder of files, tell the AI what you're looking for in plain English, and it generates structured JSON output for you.

**Example Use Case**

You want to analyze your grocery habits over the last three years but your data is buried in hundreds of order confirmation emails scattered throughout your inbox, manually copying and pasting would take hours. Instead, you can download your inbox or just the subset containing grocery receipts, point Bulk Extractor AI to the folder of .eml files, and provide a simple prompt: “For each email, extract the grocery items I have purchased, including their name, quantity, and price.” The tool then processes each email, filters out irrelevant ones, and generates clean JSON file(s) containing the data you requested.

### Getting Started

Follow these instructions to set up and run the application on your local machine.

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

#### 3. Configuration

This application uses Google's Gemini models. You will need to provide your own API key; get one for free here: https://aistudio.google.com/apikey.

1.  Create a file named `.env` in the root of the project directory.
2.  Add at least one Gemini API key and at least one desired model to the `.env` file. You can add multiple keys (comma-separated) for automatic rotation and multiple models for fallback.

```env
# .env file
GEMINI_API_KEYS="YOUR_GEMINI_API_KEY_1,YOUR_GEMINI_API_KEY_2"
GEMINI_MODELS="gemini-2.5-pro,gemini-2.5-flash,gemini-2.5-flash-lite,gemini-2.0-flash,gemini-2.0-flash-lite,gemini-1.5-flash,gemini-1.5-flash-8b"
```

#### 4. Running the Extractor

The application is run from the command line. You need to provide an input folder, an output folder, and a prompt file.

1.  Place all your `.eml` files into a directory (e.g., `input_data`).
2.  Create an empty directory for the results (e.g., `output_data`).
3.  Write your extraction instructions in a text file (e.g., `prompt.txt`).

Execute the application with the following command:
```bash
python src/cli.py --input-folder input_data --output-folder output_data --prompt-file prompt.txt --output-method one_per_relevant_file
```

**Available Output Methods:**
*   `one_per_file`: Creates one JSON file for every input file, even if no relevant data was found.
*   `one_per_relevant_file`: (Default) Only creates a JSON file if the AI found relevant data.
*   `single_file`: Consolidates all extracted data from all relevant files into a single JSON file.

### Future Vision

The long-term goal is to evolve this CLI tool into a full-fledged SaaS application with:
*   A user-friendly web interface (built with FastAPI and a modern frontend).
*   An "Orchestrator LLM" that translates simple user requests into powerful extraction prompts.
*   Support for a wider variety of file types.