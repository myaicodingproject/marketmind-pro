// Chart.js + Puppeteer Implementation for Financial Charts
const puppeteer = require('puppeteer');

class FinancialChartGenerator {
  constructor() {
    this.browser = null;
  }

  async init() {
    this.browser = await puppeteer.launch({ 
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  }

  async generateDCFChart(cashFlows, discountRate) {
    const page = await this.browser.newPage();
    
    const chartConfig = {
      type: 'bar',
      data: {
        labels: Object.keys(cashFlows),
        datasets: [{
          label: 'Present Value',
          data: Object.values(cashFlows).map((cf, i) => 
            cf / Math.pow(1 + discountRate, i)
          ),
          backgroundColor: '#2563eb',
          borderColor: '#1d4ed8',
          borderWidth: 1
        }]
      },
      options: {
        responsive: false,
        plugins: {
          title: { display: true, text: 'DCF Valuation Model', font: { size: 18 } },
          legend: { display: false }
        },
        scales: {
          y: { 
            beginAtZero: true,
            ticks: { callback: value => `$${(value/1000000).toFixed(1)}M` }
          }
        }
      }
    };

    const html = `
      <html>
        <head>
          <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body style="margin: 0; padding: 20px; background: white;">
          <canvas id="chart" width="800" height="500"></canvas>
          <script>
            const ctx = document.getElementById('chart').getContext('2d');
            new Chart(ctx, ${JSON.stringify(chartConfig)});
          </script>
        </body>
      </html>
    `;

    await page.setContent(html);
    await page.waitForTimeout(1000);
    
    const canvas = await page.$('#chart');
    const image = await canvas.screenshot({ type: 'png' });
    
    await page.close();
    return image;
  }

  async generatePeerComparison(peerData) {
    const page = await this.browser.newPage();
    
    const chartConfig = {
      type: 'radar',
      data: {
        labels: ['P/E Ratio', 'EV/EBITDA', 'P/B Ratio', 'ROE', 'Debt/Equity'],
        datasets: peerData.map((company, i) => ({
          label: company.name,
          data: [company.pe, company.ev_ebitda, company.pb, company.roe, company.debt_equity],
          borderColor: `hsl(${i * 60}, 70%, 50%)`,
          backgroundColor: `hsla(${i * 60}, 70%, 50%, 0.1)`,
          pointBackgroundColor: `hsl(${i * 60}, 70%, 50%)`
        }))
      },
      options: {
        responsive: false,
        plugins: {
          title: { display: true, text: 'Peer Valuation Comparison' }
        },
        scales: {
          r: { beginAtZero: true, max: 30 }
        }
      }
    };

    const html = `
      <html>
        <head>
          <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body style="margin: 0; padding: 20px; background: white;">
          <canvas id="chart" width="800" height="600"></canvas>
          <script>
            const ctx = document.getElementById('chart').getContext('2d');
            new Chart(ctx, ${JSON.stringify(chartConfig)});
          </script>
        </body>
      </html>
    `;

    await page.setContent(html);
    await page.waitForTimeout(1000);
    
    const canvas = await page.$('#chart');
    const image = await canvas.screenshot({ type: 'png' });
    
    await page.close();
    return image;
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }
}

module.exports = FinancialChartGenerator;