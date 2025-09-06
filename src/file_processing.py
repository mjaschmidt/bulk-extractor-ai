# src/file_processing.py
import email
from email.policy import default
from bs4 import BeautifulSoup

def extract_text_from_html(html_content: str) -> str:
    """
    Uses BeautifulSoup to parse HTML and extract only the visible text.

    Args:
        html_content (str): The raw HTML content of the email body.

    Returns:
        str: The clean, visible text from the HTML.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    
    # Get text and clean up whitespace
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def extract_email_body(eml_path: str) -> str | None:
    """
    Reads an .eml file, extracts the HTML body, and cleans it to get plain text.
    """
    try:
        with open(eml_path, "rb") as file:
            msg = email.message_from_binary_file(file, policy=default)
        
        raw_html = None
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/html" and "attachment" not in content_disposition:
                    # **FIX:** Using the robust get_content() method from your original code.
                    content = part.get_content()
                    raw_html = content.decode("utf-8", errors="ignore") if isinstance(content, bytes) else content
                    break # Found the main HTML body, no need to look further.
        else:
            # Not a multipart email, just get the single payload.
            content = msg.get_content()
            raw_html = content.decode("utf-8", errors="ignore") if isinstance(content, bytes) else content

        if raw_html:
            print("HTML content found. Extracting visible text...")
            return extract_text_from_html(raw_html)
        else:
            print("No HTML content found in the email.")
            return None

    except FileNotFoundError:
        print(f"Error: The file at {eml_path} was not found.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading the email: {e}")
        return None