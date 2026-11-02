import urllib.request
import json

url = 'https://api.github.com/repos/phlapapon-kulto/PythonDataViz2026_Dashboard_Group4/actions/runs'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print('Total workflow runs:', data.get('total_count', 0))
        for r in data.get('workflow_runs', [])[:5]:
            msg = r['head_commit']['message'].split('\n')[0] if r.get('head_commit') else ''
            print(f"Run #{r['run_number']}: {r['name']} | Status: {r['status']} | Conclusion: {r['conclusion']} | Commit: {r['head_sha'][:7]} - {msg[:50]}")
except Exception as e:
    print('GitHub API error:', str(e))
