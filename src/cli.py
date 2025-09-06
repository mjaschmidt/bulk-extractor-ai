# src/cli.py
import os
import json
from datetime import datetime, timezone
import pathlib
import argparse

from file_processing import extract_email_body
from llm_service import GeminiClient

def save_individual_json(data_str: str, output_path: str, source_filename: str) -> bool:
    """Parses and saves data for a single file."""
    try:
        if data_str.strip().startswith("```json"):
            data_str = data_str.strip()[7:-3]
        
        # Handles cases where the LLM returns 'null' or an empty string.
        if not data_str.strip() or data_str.strip().lower() == 'null':
            extracted_data = None
        else:
            extracted_data = json.loads(data_str)

        # --- CHANGED: This is our new, universal relevance check ---
        # Instead of looking for a "groceries" key, we now check if the LLM
        # returned any data at all (i.e., it's not None or an empty dictionary {}).
        if not extracted_data:
            print(f"No relevant data found in {source_filename}. Skipping file creation.")
            return False

        final_output = {
            "metadata": {
                "extraction_timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "source_file": source_filename,
            },
            "extracted_data": extracted_data,
        }
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

def main():
    """The main function to run the CLI application."""
    parser = argparse.ArgumentParser(description="Intelligent File Extractor using Gemini AI.")
    # ... (The argparse section remains exactly the same) ...
    parser.add_argument("--input-folder", type=str, required=True, help="Path to the folder containing .eml files.")
    parser.add_argument("--output-folder", type=str, required=True, help="Path to the folder where output .json files will be saved.")
    parser.add_argument("--prompt-file", type=str, required=True, help="Path to a .txt file with the extraction prompt.")
    parser.add_argument("--output-method", type=str, choices=["one_per_file", "single_file", "one_per_relevant_file"], default="one_per_file", help="Defines how output files are generated.")
    args = parser.parse_args()

    project_root = pathlib.Path(__file__).parent.parent
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")

    try:
        with open(args.prompt_file, 'r', encoding='utf-8') as f:
            base_prompt = f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {args.prompt_file}")
        return

    print("--- Starting Extraction Process ---")
    
    try:
        gemini_client = GeminiClient()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return

    all_results_for_single_file = []
    try:
        files_to_process = os.listdir(args.input_folder)
    except FileNotFoundError:
        print(f"Error: Input folder not found at {args.input_folder}")
        return

    for filename in files_to_process:
        if filename.endswith(".eml"):
            print(f"\nProcessing file: {filename}...")
            input_eml_path = os.path.join(args.input_folder, filename)
            
            clean_text = extract_email_body(input_eml_path)
            if not clean_text:
                print(f"Could not extract content from {filename}. Skipping.")
                continue

            full_prompt = f"{base_prompt}\n\nHere is the email content:\n\n---\n{clean_text}\n---"
            api_response = gemini_client.generate_content(full_prompt)

            if not api_response:
                print(f"No response from API for {filename} after all retries. Skipping.")
                continue

            if args.output_method in ["one_per_file", "one_per_relevant_file"]:
                output_json_path = os.path.join(args.output_folder, filename.replace(".eml", ".json"))
                saved = save_individual_json(api_response, output_json_path, filename)
                if args.output_method == "one_per_file" and not saved:
                    # If save_individual_json returned False because the data was empty,
                    # we create a file with just the metadata but empty extracted_data.
                    empty_output = {
                        "metadata": {
                            "extraction_timestamp_utc": datetime.now(timezone.utc).isoformat(),
                            "source_file": filename,
                        },
                        "extracted_data": None
                    }
                    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
                    with open(output_json_path, "w", encoding="utf-8") as f:
                        json.dump(empty_output, f, indent=4, ensure_ascii=False)

            elif args.output_method == "single_file":
                try:
                    if api_response.strip().startswith("```json"):
                        api_response = api_response.strip()[7:-3]
                    
                    if not api_response.strip() or api_response.strip().lower() == 'null':
                        data = None
                    else:
                        data = json.loads(api_response)

                    # --- CHANGED: This is our new, universal check and append logic ---
                    # We now check if the data object is truthy (not None, not {})
                    # and append the entire data object, not just a "groceries" key.
                    if data:
                        all_results_for_single_file.append({
                            "source_file": filename,
                            "data": data # Append the whole object
                        })
                        print(f"Found relevant data in {filename}. Added to results.")
                except json.JSONDecodeError:
                    print(f"Could not decode JSON for {filename}. Skipping for single file.")

    if args.output_method == "single_file" and all_results_for_single_file:
        output_path = os.path.join(args.output_folder, "consolidated_results.json")
        final_output = {
            "metadata": {
                "extraction_timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "total_files_processed": len(files_to_process),
                "files_with_data": len(all_results_for_single_file),
            },
            "extracted_data": all_results_for_single_file,
        }
        os.makedirs(args.output_folder, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=4, ensure_ascii=False)
        print(f"\nSaved all consolidated data to {output_path}")

    print("\n--- Extraction Process Finished ---")

if __name__ == "__main__":
    main()