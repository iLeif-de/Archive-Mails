import imaplib
import email
import os
import yaml
import logging
import random
import string
import base64
import quopri
from email.header import decode_header
from bs4 import BeautifulSoup
from unidecode import unidecode

# Load configuration from YAML file
CONFIG_FILE = "config.yaml"
with open(CONFIG_FILE, "r") as file:
    config = yaml.safe_load(file)

# Extract IMAP server details and credentials from config
IMAP_SERVER = config["imap_server"]
EMAIL_USER = config["username"]
EMAIL_PASS = config["password"]
ARCHIVE_DIR = config["output_folder"]

# Ensure the archive directory exists
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# Configure logging for tracking operations
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def safe_filename(name):
    """Sanitize filenames to be filesystem-safe by removing invalid characters."""
    return "".join(c for c in unidecode(name) if c.isalnum() or c in (" ", "-", "_")).rstrip()

def generate_random_string(length=10):
    """Generate a random string for unique filenames."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def decode_content(payload, encoding):
    """Decode email content based on its encoding."""
    if encoding == 'base64':
        return base64.b64decode(payload).decode(errors='ignore')
    elif encoding == 'quoted-printable':
        return quopri.decodestring(payload).decode(errors='ignore')
    return payload

def save_email_content(email_folder, email_obj):
    """Extract and save email contents including text, HTML, and attachments."""
    # Get the folder name to use for the files
    folder_name = os.path.basename(email_folder)
    
    # Save the full raw email as an .eml file with the folder name
    raw_email_path = os.path.join(email_folder, f"{folder_name}.eml")
    with open(raw_email_path, "wb") as f:
        f.write(email_obj.as_bytes())

    html_content = None
    text_content = None
    attachments = []

    # Iterate through each part of the email
    for part in email_obj.walk():
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition"))

        if "attachment" in content_disposition:
            # Handle email attachments
            filename = part.get_filename()
            if filename:
                filename = safe_filename(filename)
                filepath = os.path.join(email_folder, filename)
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                attachments.append(filename)
        elif content_type == "text/html":
            # Extract HTML content if available
            html_content = decode_content(part.get_payload(), part.get("Content-Transfer-Encoding", "")).strip()
        elif content_type == "text/plain" and not html_content:
            # Extract plain text content if HTML is not available
            text_content = decode_content(part.get_payload(), part.get("Content-Transfer-Encoding", "")).strip()

    # Process and save HTML content
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        for img in soup.find_all("img"):
            # Replace inline CID images with local file references
            if img.get("src", "").startswith("cid:"):
                cid = img["src"].replace("cid:", "").strip("<>")
                for part in email_obj.walk():
                    if part.get("Content-ID", "").strip("<>") == cid:
                        filename = generate_random_string() + ".jpg"
                        filepath = os.path.join(email_folder, filename)
                        with open(filepath, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        img["src"] = filename

        # Save HTML content with the folder name
        with open(os.path.join(email_folder, f"{folder_name}.html"), "w", encoding="utf-8") as f:
            f.write(str(soup))

    # Save plain text content with the folder name if extracted
    if text_content:
        with open(os.path.join(email_folder, f"{folder_name}.txt"), "w", encoding="utf-8") as f:
            f.write(text_content)

def process_emails():
    """Main function to connect to IMAP, fetch, and process unread emails."""
    try:
        # Establish a secure IMAP connection
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        # Search for unread emails
        result, data = mail.search(None, "UNSEEN")
        email_ids = data[0].split()

        for e_id in email_ids:
            # Fetch the email
            result, msg_data = mail.fetch(e_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Decode and sanitize the email subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors='ignore')
            subject = safe_filename(subject) or "No_Subject"

            # Create folder name using only the sanitized subject
            email_folder = os.path.join(ARCHIVE_DIR, subject)

            # Ensure unique folder name by appending a number if necessary
            folder_counter = 1
            original_folder = email_folder
            while os.path.exists(email_folder):
                email_folder = f"{original_folder}_{folder_counter}"
                folder_counter += 1

            os.makedirs(email_folder, exist_ok=True)

            # Save the email content and attachments
            save_email_content(email_folder, msg)

            # Mark email as read on IMAP server
            mail.store(e_id, "+FLAGS", "\\Seen")

            logging.info(f"Processed email: {subject}")

        # Logout from IMAP server
        mail.logout()

    except Exception as e:
        logging.error(f"Error processing emails: {e}")

# Entry point of the script
if __name__ == "__main__":
    process_emails()
