import os
import sys
import json

repo_dir = r"c:\Users\USER\PythonDataViz2026_Dashboard_Group4"
processed_dir = os.path.join(repo_dir, "data", "processed")

with open(os.path.join(processed_dir, "ai_incidents.json"), "r", encoding="utf-8") as f:
    aiid_data = f.read()

with open(os.path.join(processed_dir, "financial_news.json"), "r", encoding="utf-8") as f:
    fin_data = f.read()

with open(os.path.join(processed_dir, "weekly_scams.json"), "r", encoding="utf-8") as f:
    weekly_data = f.read()

data_store_js = f"""// Auto-generated production data store for AI Digital Threat Intelligence Dashboard
// Enables seamless offline execution and fast static hosting without CORS restrictions
window.DATA_AIID = {aiid_data};
window.DATA_FINANCIAL = {fin_data};
window.DATA_WEEKLY = {weekly_data};
console.log('Production datasets loaded:', {{
  aiid: window.DATA_AIID.length,
  financial: window.DATA_FINANCIAL.length,
  weekly: window.DATA_WEEKLY.length
}});
"""

data_store_path = os.path.join(processed_dir, "data_store.js")
with open(data_store_path, "w", encoding="utf-8") as f:
    f.write(data_store_js)

print(f"data_store.js generated successfully at {data_store_path} ({os.path.getsize(data_store_path):,} bytes)")
