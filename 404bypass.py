import os
import sys
import re
import subprocess

# Check if the user provided at least one domain
if len(sys.argv) < 2:
    print("Usage: python3 script.py <domain1> <domain2> ...")
    sys.exit(1)

domains = sys.argv[1:]  # Get domains from command-line arguments

# Define extensions to filter (Updated)
extensions = [
    "xls", "xml", "xlsx", "json", "pdf", "sql", "doc", "docx", "pptx", "txt",
    "zip", "tar.gz", "tgz", "bak", "7z", "rar", "log", "cache", "secret", "db",
    "backup", "yml", "gz", "config", "csv", "yaml", "md", "md5", "exe", "tar",
    "key", "crt", "pub", "env", "pem", "ppk", "kdb", "kdbx", "cert", "ovpn",
    "sqlite", "sqlite3", "db3", "sqlitedb", "ini", "conf", "ps1", "sh", "bat",
    "cmd", "dockercfg", "dockerfile", "kubeconfig", "k8s", "tfvars", "out",
    "dump", "core", "pcap", "pcapng", "log.1", "log.2", "log.old", "bak.old",
    "sql.old", "wallet", "dat", "keychain", "keystore", "pyc", "pyo", "class",
    "jar", "rb", "php", "asp", "jsp", "cgi", "csproj", "vbproj", "fsproj",
    "swp", "swo", "backup", "bak2", "old", "bson", "mongodump"
]

for domain in domains:
    output_file = f"out_{domain}.txt"

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

    # Create Output Folder for the domain
    output_folder = f"sorted_urls_{domain}"
    os.makedirs(output_folder, exist_ok=True)

    # Read the wayback output file
    try:
        with open(output_file, "r") as f:
            urls = [url.strip() for url in f.readlines()]
    except FileNotFoundError:
        print(f"❌ Error: File '{output_file}' not found.")
        continue

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

    print(f"✅ URLs sorted successfully inside '{output_folder}/' for {domain} (Only found extensions).")
