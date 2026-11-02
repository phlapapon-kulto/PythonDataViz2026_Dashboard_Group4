import urllib.request
import json

url = 'https://api.github.com/repos/phlapapon-kulto/PythonDataViz2026_Dashboard_Group4/actions/runs'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    runs = data.get('workflow_runs', [])
    ci_run = [r for r in runs if r['name'] == 'CI Test & GitHub Pages Deploy'][0]
    print(f"Run ID: {ci_run['id']}, Jobs URL: {ci_run['jobs_url']}")

jobs_req = urllib.request.Request(ci_run['jobs_url'], headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(jobs_req) as resp:
    jobs_data = json.loads(resp.read().decode('utf-8'))
    for j in jobs_data.get('jobs', []):
        print(f"Job: {j['name']} | Status: {j['status']} | Conclusion: {j['conclusion']}")
        for step in j.get('steps', []):
            print(f"  Step: {step['name']} | Conclusion: {step['conclusion']}")
