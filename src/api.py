# src/api.py
import os
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from typing import List
import json
import io

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from fastapi.responses import StreamingResponse

# --- Import our existing modules ---
from .file_processing import extract_email_body
from .llm_service import GeminiClient

# --- Initialize the FastAPI application ---
app = FastAPI(
    title="Bulk Extractor AI",
    description="An AI-powered service to extract structured data from files.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"status": "Bulk Extractor AI is running"}

# This is the core function that was previously in cli.py. We've adapted it
# to work within the API context, taking data as arguments instead of file paths.
def process_and_save_json(data_str: str, output_path: str, source_filename: str) -> bool:
    """
    Parses the LLM's string response, enriches it with metadata, and saves it to a JSON file.
    Returns True if relevant data was found and saved, False otherwise.
    """
    try:
        # Clean up the response string if it's wrapped in markdown code blocks
        if data_str.strip().startswith("```json"):
            data_str = data_str.strip()[7:-3]
        
        # Handle cases where the LLM returns 'null' or an empty string, indicating no data.
        if not data_str.strip() or data_str.strip().lower() == 'null':
            extracted_data = None
        else:
            extracted_data = json.loads(data_str)

        # Universal relevance check: Is there any actual data to save?
        # This works for any prompt, not just groceries.
        if not extracted_data:
            print(f"No relevant data found in {source_filename}. Skipping file creation.")
            return False

        # Structure the final JSON output with metadata
        final_output = {
            "metadata": {
                "extraction_timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "source_file": source_filename,
            },
            "extracted_data": extracted_data,
        }
        
        # Ensure the directory exists before writing
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=4, ensure_ascii=False)
            
        print(f"Successfully saved extracted data to {output_path}")
        return True
        
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from AI for {source_filename}.")
        print("AI Response was:\n", data_str)
        return False
    except Exception as e:
        print(f"An unexpected error occurred while saving JSON for {source_filename}: {e}")
        return False

@app.post("/extract/")
async def create_extraction_task(
    # --- Endpoint Parameters ---
    # 1. The user's API key. We use Form(...) to get it from the form data.
    api_key: str = Form(...),
    # 2. The user's prompt.
    prompt: str = Form(...),
    # 3. The output method.
    output_method: str = Form("one_per_relevant_file"),
    # 4. The list of files to process.
    files: List[UploadFile] = File(...)
):
    """
    Handles the file extraction task:
    1. Receives files, API key, and prompt from the user.
    2. Processes each file using the core logic.
    3. Zips the results and returns them for download.
    """
    # --- Temporary Directory Management ---
    # We create a secure, temporary directory to store this specific request's
    # files. This prevents conflicts between simultaneous user requests.
    # The 'try...finally' block ensures this directory is ALWAYS cleaned up,
    # even if an error occurs.
    temp_dir = tempfile.mkdtemp()
    try:
        input_dir = os.path.join(temp_dir, "input")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(input_dir)
        os.makedirs(output_dir)

        # --- Save Uploaded Files ---
        # We save the uploaded files to our temporary input directory.
        for file in files:
            file_path = os.path.join(input_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        # --- Initialize Gemini Client (BYOK Model) ---
        # We instantiate the GeminiClient for THIS request, using the key
        # the user provided. This is the core of the "Bring Your Own Key" model.
        try:
            # We temporarily set the environment variable for the GeminiClient to find.
            os.environ["GEMINI_API_KEYS"] = api_key
            # For simplicity, we can hardcode the models or fetch from a config later.
            os.environ["GEMINI_MODELS"] = "gemini-2.5-flash-lite,gemini-2.0-flash,gemini-2.0-flash-lite,gemini-1.5-flash,gemini-1.5-flash-8b"
            gemini_client = GeminiClient()
        except ValueError as e:
            # If the key is invalid or missing, we raise an HTTP 400 Bad Request error.
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        # --- Main Processing Loop ---
        # This logic is very similar to our CLI, demonstrating code reuse.
        all_results_for_single_file = []
        
        for filename in os.listdir(input_dir):
            if filename.endswith(".eml"):
                print(f"\nProcessing file: {filename}...")
                input_eml_path = os.path.join(input_dir, filename)
                
                clean_text = extract_email_body(input_eml_path)
                if not clean_text:
                    print(f"Could not extract content from {filename}. Skipping.")
                    continue

                full_prompt = f"{prompt}\n\nHere is the email content:\n\n---\n{clean_text}\n---"
                api_response = gemini_client.generate_content(full_prompt)

                if not api_response:
                    print(f"No response from API for {filename}. Skipping.")
                    continue

                # --- Handle Different Output Methods ---
                if output_method in ["one_per_file", "one_per_relevant_file"]:
                    output_json_path = os.path.join(output_dir, filename.replace(".eml", ".json"))
                    saved = process_and_save_json(api_response, output_json_path, filename)
                    
                    if output_method == "one_per_file" and not saved:
                        # Create an empty file for the 'one_per_file' method if no data was found.
                        empty_output = {
                            "metadata": {
                                "extraction_timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                "source_file": filename,
                            },
                            "extracted_data": None
                        }
                        with open(output_json_path, "w", encoding="utf-8") as f:
                            json.dump(empty_output, f, indent=4, ensure_ascii=False)

                elif output_method == "single_file":
                    # Logic to append results for the 'single_file' method.
                    if api_response.strip() and api_response.strip().lower() != 'null':
                        try:
                            data = json.loads(api_response.strip().lstrip("```json").rstrip("```"))
                            if data:
                                all_results_for_single_file.append({
                                    "source_file": filename,
                                    "data": data
                                })
                        except json.JSONDecodeError:
                            print(f"Could not decode JSON for {filename} in single_file mode.")

        # If using 'single_file' method, save the consolidated results now.
        if output_method == "single_file" and all_results_for_single_file:
            output_path = os.path.join(output_dir, "consolidated_results.json")
            # ... (save the consolidated file as before) ...
            final_output = {
                "metadata": {
                    "extraction_timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "total_files_processed": len(files),
                    "files_with_data": len(all_results_for_single_file),
                },
                "extracted_data": all_results_for_single_file,
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_output, f, indent=4, ensure_ascii=False)

        # --- Zip the Results ---
        # We create a zip file in memory to send back to the user.
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, _, file_list in os.walk(output_dir):
                for file in file_list:
                    file_path = os.path.join(root, file)
                    zip_file.write(file_path, os.path.basename(file_path))
        
        # Move the buffer's cursor to the beginning
        zip_buffer.seek(0)

        # --- Return the Zip File for Download ---
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=extraction_results.zip"}
        )

    finally:
        # --- Cleanup ---
        # This block ALWAYS runs, ensuring we delete the temporary directory
        # and its contents after the request is complete.
        shutil.rmtree(temp_dir)
        # Unset the environment variables to not interfere with other processes
        os.environ.pop("GEMINI_API_KEYS", None)
        os.environ.pop("GEMINI_MODELS", None)