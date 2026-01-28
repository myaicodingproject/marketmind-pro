// Chart.js service for standard financial charts
const puppeteer = require('puppeteer');

class ChartJSService {
    constructor() {
        this.browser = null;
    }

    async init() {
        this.browser = await puppeteer.launch({ 
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
    }

    async generateRevenueTrend(data) {
        const chartConfig = {
            type: 'line',
            data: {
                labels: ['2022', '2023', '2024', '2025E', '2026E'],
                datasets: [{
                    label: 'Revenue ($B)',
                    data: [282.8, 307.4, 339.7, 375.2, 415.8],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 3,
                    fill: true
                }, {
                    label: 'Net Income ($B)',
                    data: [59.9, 73.8, 88.3, 98.1, 109.2],
                    borderColor: '#059669',
                    backgroundColor: 'rgba(5, 150, 105, 0.1)',
                    borderWidth: 3,
                    fill: true
                }]
            },
            options: {
                responsive: false,
                plugins: {
                    title: {
                        display: true,
                        text: `${data.ticker || 'GOOGL'} - Revenue & Profitability Trend`,
                        font: { size: 18, weight: 'bold' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Amount ($ Billions)' }
                    }
                }
            }
        };

        return await this.renderChart(chartConfig);
    }

    async generatePeerComparison(data) {
        const chartConfig = {
            type: 'radar',
            data: {
                labels: ['P/E Ratio', 'EV/EBITDA', 'ROE (%)', 'Revenue Growth (%)', 'Margin (%)'],
                datasets: [{
                    label: data.ticker || 'GOOGL',
                    data: [24.1, 18.2, 29.2, 10.5, 26.0],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.2)',
                    pointBackgroundColor: '#2563eb'
                }, {
                    label: 'Peer Average',
                    data: [28.4, 22.1, 22.8, 12.3, 21.5],
                    borderColor: '#dc2626',
                    backgroundColor: 'rgba(220, 38, 38, 0.2)',
                    pointBackgroundColor: '#dc2626'
                }]
            },
            options: {
                responsive: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Peer Group Valuation Comparison',
                        font: { size: 18, weight: 'bold' }
                    }
                },
                scales: {
                    r: { beginAtZero: true, max: 35 }
                }
            }
        };

        return await this.renderChart(chartConfig);
    }

    async renderChart(chartConfig) {
        const page = await this.browser.newPage();
        
        const html = `
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { margin: 0; padding: 20px; background: white; font-family: Arial, sans-serif; }
                #chartContainer { width: 800px; height: 500px; }
            </style>
        </head>
        <body>
            <div id="chartContainer">
                <canvas id="chart"></canvas>
            </div>
            <script>
                const ctx = document.getElementById('chart').getContext('2d');
                new Chart(ctx, ${JSON.stringify(chartConfig)});
            </script>
        </body>
        </html>
        `;

        await page.setContent(html);
        await page.waitForTimeout(2000);
        
        const canvas = await page.$('#chart');
        const imageBuffer = await canvas.screenshot({ type: 'png' });
        
        await page.close();
        return imageBuffer.toString('base64');
    }

    async close() {
        if (this.browser) {
            await this.browser.close();
        }
    }
}

module.exports = ChartJSService;