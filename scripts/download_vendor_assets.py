import os
import urllib.request

repo_dir = r"c:\Users\USER\PythonDataViz2026_Dashboard_Group4"
vendor_dir = os.path.join(repo_dir, "vendor")
os.makedirs(vendor_dir, exist_ok=True)

assets = {
    "tailwindcss.js": "https://cdn.tailwindcss.com",
    "chart.umd.min.js": "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js",
    "lucide.min.js": "https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for fname, url in assets.items():
    dest = os.path.join(vendor_dir, fname)
    print(f"Downloading {fname} from {url}...")
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read()
        with open(dest, "wb") as f:
            f.write(content)
    print(f"Saved {fname} ({len(content):,} bytes) to {dest}")

print("All vendor assets downloaded successfully!")
