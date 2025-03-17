import os
import sys
import requests
import zipfile
import tarfile
import json
import PyPDF2
import pandas as pd
import re

# Check if user provided an input file
if len(sys.argv) < 2:
    print("Usage: python3 script.py <input_file>")
    sys.exit(1)

input_file = sys.argv[1]  # Get file from command-line argument

# Check if the file exists
if not os.path.exists(input_file):
    print(f"❌ Error: File '{input_file}' not found.")
    sys.exit(1)

# Create folder for downloaded files
download_folder = "files_scanned"
os.makedirs(download_folder, exist_ok=True)

# Supported file extensions
supported_extensions = [
    "pdf", "json", "xls", "xlsx", "xml", "csv", "txt", "sql", "doc", "docx",
    "log", "yaml", "yml", "tar.gz", "gz", "tgz", "zip", "7z", "rar", "bak",
    "cache", "secret", "db", "backup", "config", "md", "md5", "exe", "tar",
    "key", "crt", "pub"
]

# Define sensitive keywords to search (Updated with PII)
sensitive_keywords = [
    # Authentication & Secrets
    "password", "api_key", "secret", "private_key", "jwt", "access_token", 
    "ssh_key", "auth_token", "bearer_token", "session_id", "auth_code", 
    "csrf_token", "otp", "encryption_key", "token", "security_code",

    # Financial Data
    "credit_card", "cvv", "bank_account", "iban", "swift", "bic", "tax_id",

    # Personal Identifiable Information (PII)
    "ssn", "social_security", "date_of_birth", "passport", "driving_license", 
    "pan_card", "aadhaar", "voter_id", "personal_number", "dob", "user_id",

    # Internal & Confidential
    "internal_use_only", "confidential", "do_not_share", "proprietary", 
    "classified", "restricted", "sensitive_data"
]

# Function to download files
def download_file(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            filename = os.path.join(download_folder, url.split("/")[-1])
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"✅ Downloaded: {filename}")
            return filename
        else:
            print(f"❌ Failed: {url} ({response.status_code})")
            return None
    except requests.exceptions.RequestException:
        print(f"❌ Error fetching: {url}")
        return None

# Function to extract text from different file types
def extract_text(file_path):
    try:
        file_extension = file_path.split(".")[-1].lower()
        text = ""

        if file_extension == "pdf":
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"

        elif file_extension in ["json"]:
            with open(file_path, "r", encoding="utf-8") as f:
                text = json.dumps(json.load(f))

        elif file_extension in ["csv", "xlsx", "xls"]:
            df = pd.read_csv(file_path, encoding="utf-8", errors="ignore") if "csv" in file_extension else pd.read_excel(file_path)
            text = df.to_string()

        elif file_extension in ["xml", "sql", "txt", "log", "yaml", "yml", "md", "config"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        elif file_extension in ["tar.gz", "gz", "tgz"]:
            with tarfile.open(file_path, "r:*") as tar:
                for member in tar.getmembers():
                    f = tar.extractfile(member)
                    if f:
                        text += f.read().decode("utf-8", errors="ignore") + "\n"

        elif file_extension in ["zip", "7z", "rar"]:
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                for name in zip_ref.namelist():
                    with zip_ref.open(name) as f:
                        text += f.read().decode("utf-8", errors="ignore") + "\n"

        return text.lower()

    except Exception:
        print(f"❌ Error reading: {file_path}")
        return ""

# Function to scan for sensitive data
def scan_for_sensitive_data(text):
    for keyword in sensitive_keywords:
        if re.search(rf"\b{keyword}\b", text, re.IGNORECASE):
            return True
    return False

# Process Files
with open(input_file, "r") as f:
    file_urls = [url.strip() for url in f.readlines()]

for url in file_urls:
    if any(url.endswith(f".{ext}") for ext in supported_extensions):
        file_path = download_file(url)
        if file_path:
            extracted_text = extract_text(file_path)
            if scan_for_sensitive_data(extracted_text):
                print(f"🚨 Sensitive Data Found in: {file_path}")
            else:
                print(f"🔍 No Sensitive Data in: {file_path}")

print("✅ Scan Complete!")
