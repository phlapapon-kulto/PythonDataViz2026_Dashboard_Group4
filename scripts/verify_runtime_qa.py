import asyncio
import json
import os
import subprocess
import time
import urllib.request
import websockets
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INDEX_FILE_URL = "file:///" + os.path.join(WORKSPACE_DIR, "index.html").replace("\\", "/")
LOCAL_HTTP_URL = "http://127.0.0.1:8080/index.html"
LIVE_GH_URL = "https://phlapapon-kulto.github.io/PythonDataViz2026_Dashboard_Group4/"

class BrowserRunner:
    def __init__(self, port=9222):
        self.port = port
        self.proc = None

    def start(self):
        cmd = [
            CHROME_PATH,
            "--headless=new",
            f"--remote-debugging-port={self.port}",
            "--disable-gpu",
            "--no-sandbox",
            "--allow-file-access-from-files",
            "--disable-web-security",
            "--user-data-dir=" + os.path.join(WORKSPACE_DIR, f"temp_chrome_profile_{self.port}")
        ]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(30):
            time.sleep(0.3)
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json", timeout=1) as resp:
                    if resp.status == 200:
                        return
            except Exception:
                pass
        raise RuntimeError("Chrome failed to start on debugging port")

    def stop(self):
        if self.proc:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=3)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass

    def get_tab_ws_url(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json") as resp:
            tabs = json.loads(resp.read().decode())
            for tab in tabs:
                if tab.get("type") == "page":
                    return tab["webSocketDebuggerUrl"]
            with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json/new") as new_resp:
                new_tab = json.loads(new_resp.read().decode())
                return new_tab["webSocketDebuggerUrl"]

class CDPClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self.req_id = 0
        self.responses = {}
        self.events = []
        self.console_errors = []
        self.network_requests = []
        self.network_failed = []
        self.listen_task = None

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=20*1024*1024)
        self.listen_task = asyncio.create_task(self._listen())

    async def _listen(self):
        try:
            async for msg in self.ws:
                data = json.loads(msg)
                if "id" in data:
                    self.responses[data["id"]] = data
                elif "method" in data:
                    method = data["method"]
                    params = data.get("params", {})
                    self.events.append(data)
                    if method == "Runtime.consoleAPICalled":
                        c_type = params.get("type")
                        text = " ".join([str(arg.get("value", "")) for arg in params.get("args", [])])
                        if c_type in ["error", "exception"]:
                            self.console_errors.append((c_type, text))
                    elif method == "Runtime.exceptionThrown":
                        details = params.get("exceptionDetails", {})
                        text = details.get("text", "")
                        if "exception" in details:
                            text += " " + str(details["exception"].get("description", ""))
                        self.console_errors.append(("exception", text))
                    elif method == "Network.requestWillBeSent":
                        req = params.get("request", {})
                        url = req.get("url", "")
                        if not url.startswith("chrome://") and not url.startswith("chrome-untrusted://"):
                            self.network_requests.append(url)
                    elif method == "Network.loadingFailed":
                        self.network_failed.append(params.get("errorText", "") + " URL: " + str(params.get("canceled", False)))
        except asyncio.CancelledError:
            pass
        except Exception:
            pass

    async def send(self, method, params=None):
        self.req_id += 1
        msg_id = self.req_id
        payload = {"id": msg_id, "method": method}
        if params:
            payload["params"] = params
        await self.ws.send(json.dumps(payload))
        for _ in range(100):
            if msg_id in self.responses:
                resp = self.responses.pop(msg_id)
                if "error" in resp:
                    raise RuntimeError(f"CDP Error in {method}: {resp['error']}")
                return resp.get("result", {})
            await asyncio.sleep(0.05)
        raise TimeoutError(f"Timed out waiting for response to {method}")

    async def eval_js(self, expression):
        result = await self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        if "exceptionDetails" in result:
            err = result["exceptionDetails"].get("text", "")
            if "exception" in result["exceptionDetails"]:
                err += " " + str(result["exceptionDetails"]["exception"].get("description", ""))
            raise RuntimeError(f"JS Eval Error: {err}")
        return result.get("result", {}).get("value")

    async def close(self):
        if self.listen_task:
            self.listen_task.cancel()
        if self.ws:
            await self.ws.close()

async def run_environment_qa(name, target_url, port=9222):
    print(f"\n========================================================")
    print(f"RUNNING QA TEST SUITE: {name}")
    print(f"URL: {target_url}")
    print(f"========================================================")
    
    runner = BrowserRunner(port=port)
    runner.start()
    
    results = {
        "env": name,
        "url": target_url,
        "checks": [],
        "errors": [],
        "charts": {},
        "kpis": {}
    }
    
    try:
        ws_url = runner.get_tab_ws_url()
        client = CDPClient(ws_url)
        await client.connect()
        
        await client.send("Page.enable")
        await client.send("Network.enable")
        await client.send("Runtime.enable")
        
        # Clear any prior background requests before actual navigation
        client.network_requests.clear()
        client.console_errors.clear()
        
        print(f"[*] Navigating to {target_url}...")
        await client.send("Page.navigate", {"url": target_url})
        await asyncio.sleep(3.0) # Allow DOM & scripts to execute
        
        # 1. Network Requests check
        page_requests = list(client.network_requests)
        print(f"[+] Total page requests sent: {len(page_requests)}")
        results["checks"].append({
            "name": "Network Assets Loaded",
            "passed": len(page_requests) > 0,
            "details": f"Total requests: {len(page_requests)}: {page_requests[:8]}"
        })
        
        # Check for external scripts/links in standalone offline mode
        if "Offline" in name:
            external_scripts = [u for u in page_requests if not u.startswith("file://") and not u.startswith("data:") and not "fonts.googleapis" in u and not "fonts.gstatic" in u]
            passed_ext = len(external_scripts) == 0
            results["checks"].append({
                "name": "Zero External JavaScript/CSS Execution",
                "passed": passed_ext,
                "details": f"External scripts: {external_scripts}"
            })
            print(f"[+] Zero External Script Dependencies: {'PASS' if passed_ext else 'FAIL'}")

        # 2. Console Errors check
        actual_errors = [e for e in client.console_errors if e[0] in ["error", "exception"]]
        passed_errs = len(actual_errors) == 0
        results["checks"].append({
            "name": "Zero JavaScript Console Errors",
            "passed": passed_errs,
            "details": f"Total errors: {len(actual_errors)}"
        })
        print(f"[+] Zero JS Errors: {'PASS' if passed_errs else 'FAIL'} ({len(actual_errors)} errors)")

        # 3. Vendor Libraries check
        vendor_check = await client.eval_js("""
            ({
                hasTailwind: typeof tailwind !== 'undefined',
                hasChart: typeof Chart !== 'undefined',
                hasLucide: typeof lucide !== 'undefined',
                svgLucideCount: document.querySelectorAll('svg.lucide').length,
                hasDataAIID: typeof DATA_AIID !== 'undefined',
                aiCount: (typeof DATA_AIID !== 'undefined') ? DATA_AIID.length : 0,
                hasDataFin: typeof DATA_FINANCIAL !== 'undefined',
                finCount: (typeof DATA_FINANCIAL !== 'undefined') ? DATA_FINANCIAL.length : 0,
                hasDataWeekly: typeof DATA_WEEKLY !== 'undefined',
                weeklyCount: (typeof DATA_WEEKLY !== 'undefined') ? DATA_WEEKLY.length : 0,
                reportedWeeks: (typeof DATA_WEEKLY !== 'undefined') ? DATA_WEEKLY.filter(w => w.acsc_reported).length : 0
            })
        """)
        passed_vendor = vendor_check['hasTailwind'] and vendor_check['hasChart'] and vendor_check['hasLucide'] and vendor_check['svgLucideCount'] > 0
        results["checks"].append({
            "name": "Vendor Libraries Loaded (Tailwind, Chart.js, Lucide SVG)",
            "passed": passed_vendor,
            "details": f"Tailwind={vendor_check['hasTailwind']}, Chart={vendor_check['hasChart']}, Lucide={vendor_check['hasLucide']}, IconsRendered={vendor_check['svgLucideCount']}"
        })
        print(f"[+] Vendor Libraries: {'PASS' if passed_vendor else 'FAIL'}")

        # 4. Data Store check
        passed_datastore = (vendor_check['aiCount'] == 1749 and 
                            vendor_check['finCount'] == 2514 and 
                            vendor_check['reportedWeeks'] == 48 and 
                            vendor_check['weeklyCount'] == 409)
        results["checks"].append({
            "name": "Data Store Preloaded (1,749 AIID, 2,514 AFNC, 48 ACSC weeks, 409 panel weeks)",
            "passed": passed_datastore,
            "details": f"AIID={vendor_check['aiCount']}, AFNC={vendor_check['finCount']}, ReportedWeeks={vendor_check['reportedWeeks']}, TotalPanelWeeks={vendor_check['weeklyCount']}"
        })
        print(f"[+] Data Store Integrity: {'PASS' if passed_datastore else 'FAIL'}")

        # 5. TAB 1: AI Risks KPIs & Charts
        tab1_kpi = await client.eval_js("""
            ({
                total: document.getElementById('tab1-kpi-total') ? document.getElementById('tab1-kpi-total').innerText.trim() : null,
                casualties: document.getElementById('tab1-kpi-casualties') ? document.getElementById('tab1-kpi-casualties').innerText.trim() : null,
                growth: document.getElementById('tab1-kpi-growth') ? document.getElementById('tab1-kpi-growth').innerText.trim() : null,
                domains: document.getElementById('tab1-kpi-domains') ? document.getElementById('tab1-kpi-domains').innerText.trim() : null,
            })
        """)
        results["kpis"]["tab1"] = tab1_kpi
        passed_tab1_kpi = tab1_kpi['total'] == "1,749" and tab1_kpi['casualties'] == "21" and tab1_kpi['domains'] == "7"
        results["checks"].append({
            "name": "Tab 1 KPIs (1,749 incidents, 21 casualties, 7 active risk domains)",
            "passed": passed_tab1_kpi,
            "details": str(tab1_kpi)
        })
        print(f"[+] Tab 1 KPIs: {'PASS' if passed_tab1_kpi else 'FAIL'} -> {tab1_kpi}")

        # Tab 1 Charts
        tab1_charts = await client.eval_js("""
            ({
                topDomains: !!(Chart.getChart('chart-top-domains')),
                timeline: !!(Chart.getChart('chart-incidents-timeline')),
                riskDist: !!(Chart.getChart('chart-risk-distribution')),
                regional: !!(Chart.getChart('chart-regional-distribution')),
            })
        """)
        results["charts"].update(tab1_charts)
        passed_tab1_charts = all(tab1_charts.values())
        results["checks"].append({
            "name": "Tab 1 Charts (1: Top Domains, 2: Timeline, 3: Risk Donut, 4: Regional Bar)",
            "passed": passed_tab1_charts,
            "details": str(tab1_charts)
        })
        print(f"[+] Tab 1 Charts 1-4: {'PASS' if passed_tab1_charts else 'FAIL'}")

        # Tab 1 Filter Execution
        tab1_filter_test = await client.eval_js("""
            (function() {
                var select = document.getElementById('tab1-filter-year');
                select.value = '2024';
                applyTab1Filters();
                var filteredTotal = document.getElementById('tab1-kpi-total').innerText.trim();
                
                // Search filter test
                var searchInput = document.getElementById('tab1-filter-search');
                searchInput.value = 'autonomous';
                applyTab1Filters();
                var searchedTotal = document.getElementById('tab1-kpi-total').innerText.trim();
                
                // Reset
                resetTab1Filters();
                var resetTotal = document.getElementById('tab1-kpi-total').innerText.trim();
                
                return {
                    filtered2024: filteredTotal,
                    searchedAutonomous: searchedTotal,
                    resetTotal: resetTotal
                };
            })()
        """)
        passed_tab1_filter = (tab1_filter_test.get('filtered2024') == "310" and 
                              int(tab1_filter_test.get('searchedAutonomous')) < 310 and
                              tab1_filter_test.get('resetTotal') == "1,749")
        results["checks"].append({
            "name": "Tab 1 Interactive Filter & Search Reactivity",
            "passed": passed_tab1_filter,
            "details": str(tab1_filter_test)
        })
        print(f"[+] Tab 1 Filter Test: {'PASS' if passed_tab1_filter else 'FAIL'} -> {tab1_filter_test}")

        # 6. SWITCH TO TAB 2: FINANCIAL FAKE NEWS
        print(f"[*] Navigating to Tab 2...")
        await client.eval_js("switchTab('tab2')")
        await asyncio.sleep(1.0)
        
        tab2_state = await client.eval_js("""
            ({
                tab1Hidden: document.getElementById('tab1-content').classList.contains('hidden'),
                tab2Hidden: document.getElementById('tab2-content').classList.contains('hidden'),
                totalChecked: document.getElementById('tab2-kpi-total').innerText.trim(),
                fakeCount: document.getElementById('tab2-kpi-fake').innerText.trim(),
                distortedCount: document.getElementById('tab2-kpi-distorted').innerText.trim(),
                fakePct: document.getElementById('tab2-kpi-pct').innerText.trim(),
                avgViews: document.getElementById('tab2-kpi-views').innerText.trim(),
                tableRowCount: document.querySelectorAll('#news-table-body tr').length,
                pageInfo: document.getElementById('table-page-info').innerText.trim()
            })
        """)
        results["kpis"]["tab2"] = tab2_state
        passed_tab2_kpi = (tab2_state['tab2Hidden'] == False and 
                           tab2_state['totalChecked'] == "2,514" and 
                           tab2_state['fakeCount'] == "2,339" and 
                           tab2_state['fakePct'] == "93.04%" and
                           tab2_state['tableRowCount'] == 10)
        results["checks"].append({
            "name": "Tab 2 KPIs & Table (2,514 checked, 2,339 fake, 93.04%, 10 rows page 1)",
            "passed": passed_tab2_kpi,
            "details": str(tab2_state)
        })
        print(f"[+] Tab 2 KPIs & Table: {'PASS' if passed_tab2_kpi else 'FAIL'} -> {tab2_state}")

        # Tab 2 Charts
        tab2_charts = await client.eval_js("""
            ({
                fakeTopics: !!(Chart.getChart('chart-fake-topics')),
                verdictDonut: !!(Chart.getChart('chart-verdict-donut')),
                monthlyTrends: !!(Chart.getChart('chart-monthly-trends')),
                topViews: !!(Chart.getChart('chart-top-views')),
            })
        """)
        results["charts"].update(tab2_charts)
        passed_tab2_charts = all(tab2_charts.values())
        results["checks"].append({
            "name": "Tab 2 Charts (5: Fake Topics, 6: Verdict Donut, 7: Monthly Trends, 8: Top Views)",
            "passed": passed_tab2_charts,
            "details": str(tab2_charts)
        })
        print(f"[+] Tab 2 Charts 5-8: {'PASS' if passed_tab2_charts else 'FAIL'}")

        # Tab 2 Pagination Test
        tab2_pagination = await client.eval_js("""
            (function() {
                var p1 = document.getElementById('table-page-info').innerText.trim();
                nextTablePage();
                var p2 = document.getElementById('table-page-info').innerText.trim();
                prevTablePage();
                var p3 = document.getElementById('table-page-info').innerText.trim();
                return { page1: p1, page2: p2, page3: p3 };
            })()
        """)
        passed_pag = "1" in tab2_pagination['page1'] and "2" in tab2_pagination['page2'] and "1" in tab2_pagination['page3']
        results["checks"].append({
            "name": "Tab 2 Table Pagination (Page 1 -> Page 2 -> Page 1)",
            "passed": passed_pag,
            "details": str(tab2_pagination)
        })
        print(f"[+] Tab 2 Pagination: {'PASS' if passed_pag else 'FAIL'} -> {tab2_pagination}")

        # 7. SWITCH TO TAB 3: SCAM CORRELATION
        print(f"[*] Navigating to Tab 3...")
        await client.eval_js("switchTab('tab3')")
        await asyncio.sleep(1.0)
        
        tab3_charts = await client.eval_js("""
            ({
                weeklyDual: !!(Chart.getChart('chart-weekly-dual-trend')),
                scatterCases: !!(Chart.getChart('chart-scatter-cases')),
                scatterLoss: !!(Chart.getChart('chart-scatter-loss')),
            })
        """)
        results["charts"].update(tab3_charts)
        passed_tab3_charts = all(tab3_charts.values())
        results["checks"].append({
            "name": "Tab 3 Charts (9: Dual-Axis Line, 10: Scatter Cases, 11: Scatter Loss)",
            "passed": passed_tab3_charts,
            "details": str(tab3_charts)
        })
        print(f"[+] Tab 3 Charts 9-11: {'PASS' if passed_tab3_charts else 'FAIL'}")

        # Tab 3 Outlier Sensitivity Pearson Toggle
        tab3_outlier_test = await client.eval_js("""
            (function() {
                // Mode 1: Include Outlier (Full 48 weeks)
                setOutlierMode(false);
                var rAll = document.getElementById('corr-cases-r').innerText.trim();
                var pAll = document.getElementById('corr-cases-p').innerText.trim();
                var badgeAll = document.getElementById('corr-cases-strength').innerText.trim();
                var casesWeeklyAll = document.getElementById('tab3-kpi-cases-weekly').innerText.trim();
                
                // Mode 2: Exclude Outlier (Clean 47 weeks)
                setOutlierMode(true);
                var rClean = document.getElementById('corr-cases-r').innerText.trim();
                var pClean = document.getElementById('corr-cases-p').innerText.trim();
                var badgeClean = document.getElementById('corr-cases-strength').innerText.trim();
                var casesWeeklyClean = document.getElementById('tab3-kpi-cases-weekly').innerText.trim();
                
                return {
                    allWeeks: { r: rAll, p: pAll, badge: badgeAll, avgCases: casesWeeklyAll },
                    cleanWeeks: { r: rClean, p: pClean, badge: badgeClean, avgCases: casesWeeklyClean }
                };
            })()
        """)
        passed_tab3_toggle = ("-0.0903" in tab3_outlier_test['allWeeks']['r'] and 
                              "0.5377" in tab3_outlier_test['cleanWeeks']['r'] and
                              "ไม่มีนัยสำคัญ" in tab3_outlier_test['allWeeks']['badge'] and
                              "มีนัยสำคัญ" in tab3_outlier_test['cleanWeeks']['badge'])
        results["checks"].append({
            "name": "Tab 3 Outlier Sensitivity Pearson Toggle (All: r=-0.0903 vs Clean: r=+0.5377)",
            "passed": passed_tab3_toggle,
            "details": str(tab3_outlier_test)
        })
        print(f"[+] Tab 3 Outlier Toggle: {'PASS' if passed_tab3_toggle else 'FAIL'} -> {tab3_outlier_test}")

        # Total 11 Charts check
        total_active_charts = len(results["charts"])
        passed_all_charts = (total_active_charts == 11 and all(results["charts"].values()))
        results["checks"].append({
            "name": "All 11 Dashboard Charts Initialized & Active in Browser",
            "passed": passed_all_charts,
            "details": f"11/11 charts: {list(results['charts'].keys())}"
        })
        print(f"[+] All 11 Charts Verified: {'PASS' if passed_all_charts else 'FAIL'} ({total_active_charts}/11)")

        await client.close()

    finally:
        runner.stop()

    return results

async def main():
    print("="*60)
    print("STARTING FULL PRODUCTION BROWSER RUNTIME & DEPLOYMENT QA")
    print("="*60)
    
    # 1. Standalone Offline Mode (file://)
    res_offline = await run_environment_qa("Standalone Offline (file://)", INDEX_FILE_URL, port=9222)
    
    # 2. Local HTTP Server Mode (http://127.0.0.1:8080)
    http_proc = subprocess.Popen(["python", "-m", "http.server", "8080"], cwd=WORKSPACE_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    try:
        res_local = await run_environment_qa("Local Web Server (http://127.0.0.1:8080)", LOCAL_HTTP_URL, port=9223)
    finally:
        http_proc.terminate()
        
    # 3. Live GitHub Pages Deployment Mode
    res_gh = await run_environment_qa("Live GitHub Pages (Production)", LIVE_GH_URL, port=9224)
    
    # Save combined results
    output_path = os.path.join(WORKSPACE_DIR, "reports", "runtime_qa_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "offline": res_offline,
            "local_http": res_local,
            "github_pages": res_gh
        }, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] Results successfully written to {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
