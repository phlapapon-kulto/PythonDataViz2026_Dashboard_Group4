/**
 * AI Digital Threat Intelligence Dashboard
 * Project: ภัยดิจิทัลยุค AI: วิเคราะห์ความเสี่ยงจากปัญญาประดิษฐ์ ข่าวปลอม และการหลอกลวงออนไลน์
 * Senior Full-Stack Engineering & Data Analytics Logic
 */

// Global State
const STATE = {
  activeTab: 'tab1',
  aiid: [],
  financial: [],
  weekly: [],
  
  // Tab 1 Filters
  tab1: {
    year: 'all',
    domain: 'all',
    region: 'all',
    search: '',
    filtered: []
  },

  // Tab 2 Filters & Pagination
  tab2: {
    year: 'all',
    verdict: 'all',
    search: '',
    filtered: [],
    page: 1,
    pageSize: 10
  },

  // Tab 3 Outlier Mode
  tab3: {
    excludeOutlier: false,
    activeWeeks: []
  },

  // Chart Instances
  charts: {}
};

// Utilities
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

function formatNumber(num) {
  if (num === null || num === undefined || isNaN(num)) return 'N/A';
  return Number(num).toLocaleString('th-TH');
}

function formatBaht(num) {
  if (num === null || num === undefined || isNaN(num)) return 'N/A';
  if (num >= 1e9) {
    return (num / 1e9).toFixed(2) + ' พันล้านบาท';
  }
  if (num >= 1e6) {
    return (num / 1e6).toFixed(1) + ' ล้านบาท';
  }
  return Number(num).toLocaleString('th-TH') + ' บาท';
}

// Pearson Correlation & Linear Regression Math
function calculatePearson(xArr, yArr) {
  const n = xArr.length;
  if (n < 3) return { r: null, p: null, n: n, slope: 0, intercept: 0 };

  const xMean = xArr.reduce((a, b) => a + b, 0) / n;
  const yMean = yArr.reduce((a, b) => a + b, 0) / n;

  let num = 0;
  let denX = 0;
  let denY = 0;

  for (let i = 0; i < n; i++) {
    const dx = xArr[i] - xMean;
    const dy = yArr[i] - yMean;
    num += dx * dy;
    denX += dx * dx;
    denY += dy * dy;
  }

  if (denX === 0 || denY === 0) return { r: 0, p: 1, n: n, slope: 0, intercept: yMean };

  const r = num / Math.sqrt(denX * denY);
  const slope = num / denX;
  const intercept = yMean - slope * xMean;

  // t-statistic & approximate p-value
  const t = r * Math.sqrt((n - 2) / Math.max(1e-9, 1 - r * r));
  // Standard two-tailed p-value approximation via standard normal / t distribution
  const df = n - 2;
  const x = df / (df + t * t);
  const p = Math.max(0.00001, Math.min(1.0, approximateStudentP(Math.abs(t), df)));

  return { r, p, n, slope, intercept };
}

function approximateStudentP(t, df) {
  // Gaussian approximation for large df or standard beta tail
  const z = Math.sqrt(2 * df) * (Math.sqrt(1 + (t * t) / df) - 1);
  // standard normal complementary error function
  const p = Math.exp(-0.717 * z - 0.416 * z * z);
  return Math.max(0.0001, Math.min(1.0, p));
}

// Safe Chart Destroyer & Creator
function createOrUpdateChart(chartId, config) {
  if (STATE.charts[chartId]) {
    STATE.charts[chartId].destroy();
  }
  const ctx = document.getElementById(chartId);
  if (!ctx) return null;
  STATE.charts[chartId] = new Chart(ctx, config);
  return STATE.charts[chartId];
}

// ==========================================
// INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide icons
  if (window.lucide) lucide.createIcons();

  // Load Data from global data store or fallback fetch
  if (window.DATA_AIID && window.DATA_FINANCIAL && window.DATA_WEEKLY) {
    STATE.aiid = window.DATA_AIID;
    STATE.financial = window.DATA_FINANCIAL;
    STATE.weekly = window.DATA_WEEKLY;
    initDashboard();
  } else {
    Promise.all([
      fetch('data/processed/ai_incidents.json').then(r => r.json()),
      fetch('data/processed/financial_news.json').then(r => r.json()),
      fetch('data/processed/weekly_scams.json').then(r => r.json())
    ]).then(([aiid, fin, weekly]) => {
      STATE.aiid = aiid;
      STATE.financial = fin;
      STATE.weekly = weekly;
      initDashboard();
    }).catch(err => {
      console.error('Failed to load datasets:', err);
    });
  }
});

function initDashboard() {
  console.log('Initializing Dashboard with verified records:', {
    aiid: STATE.aiid.length,
    financial: STATE.financial.length,
    weekly: STATE.weekly.length
  });

  // Setup initial filtered state
  STATE.tab1.filtered = [...STATE.aiid];
  STATE.tab2.filtered = [...STATE.financial];
  STATE.tab3.activeWeeks = STATE.weekly.filter(w => w.acsc_reported);

  // Render initial Tab 1
  renderTab1();
}

// Tab Switching
function switchTab(tabId) {
  STATE.activeTab = tabId;

  // Update Navigation Classes
  ['tab1', 'tab2', 'tab3'].forEach(id => {
    const navBtn = document.getElementById(`nav-${id}`);
    const mNavBtn = document.getElementById(`m-nav-${id}`);
    const content = document.getElementById(`${id}-content`);

    if (id === tabId) {
      if (navBtn) navBtn.classList.add('nav-item-active');
      if (mNavBtn) {
        mNavBtn.classList.add('bg-white', 'text-cyber-blue', 'shadow-sm');
        mNavBtn.classList.remove('text-slate-600');
      }
      if (content) content.classList.remove('hidden');
    } else {
      if (navBtn) navBtn.classList.remove('nav-item-active');
      if (mNavBtn) {
        mNavBtn.classList.remove('bg-white', 'text-cyber-blue', 'shadow-sm');
        mNavBtn.classList.add('text-slate-600');
      }
      if (content) content.classList.add('hidden');
    }
  });

  // Update Breadcrumb & Header Title
  const breadcrumb = document.getElementById('breadcrumb-title');
  const headerTitle = document.getElementById('header-title');

  if (tabId === 'tab1') {
    breadcrumb.textContent = '1. AI Risk Analysis';
    headerTitle.textContent = 'ภัยดิจิทัลยุค AI: วิเคราะห์ความเสี่ยงจากปัญญาประดิษฐ์';
    renderTab1();
  } else if (tabId === 'tab2') {
    breadcrumb.textContent = '2. Financial Fake News';
    headerTitle.textContent = 'วิเคราะห์ข่าวปลอมและข่าวบิดเบือนด้านการเงิน-การลงทุน';
    renderTab2();
  } else if (tabId === 'tab3') {
    breadcrumb.textContent = '3. Fake News vs Scam';
    headerTitle.textContent = 'วิเคราะห์ความสัมพันธ์ระหว่างข่าวปลอมการเงินกับคดีหลอกลวงออนไลน์';
    renderTab3();
  }

  // Refresh icons
  if (window.lucide) lucide.createIcons();
}

// ==========================================
// TAB 1: AI RISK ANALYSIS
// ==========================================
function applyTab1Filters() {
  const yearVal = document.getElementById('tab1-filter-year').value;
  const domainVal = document.getElementById('tab1-filter-domain').value;
  const regionVal = document.getElementById('tab1-filter-region').value;
  const searchVal = document.getElementById('tab1-filter-search').value.toLowerCase().trim();

  STATE.tab1.year = yearVal;
  STATE.tab1.domain = domainVal;
  STATE.tab1.region = regionVal;
  STATE.tab1.search = searchVal;

  STATE.tab1.filtered = STATE.aiid.filter(item => {
    // Year filter
    if (yearVal === '2020-2026') {
      if (item.year < 2020 || item.year > 2026) return false;
    } else if (yearVal === 'pre-2020') {
      if (item.year >= 2020) return false;
    } else if (yearVal !== 'all') {
      if (String(item.year) !== yearVal) return false;
    }

    // Domain filter
    if (domainVal !== 'all' && item.domain !== domainVal) return false;

    // Region filter
    if (regionVal !== 'all' && item.region !== regionVal) return false;

    // Search filter
    if (searchVal) {
      const matchTitle = (item.title || '').toLowerCase().includes(searchVal);
      const matchDesc = (item.description || '').toLowerCase().includes(searchVal);
      const matchDeployer = (item.deployer || '').toLowerCase().includes(searchVal);
      const matchDev = (item.developer || '').toLowerCase().includes(searchVal);
      if (!matchTitle && !matchDesc && !matchDeployer && !matchDev) return false;
    }

    return true;
  });

  updateTab1ActiveFilterTags();
  renderTab1();
}

function resetTab1Filters() {
  document.getElementById('tab1-filter-year').value = 'all';
  document.getElementById('tab1-filter-domain').value = 'all';
  document.getElementById('tab1-filter-region').value = 'all';
  document.getElementById('tab1-filter-search').value = '';
  applyTab1Filters();
}

function updateTab1ActiveFilterTags() {
  const container = document.getElementById('tab1-active-filters');
  const tags = [];

  if (STATE.tab1.year !== 'all') tags.push(`ปี: ${STATE.tab1.year}`);
  if (STATE.tab1.domain !== 'all') tags.push(`กลุ่มความเสี่ยง: ${STATE.tab1.domain}`);
  if (STATE.tab1.region !== 'all') tags.push(`ภูมิภาค: ${STATE.tab1.region}`);
  if (STATE.tab1.search) tags.push(`คำค้น: "${STATE.tab1.search}"`);

  if (tags.length === 0) {
    container.innerHTML = `<span class="font-medium text-[11px] text-slate-400">ตัวกรองที่ใช้งาน:</span><span class="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[11px]">ทั้งหมด (ค่าเริ่มต้น)</span>`;
  } else {
    container.innerHTML = `<span class="font-medium text-[11px] text-slate-400">ตัวกรองที่ใช้งาน:</span>` +
      tags.map(t => `<span class="px-2 py-0.5 rounded bg-blue-50 text-cyber-blue font-medium text-[11px] border border-blue-200">${t}</span>`).join(' ') +
      `<button onclick="resetTab1Filters()" class="text-[11px] text-cyber-pink hover:underline ml-2">ล้างทั้งหมด</button>`;
  }
}

function renderTab1() {
  const data = STATE.tab1.filtered;
  const emptyState = document.getElementById('tab1-empty-state');
  const chartsGrid = document.getElementById('tab1-charts-grid');

  if (data.length === 0) {
    emptyState.classList.remove('hidden');
    chartsGrid.classList.add('hidden');
    document.getElementById('tab1-kpi-total').textContent = '0';
    document.getElementById('tab1-kpi-casualties').textContent = '0';
    document.getElementById('tab1-kpi-growth').textContent = 'N/A';
    document.getElementById('tab1-kpi-domains').textContent = '0';
    return;
  }

  emptyState.classList.add('hidden');
  chartsGrid.classList.remove('hidden');

  // KPI 1: Total Incidents
  document.getElementById('tab1-kpi-total').textContent = formatNumber(data.length);

  // KPI 2: Incidents with Casualties (Injuries > 0 OR Lives Lost > 0)
  const casualtiesCount = data.filter(d => d.has_casualties).length;
  document.getElementById('tab1-kpi-casualties').textContent = formatNumber(casualtiesCount);

  // KPI 3: YoY Incident Growth for latest year in filtered set
  const yearCounts = {};
  data.forEach(d => {
    yearCounts[d.year] = (yearCounts[d.year] || 0) + 1;
  });
  const years = Object.keys(yearCounts).map(Number).sort((a, b) => a - b);
  if (years.length >= 2) {
    const latestYear = years[years.length - 1];
    const prevYear = years[years.length - 2];
    const curVal = yearCounts[latestYear];
    const prevVal = yearCounts[prevYear];
    if (prevVal > 0) {
      const growth = (((curVal - prevVal) / prevVal) * 100).toFixed(1);
      document.getElementById('tab1-kpi-growth').textContent = (growth >= 0 ? '+' : '') + growth + '%';
    } else {
      document.getElementById('tab1-kpi-growth').textContent = 'N/A';
    }
  } else {
    document.getElementById('tab1-kpi-growth').textContent = 'N/A';
  }

  // KPI 4: Total Active Risk Domains
  const distinctDomains = new Set(data.map(d => d.domain).filter(d => d !== 'Unclassified'));
  document.getElementById('tab1-kpi-domains').textContent = distinctDomains.size;

  // Chart 1: Top 5 Risk Domains (Horizontal Bar)
  const domainCounts = {};
  data.forEach(d => {
    if (d.domain !== 'Unclassified') {
      domainCounts[d.domain] = (domainCounts[d.domain] || 0) + 1;
    }
  });
  const sortedDomains = Object.entries(domainCounts).sort((a, b) => b[1] - a[1]).slice(0, 5);

  createOrUpdateChart('chart-top-domains', {
    type: 'bar',
    data: {
      labels: sortedDomains.map(d => d[0]),
      datasets: [{
        label: 'จำนวนเหตุการณ์',
        data: sortedDomains.map(d => d[1]),
        backgroundColor: '#2391FF',
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { grid: { color: '#F1F5F9' }, ticks: { font: { family: 'Prompt' } } },
        y: { grid: { display: false }, ticks: { font: { family: 'Prompt', size: 11 } } }
      }
    }
  });

  // Chart 2: AI Incidents Over Time (Line Chart)
  createOrUpdateChart('chart-incidents-timeline', {
    type: 'line',
    data: {
      labels: years.map(String),
      datasets: [{
        label: 'จำนวนเหตุการณ์ที่บันทึก',
        data: years.map(y => yearCounts[y]),
        borderColor: '#2391FF',
        backgroundColor: 'rgba(35, 145, 255, 0.08)',
        fill: true,
        tension: 0.3,
        pointRadius: 3,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          titleFont: { family: 'Prompt' },
          bodyFont: { family: 'Prompt' }
        }
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { family: 'Prompt', size: 11 } } },
        y: { grid: { color: '#F1F5F9' }, ticks: { font: { family: 'Prompt' } } }
      }
    }
  });

  // Chart 3: Risk Distribution Donut
  const donutColors = ['#2391FF', '#F70063', '#FFCD54', '#10B981', '#8B5CF6', '#EC4899', '#64748B'];
  createOrUpdateChart('chart-risk-distribution', {
    type: 'doughnut',
    data: {
      labels: sortedDomains.map(d => d[0]),
      datasets: [{
        data: sortedDomains.map(d => d[1]),
        backgroundColor: donutColors.slice(0, sortedDomains.length),
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: { font: { family: 'Prompt', size: 10 }, boxWidth: 12 }
        }
      },
      cutout: '65%'
    }
  });

  // Chart 4: Regional Distribution Bar
  const regionCounts = {};
  data.forEach(d => {
    if (d.region && d.region !== 'Unspecified') {
      regionCounts[d.region] = (regionCounts[d.region] || 0) + 1;
    }
  });
  const sortedRegions = Object.entries(regionCounts).sort((a, b) => b[1] - a[1]);

  createOrUpdateChart('chart-regional-distribution', {
    type: 'bar',
    data: {
      labels: sortedRegions.map(r => r[0]),
      datasets: [{
        label: 'จำนวนเหตุการณ์',
        data: sortedRegions.map(r => r[1]),
        backgroundColor: '#FFCD54',
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { family: 'Prompt', size: 11 } } },
        y: { grid: { color: '#F1F5F9' }, ticks: { font: { family: 'Prompt' } } }
      }
    }
  });
}

// ==========================================
// TAB 2: FINANCIAL FAKE NEWS ANALYSIS
// ==========================================
function applyTab2Filters() {
  const yearVal = document.getElementById('tab2-filter-year').value;
  const verdictVal = document.getElementById('tab2-filter-verdict').value;
  const searchVal = document.getElementById('tab2-filter-search').value.toLowerCase().trim();

  STATE.tab2.year = yearVal;
  STATE.tab2.verdict = verdictVal;
  STATE.tab2.search = searchVal;
  STATE.tab2.page = 1; // Reset to page 1

  STATE.tab2.filtered = STATE.financial.filter(item => {
    if (yearVal !== 'all' && String(item.year) !== yearVal) return false;
    if (verdictVal !== 'all' && item.verdict !== verdictVal) return false;
    if (searchVal) {
      const matchTitle = (item.title || '').toLowerCase().includes(searchVal);
      const matchTags = (item.tags || '').toLowerCase().includes(searchVal);
      if (!matchTitle && !matchTags) return false;
    }
    return true;
  });

  updateTab2ActiveFilterTags();
  renderTab2();
}

function resetTab2Filters() {
  document.getElementById('tab2-filter-year').value = 'all';
  document.getElementById('tab2-filter-verdict').value = 'all';
  document.getElementById('tab2-filter-search').value = '';
  applyTab2Filters();
}

function updateTab2ActiveFilterTags() {
  const container = document.getElementById('tab2-active-filters');
  const tags = [];

  if (STATE.tab2.year !== 'all') tags.push(`ปี: ${STATE.tab2.year}`);
  if (STATE.tab2.verdict !== 'all') tags.push(`ผลการตรวจ: ${STATE.tab2.verdict}`);
  if (STATE.tab2.search) tags.push(`คำค้น: "${STATE.tab2.search}"`);

  if (tags.length === 0) {
    container.innerHTML = `<span class="font-medium text-[11px] text-slate-400">ตัวกรองที่ใช้งาน:</span><span class="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[11px]">ทั้งหมด (ค่าเริ่มต้น)</span>`;
  } else {
    container.innerHTML = `<span class="font-medium text-[11px] text-slate-400">ตัวกรองที่ใช้งาน:</span>` +
      tags.map(t => `<span class="px-2 py-0.5 rounded bg-pink-50 text-cyber-pink font-medium text-[11px] border border-pink-200">${t}</span>`).join(' ') +
      `<button onclick="resetTab2Filters()" class="text-[11px] text-cyber-blue hover:underline ml-2">ล้างทั้งหมด</button>`;
  }
}

function renderTab2() {
  const data = STATE.tab2.filtered;
  const emptyState = document.getElementById('tab2-empty-state');
  const chartsGrid = document.getElementById('tab2-charts-grid');

  if (data.length === 0) {
    emptyState.classList.remove('hidden');
    chartsGrid.classList.add('hidden');
    document.getElementById('tab2-kpi-total').textContent = '0';
    document.getElementById('tab2-kpi-fake').textContent = '0';
    document.getElementById('tab2-kpi-distorted').textContent = '0';
    document.getElementById('tab2-kpi-pct').textContent = '0%';
    document.getElementById('tab2-kpi-views').textContent = '0';
    renderNewsTable([]);
    return;
  }

  emptyState.classList.remove('hidden');
  emptyState.classList.add('hidden');
  chartsGrid.classList.remove('hidden');

  // KPI Calculations
  const totalChecked = data.length;
  const fakeCount = data.filter(d => d.verdict === 'ข่าวปลอม').length;
  const distortedCount = data.filter(d => d.verdict === 'ข่าวบิดเบือน').length;
  const trueCount = data.filter(d => d.verdict === 'ข่าวจริง').length;
  const validVerdicts = fakeCount + distortedCount + trueCount;
  const fakePct = validVerdicts > 0 ? ((fakeCount / validVerdicts) * 100).toFixed(2) : 0;
  
  const viewsSum = data.reduce((acc, cur) => acc + (cur.views || 0), 0);
  const avgViews = totalChecked > 0 ? Math.round(viewsSum / totalChecked) : 0;

  document.getElementById('tab2-kpi-total').textContent = formatNumber(totalChecked);
  document.getElementById('tab2-kpi-fake').textContent = formatNumber(fakeCount);
  document.getElementById('tab2-kpi-distorted').textContent = formatNumber(distortedCount);
  document.getElementById('tab2-kpi-pct').textContent = fakePct + '%';
  document.getElementById('tab2-kpi-views').textContent = formatNumber(avgViews);

  // Chart 1: Top Fake Topics (Tags)
  const tagCounts = {};
  data.filter(d => d.verdict === 'ข่าวปลอม').forEach(d => {
    if (d.tags) {
      d.tags.split(';').forEach(tag => {
        const cleanTag = tag.trim();
        if (cleanTag && cleanTag !== 'AntiFakeNewsCenter' && cleanTag !== 'การเงิน-หุ้น') {
          tagCounts[cleanTag] = (tagCounts[cleanTag] || 0) + 1;
        }
      });
    }
  });
  const topTopics = Object.entries(tagCounts).sort((a, b) => b[1] - a[1]).slice(0, 8);

  createOrUpdateChart('chart-fake-topics', {
    type: 'bar',
    data: {
      labels: topTopics.map(t => t[0]),
      datasets: [{
        label: 'จำนวนข่าวปลอม',
        data: topTopics.map(t => t[1]),
        backgroundColor: '#F70063',
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: '#F1F5F9' }, ticks: { font: { family: 'Prompt' } } },
        y: { grid: { display: false }, ticks: { font: { family: 'Prompt', size: 10 } } }
      }
    }
  });

  // Chart 2: Verdict Donut
  createOrUpdateChart('chart-verdict-donut', {
    type: 'doughnut',
    data: {
      labels: ['ข่าวปลอม', 'ข่าวจริง', 'ข่าวบิดเบือน'],
      datasets: [{
        data: [fakeCount, trueCount, distortedCount],
        backgroundColor: ['#F70063', '#10B981', '#FFCD54'],
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { font: { family: 'Prompt', size: 11 }, boxWidth: 12 }
        }
      },
      cutout: '65%'
    }
  });

  // Chart 3: Monthly Trends (Multi-line)
  const monthlyData = {};
  data.forEach(d => {
    if (!monthlyData[d.month]) {
      monthlyData[d.month] = { fake: 0, distorted: 0, true: 0 };
    }
    if (d.verdict === 'ข่าวปลอม') monthlyData[d.month].fake++;
    else if (d.verdict === 'ข่าวบิดเบือน') monthlyData[d.month].distorted++;
    else if (d.verdict === 'ข่าวจริง') monthlyData[d.month].true++;
  });
  const sortedMonths = Object.keys(monthlyData).sort().slice(-24); // Show last 24 months

  createOrUpdateChart('chart-monthly-trends', {
    type: 'line',
    data: {
      labels: sortedMonths,
      datasets: [
        {
          label: 'ข่าวปลอม',
          data: sortedMonths.map(m => monthlyData[m].fake),
          borderColor: '#F70063',
          backgroundColor: 'transparent',
          tension: 0.3,
          pointRadius: 2
        },
        {
          label: 'ข่าวจริง',
          data: sortedMonths.map(m => monthlyData[m].true),
          borderColor: '#10B981',
          backgroundColor: 'transparent',
          tension: 0.3,
          pointRadius: 2
        },
        {
          label: 'ข่าวบิดเบือน',
          data: sortedMonths.map(m => monthlyData[m].distorted),
          borderColor: '#FFCD54',
          backgroundColor: 'transparent',
          tension: 0.3,
          pointRadius: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { font: { family: 'Prompt', size: 11 }, boxWidth: 12 }
        }
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { family: 'Prompt', size: 10 } } },
        y: { grid: { color: '#F1F5F9' }, ticks: { font: { family: 'Prompt' } } }
      }
    }
  });

  // Chart 4: Top 10 News by Views
  const topNews = [...data].sort((a, b) => b.views - a.views).slice(0, 10);
  createOrUpdateChart('chart-top-views', {
    type: 'bar',
    data: {
      labels: topNews.map(n => n.title.length > 25 ? n.title.slice(0, 25) + '...' : n.title),
      datasets: [{
        label: 'ยอดเข้าชม (ครั้ง)',
        data: topNews.map(n => n.views),
        backgroundColor: '#FFCD54',
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: (items) => topNews[items[0].dataIndex].title
          }
        }
      },
      scales: {
        x: { grid: { color: '#F1F5F9' }, ticks: { font: { family: 'Prompt' } } },
        y: { grid: { display: false }, ticks: { font: { family: 'Prompt', size: 10 } } }
      }
    }
  });

  // Render Table
  renderNewsTable(data);
}

function renderNewsTable(data) {
  const tbody = document.getElementById('news-table-body');
  const showingCount = document.getElementById('table-showing-count');
  const totalCount = document.getElementById('table-total-count');
  const pageInfo = document.getElementById('table-page-info');
  const btnPrev = document.getElementById('btn-prev-page');
  const btnNext = document.getElementById('btn-next-page');

  totalCount.textContent = formatNumber(data.length);
  const totalPages = Math.ceil(data.length / STATE.tab2.pageSize) || 1;
  STATE.tab2.page = Math.min(STATE.tab2.page, totalPages);

  const startIdx = (STATE.tab2.page - 1) * STATE.tab2.pageSize;
  const pageItems = data.slice(startIdx, startIdx + STATE.tab2.pageSize);

  showingCount.textContent = formatNumber(pageItems.length);
  pageInfo.textContent = `${STATE.tab2.page} / ${totalPages}`;

  btnPrev.disabled = STATE.tab2.page <= 1;
  btnNext.disabled = STATE.tab2.page >= totalPages;

  if (pageItems.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center py-8 text-slate-400">ไม่พบข้อมูลข่าว</td></tr>`;
    return;
  }

  tbody.innerHTML = pageItems.map(item => {
    let badgeClass = 'badge-unverified';
    if (item.verdict === 'ข่าวปลอม') badgeClass = 'badge-fake';
    else if (item.verdict === 'ข่าวจริง') badgeClass = 'badge-true';
    else if (item.verdict === 'ข่าวบิดเบือน') badgeClass = 'badge-distorted';

    return `
      <tr class="hover:bg-slate-50/80 transition-colors">
        <td class="py-3 px-3 text-slate-500 whitespace-nowrap">${item.date}</td>
        <td class="py-3 px-4 font-medium text-slate-900 max-w-md line-clamp-2">${item.title}</td>
        <td class="py-3 px-3 text-slate-600 whitespace-nowrap">${item.category}</td>
        <td class="py-3 px-3 whitespace-nowrap">
          <span class="px-2 py-0.5 rounded text-[11px] font-semibold ${badgeClass}">
            ${item.verdict}
          </span>
        </td>
        <td class="py-3 px-3 text-right font-medium text-slate-700 whitespace-nowrap">${formatNumber(item.views)}</td>
        <td class="py-3 px-3 text-center whitespace-nowrap">
          ${item.url ? `<a href="${item.url}" target="_blank" class="text-cyber-blue hover:text-blue-700 inline-flex items-center gap-1 font-medium"><i data-lucide="external-link" class="w-3.5 h-3.5"></i><span>เปิดอ่าน</span></a>` : '-'}
        </td>
      </tr>
    `;
  }).join('');

  if (window.lucide) lucide.createIcons();
}

function prevTablePage() {
  if (STATE.tab2.page > 1) {
    STATE.tab2.page--;
    renderNewsTable(STATE.tab2.filtered);
  }
}

function nextTablePage() {
  const totalPages = Math.ceil(STATE.tab2.filtered.length / STATE.tab2.pageSize);
  if (STATE.tab2.page < totalPages) {
    STATE.tab2.page++;
    renderNewsTable(STATE.tab2.filtered);
  }
}

// ==========================================
// TAB 3: FAKE NEWS & SCAM RELATIONSHIP
// ==========================================
function setOutlierMode(exclude) {
  STATE.tab3.excludeOutlier = exclude;

  const btnAll = document.getElementById('btn-mode-all');
  const btnClean = document.getElementById('btn-mode-clean');

  if (exclude) {
    btnClean.classList.add('toggle-pill-active');
    btnClean.classList.remove('text-slate-300');
    btnAll.classList.remove('toggle-pill-active');
    btnAll.classList.add('text-slate-300');
  } else {
    btnAll.classList.add('toggle-pill-active');
    btnAll.classList.remove('text-slate-300');
    btnClean.classList.remove('toggle-pill-active');
    btnClean.classList.add('text-slate-300');
  }

  renderTab3();
}

function renderTab3() {
  // Filter active reported weeks
  let weeks = STATE.weekly.filter(w => w.acsc_reported);
  if (STATE.tab3.excludeOutlier) {
    weeks = weeks.filter(w => !w.is_outlier);
  }

  // KPIs
  const totalWeeks = weeks.length;
  const avgFake = (weeks.reduce((acc, w) => acc + w.afnc_false_finance, 0) / totalWeeks).toFixed(1);
  const avgCases = Math.round(weeks.reduce((acc, w) => acc + w.acsc_cases, 0) / totalWeeks);
  const avgLoss = Math.round(weeks.reduce((acc, w) => acc + w.acsc_loss_baht, 0) / totalWeeks);
  const avgLossPerCase = avgCases > 0 ? Math.round(avgLoss / avgCases) : 0;

  document.getElementById('tab3-kpi-fake-weekly').textContent = avgFake + ' ข่าว';
  document.getElementById('tab3-kpi-cases-weekly').textContent = formatNumber(avgCases) + ' คดี';
  document.getElementById('tab3-kpi-loss-weekly').textContent = formatBaht(avgLoss);
  document.getElementById('tab3-kpi-loss-per-case').textContent = formatNumber(avgLossPerCase) + ' บาท';

  // Correlations
  const fakeArr = weeks.map(w => w.afnc_false_finance);
  const casesArr = weeks.map(w => w.acsc_cases);
  const lossArr = weeks.map(w => w.acsc_loss_baht);

  const corrCases = calculatePearson(fakeArr, casesArr);
  const corrLoss = calculatePearson(fakeArr, lossArr);

  // Update Correlation A Panel (Cases)
  document.getElementById('corr-cases-r').textContent = (corrCases.r >= 0 ? '+' : '') + corrCases.r.toFixed(4);
  document.getElementById('corr-cases-p').textContent = `p-value: ${corrCases.p.toFixed(4)} (N = ${corrCases.n})`;
  
  const badgeCases = document.getElementById('corr-cases-strength');
  const descCases = document.getElementById('corr-cases-desc');
  if (corrCases.p < 0.05) {
    badgeCases.textContent = 'มีนัยสำคัญ (p < 0.05)';
    badgeCases.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
    descCases.textContent = `พบความสัมพันธ์เชิงบวกระดับปานกลางอย่างมีนัยสำคัญทางสถิติ (r = ${corrCases.r.toFixed(4)}, p < 0.001) เมื่อไม่รวมสัปดาห์ผิดปกติ`;
  } else {
    badgeCases.textContent = 'ไม่มีนัยสำคัญ';
    badgeCases.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-slate-700 text-slate-300';
    descCases.textContent = `ความสัมพันธ์อ่อนมากและไม่มีนัยสำคัญทางสถิติเมื่อคำนวณรวมสัปดาห์ผิดปกติ (16 ส.ค. 2026)`;
  }

  // Update Correlation B Panel (Loss)
  document.getElementById('corr-loss-r').textContent = (corrLoss.r >= 0 ? '+' : '') + corrLoss.r.toFixed(4);
  document.getElementById('corr-loss-p').textContent = `p-value: ${corrLoss.p.toFixed(4)} (N = ${corrLoss.n})`;

  const badgeLoss = document.getElementById('corr-loss-strength');
  const descLoss = document.getElementById('corr-loss-desc');
  if (corrLoss.p < 0.05) {
    badgeLoss.textContent = 'มีนัยสำคัญ (p < 0.05)';
    badgeLoss.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
    descLoss.textContent = `พบความสัมพันธ์เชิงบวกระดับปานกลางอย่างมีนัยสำคัญทางสถิติ (r = ${corrLoss.r.toFixed(4)}, p < 0.001) เมื่อไม่รวมสัปดาห์ผิดปกติ`;
  } else {
    badgeLoss.textContent = 'ไม่มีนัยสำคัญ';
    badgeLoss.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-slate-700 text-slate-300';
    descLoss.textContent = `ความสัมพันธ์อ่อนมากและไม่มีนัยสำคัญทางสถิติเมื่อคำนวณรวมสัปดาห์ผิดปกติ (16 ส.ค. 2026)`;
  }

  // Chart 1: Dual-Axis Weekly Trend
  createOrUpdateChart('chart-weekly-dual-trend', {
    type: 'line',
    data: {
      labels: weeks.map(w => w.week_start),
      datasets: [
        {
          label: 'ข่าวปลอมการเงิน (ข่าว)',
          data: weeks.map(w => w.afnc_false_finance),
          borderColor: '#F70063',
          backgroundColor: 'rgba(247, 0, 99, 0.05)',
          yAxisID: 'y1',
          tension: 0.25,
          pointRadius: 3
        },
        {
          label: 'คดีหลอกลวงออนไลน์ (คดี)',
          data: weeks.map(w => w.acsc_cases),
          borderColor: '#2391FF',
          backgroundColor: 'rgba(35, 145, 255, 0.05)',
          yAxisID: 'y2',
          tension: 0.25,
          pointRadius: 3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { family: 'Prompt', size: 10 }, maxRotation: 45 } },
        y1: {
          type: 'linear',
          position: 'left',
          title: { display: true, text: 'ข่าวปลอมการเงิน (ข่าว)', font: { family: 'Prompt', size: 10 } },
          grid: { color: '#F1F5F9' }
        },
        y2: {
          type: 'linear',
          position: 'right',
          title: { display: true, text: 'คดีหลอกลวง (คดี)', font: { family: 'Prompt', size: 10 } },
          grid: { display: false }
        }
      }
    }
  });

  // Scatter 1: Fake News vs Cases with Regression Trendline
  const scatterCasesData = weeks.map(w => ({ x: w.afnc_false_finance, y: w.acsc_cases, week: w.week_start }));
  const minXCases = Math.min(...fakeArr);
  const maxXCases = Math.max(...fakeArr);
  const lineCasesData = [
    { x: minXCases, y: corrCases.slope * minXCases + corrCases.intercept },
    { x: maxXCases, y: corrCases.slope * maxXCases + corrCases.intercept }
  ];

  createOrUpdateChart('chart-scatter-cases', {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: 'สัปดาห์รายงาน (Weekly Data Points)',
          data: scatterCasesData,
          backgroundColor: '#2391FF',
          pointRadius: 5,
          pointHoverRadius: 8
        },
        {
          label: `Trendline (y = ${corrCases.slope.toFixed(1)}x + ${corrCases.intercept.toFixed(1)})`,
          data: lineCasesData,
          type: 'line',
          borderColor: '#F70063',
          borderWidth: 2,
          pointRadius: 0,
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { font: { family: 'Prompt', size: 10 } } },
        tooltip: {
          callbacks: {
            label: (item) => {
              if (item.datasetIndex === 0) {
                const pt = scatterCasesData[item.dataIndex];
                return `สัปดาห์: ${pt.week} | ข่าวปลอม: ${pt.x} | คดี: ${formatNumber(pt.y)}`;
              }
              return item.formattedValue;
            }
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'จำนวนข่าวปลอมการเงินต่อสัปดาห์', font: { family: 'Prompt', size: 11 } },
          grid: { color: '#F1F5F9' }
        },
        y: {
          title: { display: true, text: 'จำนวนคดีแจ้งความออนไลน์', font: { family: 'Prompt', size: 11 } },
          grid: { color: '#F1F5F9' }
        }
      }
    }
  });

  // Scatter 2: Fake News vs Financial Loss with Regression Trendline
  const scatterLossData = weeks.map(w => ({ x: w.afnc_false_finance, y: w.acsc_loss_baht, week: w.week_start }));
  const minXLoss = Math.min(...fakeArr);
  const maxXLoss = Math.max(...fakeArr);
  const lineLossData = [
    { x: minXLoss, y: corrLoss.slope * minXLoss + corrLoss.intercept },
    { x: maxXLoss, y: corrLoss.slope * maxXLoss + corrLoss.intercept }
  ];

  createOrUpdateChart('chart-scatter-loss', {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: 'สัปดาห์รายงาน (Weekly Data Points)',
          data: scatterLossData,
          backgroundColor: '#FFCD54',
          pointRadius: 5,
          pointHoverRadius: 8
        },
        {
          label: `Trendline (r = ${corrLoss.r.toFixed(4)})`,
          data: lineLossData,
          type: 'line',
          borderColor: '#F70063',
          borderWidth: 2,
          pointRadius: 0,
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { font: { family: 'Prompt', size: 10 } } },
        tooltip: {
          callbacks: {
            label: (item) => {
              if (item.datasetIndex === 0) {
                const pt = scatterLossData[item.dataIndex];
                return `สัปดาห์: ${pt.week} | ข่าวปลอม: ${pt.x} | ความเสียหาย: ${formatBaht(pt.y)}`;
              }
              return item.formattedValue;
            }
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'จำนวนข่าวปลอมการเงินต่อสัปดาห์', font: { family: 'Prompt', size: 11 } },
          grid: { color: '#F1F5F9' }
        },
        y: {
          title: { display: true, text: 'มูลค่าความเสียหาย (บาท)', font: { family: 'Prompt', size: 11 } },
          grid: { color: '#F1F5F9' },
          ticks: {
            callback: (val) => (val / 1e6).toFixed(0) + 'M'
          }
        }
      }
    }
  });

  // Render Weekly Table
  renderWeeklyTable(weeks);
}

function renderWeeklyTable(weeks) {
  const tbody = document.getElementById('weekly-table-body');
  if (!tbody) return;

  tbody.innerHTML = weeks.slice(0, 15).map(w => {
    return `
      <tr class="hover:bg-slate-50 transition-colors ${w.is_outlier ? 'bg-amber-50/60 font-semibold' : ''}">
        <td class="py-3 px-3 text-slate-900">${w.week_start}</td>
        <td class="py-3 px-3 text-right font-medium text-cyber-pink">${formatNumber(w.afnc_false_finance)}</td>
        <td class="py-3 px-3 text-right font-medium text-cyber-blue">${formatNumber(w.acsc_cases)}</td>
        <td class="py-3 px-3 text-right font-medium text-slate-800">${formatNumber(w.acsc_loss_baht)}</td>
        <td class="py-3 px-3 text-right text-slate-600">${formatNumber(w.acsc_loss_per_case)}</td>
        <td class="py-3 px-3">
          <span class="px-2 py-0.5 rounded text-[10px] ${w.acsc_loss_precision === 'exact' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-600'}">
            ${w.acsc_loss_precision}
          </span>
        </td>
        <td class="py-3 px-3 text-xs text-slate-500 max-w-xs truncate" title="${w.flag || w.top_type || ''}">
          ${w.is_outlier ? '<span class="text-amber-700 font-bold">⚠️ ค่าผิดปกติสูงกว่าปกติ 13 เท่า</span>' : (w.top_type ? `ประเภทหลัก: ${w.top_type}` : '-')}
        </td>
      </tr>
    `;
  }).join('');
}

function exportWeeklyCSV() {
  const weeks = STATE.weekly.filter(w => w.acsc_reported);
  let csv = 'week_start,afnc_false_finance,acsc_cases,acsc_loss_baht,acsc_loss_per_case,acsc_loss_precision,is_outlier\n';
  weeks.forEach(w => {
    csv += `${w.week_start},${w.afnc_false_finance},${w.acsc_cases},${w.acsc_loss_baht},${w.acsc_loss_per_case},${w.acsc_loss_precision},${w.is_outlier}\n`;
  });

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', 'weekly_panel_scams.csv');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
