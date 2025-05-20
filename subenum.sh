#!/bin/bash

# === Check input ===
if [ -z "$1" ]; then
  echo "Usage: $0 <domain>"
  exit 1
fi

domain="$1"
outdir="subdomains/$domain"
mkdir -p "$outdir"

echo "[*] Enumerating subdomains for: $domain"
echo "[*] Saving output to: $outdir"

# === Subfinder ===
echo "[+] Running subfinder..."
subfinder -d "$domain" -silent | tee "$outdir/subfinder.txt"

# === crt.sh ===
echo "[+] Querying crt.sh..."
curl -s "https://crt.sh/?q=%25.$domain&output=json" | \
  jq -r '.[].name_value' | sed 's/\*\.//g' | tee "$outdir/crtsh.txt"

# === Combine all & deduplicate ===
echo "[+] Creating final list..."
cat "$outdir"/subfinder.txt "$outdir"/crtsh.txt | \
  sort -u > "$outdir/final_subdomains.txt"

echo "✅ Done! Results in $outdir/final_subdomains.txt"
