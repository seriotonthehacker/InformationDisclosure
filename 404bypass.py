import os
import sys
import re
import subprocess

# Check if the user provided a domain
if len(sys.argv) < 2:
    print("Usage: python3 script.py <domain>")
    sys.exit(1)

domain = sys.argv[1]  # Get domain from command-line argument
output_file = "out.txt"

# Fetch URLs using Wayback Machine
print(f"🔍 Fetching URLs from Wayback Machine for {domain}...")
wayback_cmd = [
    "curl", "-G", "https://web.archive.org/cdx/search/cdx",
    "--data-urlencode", f"url=*.{domain}/*",
    "--data-urlencode", "collapse=urlkey",
    "--data-urlencode", "output=text",
    "--data-urlencode", "fl=original"
]

with open(output_file, "w") as f:
    subprocess.run(wayback_cmd, stdout=f)

print(f"✅ Wayback URLs saved to {output_file}")

# Define extensions to filter
extensions = [
    "xls", "xml", "xlsx", "json", "pdf", "sql", "doc", "docx", "pptx", "txt",
    "zip", "tar.gz", "tgz", "bak", "7z", "rar", "log", "cache", "secret", "db",
    "backup", "yml", "gz", "config", "csv", "yaml", "md", "md5", "exe", "tar",
    "key", "crt", "pub"
]

# Create Output Folder
output_folder = f"sorted_urls_{domain}"
os.makedirs(output_folder, exist_ok=True)

# Read the wayback output file
try:
    with open(output_file, "r") as f:
        urls = [url.strip() for url in f.readlines()]
except FileNotFoundError:
    print(f"Error: File '{output_file}' not found.")
    sys.exit(1)

# Dictionary to store found URLs for each extension
found_urls = {ext: [] for ext in extensions}

# Process URLs and group them by extension
for url in urls:
    for ext in extensions:
        if re.search(rf"\.{ext}\b", url, re.IGNORECASE):
            found_urls[ext].append(url)

# Write only non-empty extension files
for ext, url_list in found_urls.items():
    if url_list:  # Only create file if URLs exist for this extension
        ext_file = os.path.join(output_folder, f"{ext}.txt")
        with open(ext_file, "w") as f:
            f.write("\n".join(url_list) + "\n")

print(f"✅ URLs sorted successfully inside '{output_folder}/' (Only found extensions).")