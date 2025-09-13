# 🤖 Bulk Extractor AI

An AI-powered, full-stack application that transforms unstructured files into structured JSON data using natural language. This project features an intuitive Streamlit web interface, a powerful FastAPI backend, and a robust command-line tool for developers.

**Live Demo:** [bulkai.streamlit.app](https://bulkai.streamlit.app/)

---

### What it Does

This tool automates the tedious process of extracting specific information from a large number of similar files (e.g., emails, documents). You provide a folder of files, tell the AI what you're looking for in plain English, and it generates structured JSON output for you.

The core of the application is an **LLM** that translates a user's simple goal into a precise, detailed prompt for the extraction task (which is performed by another LLM), ensuring high-quality results without the need for complex prompt engineering by the user.

**Example Use Case**

You want to analyze your grocery habits over the last three years, but your data is buried in hundreds of order confirmation emails. Manually copying and pasting would take hours. Instead, you can download the relevant `.eml` files, provide them to Bulk Extractor AI, and use a simple goal: “For each email, extract the grocery items I have purchased, including their name, quantity, and price.” The tool then processes each email and generates clean JSON containing exactly the data you requested.

---

### Three Ways to Use This Application

This project is designed for both end-users and developers, offering multiple ways to interact with the extraction engine.

#### Option 1: The Streamlit Web Interface (Recommended)

The easiest way to use the tool is through the live web application. It provides a user-friendly interface for uploading files, entering your API key, and describing your goal.

1.  Navigate to [bulkai.streamlit.app](https://bulkai.streamlit.app/).
2.  Enter your Gemini API Key in the sidebar. (For a free key, visit [Google AI Studio](https://aistudio.google.com/apikey). You can add multiple keys for automatic rotation by separating them with commas.)
3.  Select your desired output method.
4.  Upload one or more `.eml` files.
5.  Describe what you want to extract in the text area.
6.  Click "Run Extraction" and download your results.

#### Option 2: Run the Full Stack Locally

For development or local use, you can run the entire application stack (FastAPI backend + Streamlit frontend) on your machine.

**1. Prerequisites**
*   Python 3.8+
*   Git
*   `uv` (install with `pip install uv`)

**2. Installation & Setup**
First, clone the repository to your local machine:
```bash
git clone https://github.com/your-username/bulk-extractor-ai.git
cd bulk-extractor-ai
```

Next, create and activate a virtual environment:
```bash
# Create the virtual environment
uv venv

# Activate the environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows (PowerShell):
.venv\Scripts\activate
```

Now, install the required dependencies:
```bash
uv pip install -r requirements.txt
```

**3. Run the Backend (Terminal 1)**
Open a terminal and start the FastAPI server. It will handle all the AI processing.
```bash
uvicorn src.api:app --reload
```
The backend is now running at `http://127.0.0.1:8000`.

**4. Run the Frontend (Terminal 2)**
Open a *second* terminal and start the Streamlit application.
```bash
streamlit run app.py
```
The user interface will open in your browser, fully connected to your local backend. The app is now operational.

#### Option 3: Using the Command-Line Interface (CLI)

The CLI is ideal for power-users, scripting, and integrating the extractor into automated workflows.

**1. CLI Configuration**
The CLI reads your API key(s) from a local `.env` file.
1.  Create a file named `.env` in the root of the project directory.
2.  Add your Gemini API key(s) and desired model(s). You can add multiple keys (comma-separated) for automatic rotation and multiple models for fallback. Get a free key here: [Google AI Studio](https://aistudio.google.com/apikey).

    ```env
    # .env file
    GEMINI_API_KEYS="YOUR_GEMINI_API_KEY_1,YOUR_GEMINI_API_KEY_2"
    GEMINI_MODELS="gemini-2.5-pro,gemini-2.5-flash,gemini-2.5-flash-lite,gemini-2.0-flash,gemini-2.0-flash-lite,gemini-1.5-flash,gemini-1.5-flash-8b"
    ```

**2. Running the CLI Extractor**
1.  Place all your `.eml` files into a directory (e.g., `input_data`).
2.  Create an empty directory for the results (e.g., `output_data`).
3.  Execute the application with your desired arguments. You can provide a simple goal or a path to a detailed prompt file.

    *Example using a simple goal:*
    ```bash
    python src/cli.py --input-folder input_data --output-folder output_data --user-goal "Extract the sender's name and the subject line from each email" --output-method single_file
    ```

    *Example using a detailed prompt file:*
    ```bash
    python src/cli.py --input-folder input_data --output-folder output_data --prompt-file prompt.txt --output-method one_per_relevant_file
    ```

**Available Output Methods:**
*   `one_per_file`: Creates one JSON file for every input file, even if no relevant data was found.
*   `one_per_relevant_file`: Only creates a JSON file if the AI found relevant data.
*   `single_file`: Consolidates all extracted data from all relevant files into a single JSON file.

---

### Architecture & MLOps

This project is built with modern software engineering and MLOps practices to ensure it is robust, scalable, and maintainable.

-   **Containerization:** The FastAPI backend is containerized using **Docker**, ensuring a consistent and isolated runtime environment that can be deployed anywhere.

-   **CI/CD Automation:** An **Azure DevOps** pipeline (`azure-pipelines.yml`) is configured for Continuous Integration. On every commit to the `main` branch, the pipeline automatically:
    1.  Builds the Docker image.
    2.  Pushes the new image to a container registry (Docker Hub).

-   **Cloud Deployment:**
    -   The **FastAPI backend** is deployed as a Docker container on **Render**, providing a scalable and reliable web service.
    -   The **Streamlit frontend** is deployed to the **Streamlit Community Cloud**, offering a seamless user experience.

### Future Possibilities

Optionally, if development continues, the long-term goal is to evolve this tool into a full-fledged SaaS application with:
*   Support for a wider variety of file types (e.g., `.pdf`, `.docx`, `.txt`, `.csv`, `.jpg`).
*   Advanced user management and a credit-based system for API usage.
*   The ability to save and reuse extraction templates.
