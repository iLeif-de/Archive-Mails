I understand you’re seeking the complete content of the README.md file for your Email Archiver project. Here it is:

# Email Archiver

## Overview
Email Archiver is a Python script that connects to an IMAP email server, retrieves emails, and stores them locally in a structured format. The script decodes email content, handles attachments, and ensures safe filenames for storage.

## Features
- Connects to an IMAP server
- Retrieves and processes emails
- Decodes text and HTML content
- Handles attachments
- Stores emails in a structured format
- Configurable via a YAML file

## Requirements
- Python 3.x
- Required dependencies (install via `pip install -r requirements.txt`):
  - `PyYAML`
  - `beautifulsoup4`
  - `unidecode`

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/email-archiver.git
   cd email-archiver

	2.	Create a virtual environment:

python3 -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`


	3.	Install dependencies:

pip install -r requirements.txt


	4.	Configure the script:
	•	Edit the config.yaml file with your IMAP server details and archive directory.

Configuration

The script uses a config.yaml file to store configuration details:

imap_server: "imap.example.com"
username: "your-email@example.com"
password: "your-email-password"
output_folder: "./emails"

Usage

Run the script using:

python Email_Archiver.py

Scheduling with launchd on macOS

To run this script every hour on macOS, you can use launchd. Follow these steps:
	1.	Create a plist file:
	•	Open Terminal and create a new file in ~/Library/LaunchAgents/:

nano ~/Library/LaunchAgents/com.email.archiver.plist


	2.	Add the following content:

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>Label</key>
        <string>com.email.archiver</string>
        <key>ProgramArguments</key>
        <array>
            <string>/path/to/your/virtualenv/bin/python</string>
            <string>/path/to/email-archiver/Email_Archiver.py</string>
        </array>
        <key>StartInterval</key>
        <integer>3600</integer> <!-- Runs every hour -->
        <key>RunAtLoad</key>
        <true/>
        <key>WorkingDirectory</key>
        <string>/path/to/email-archiver</string>
        <key>StandardOutPath</key>
        <string>/tmp/email_archiver.out</string>
        <key>StandardErrorPath</key>
        <string>/tmp/email_archiver.err</string>
    </dict>
</plist>

Note:
	•	Replace /path/to/your/virtualenv/bin/python with the absolute path to the Python interpreter in your virtual environment. For example, /Users/yourusername/email-archiver/env/bin/python.
	•	Replace /path/to/email-archiver/Email_Archiver.py with the absolute path to the Email_Archiver.py script.
	•	Ensure all paths are absolute to prevent issues with launchd.

	3.	Load the job:

launchctl load ~/Library/LaunchAgents/com.email.archiver.plist

To unload the job:

launchctl unload ~/Library/LaunchAgents/com.email.archiver.plist



Important Considerations:
	•	Absolute Paths: Ensure all paths in the .plist file are absolute. Relative paths can cause the job to fail.
	•	Permissions: Ensure your script and the Python interpreter have the necessary execute permissions. You can set the appropriate permissions using the chmod command:

chmod +x /path/to/your/virtualenv/bin/python
chmod +x /path/to/email-archiver/Email_Archiver.py


	•	Environment Variables: If your script relies on specific environment variables, you can define them within the .plist file using the <key>EnvironmentVariables</key> directive.

By following these steps, your Python script will run automatically every hour using launchd on macOS.

License

This project is licensed under the MIT License.

You can copy and paste this content into a file named `README.md` in your project directory. If you need further assistance or modifications, feel free to ask! 