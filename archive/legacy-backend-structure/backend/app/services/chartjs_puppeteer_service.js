// Chart.js + Puppeteer Service for MarketMind Pro
// Generates standard financial charts with professional styling

const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

class FinancialChartGenerator {
    constructor() {
        this.browser = null;
        this.chartTemplates = this.initializeTemplates();
    }

    async init() {
        try {
            this.browser = await puppeteer.launch({ 
                headless: true,
                args: [
                    '--no-sandbox', 
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            });
            console.log('📊 Chart.js + Puppeteer service initialized');
        } catch (error) {
            console.error('❌ Failed to initialize Puppeteer:', error);
            throw error;
        }
    }

    initializeTemplates() {
        return {
            revenue_trend: this.getRevenueTrendTemplate(),
            peer_comparison: this.getPeerComparisonTemplate(),
            segment_breakdown: this.getSegmentBreakdownTemplate(),
            financial_trends: this.getFinancialTrendsTemplate()
        };
    }

    async generateChart(chartType, data, options = {}) {
        if (!this.browser) {
            await this.init();
        }

        try {
            const template = this.chartTemplates[chartType];
            if (!template) {
                throw new Error(`Unknown chart type: ${chartType}`);
            }

            const chartConfig = template(data, options);
            return await this.renderChart(chartConfig, options);
        } catch (error) {
            console.error(`❌ Error generating ${chartType} chart:`, error);
            throw error;
        }
    }

    async renderChart(chartConfig, options = {}) {
        const page = await this.browser.newPage();
        
        try {
            // Set viewport for consistent rendering
            await page.setViewport({ 
                width: options.width || 1200, 
                height: options.height || 800 
            });

            const html = this.generateHTML(chartConfig, options);
            await page.setContent(html);
            
            // Wait for chart to render
            await page.waitForTimeout(2000);
            
            // Take screenshot of the chart
            const canvas = await page.$('#chart');
            if (!canvas) {
                throw new Error('Chart canvas not found');
            }
            
            const imageBuffer = await canvas.screenshot({ 
                type: 'png',
                omitBackground: false
            });
            
            return imageBuffer.toString('base64');
            
        } finally {
            await page.close();
        }
    }

    generateHTML(chartConfig, options = {}) {
        const theme = options.theme || 'professional';
        const styles = this.getThemeStyles(theme);
        
        return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>MarketMind Pro Chart</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
            <style>
                ${styles}
            </style>
        </head>
        <body>
            <div class="chart-container">
                <canvas id="chart"></canvas>
            </div>
            <script>
                // Professional Chart.js configuration
                Chart.defaults.font.family = 'Arial, sans-serif';
                Chart.defaults.font.size = 12;
                Chart.defaults.color = '#374151';
                
                const ctx = document.getElementById('chart').getContext('2d');
                const chartConfig = ${JSON.stringify(chartConfig)};
                
                // Apply professional styling
                if (chartConfig.options) {
                    chartConfig.options.responsive = false;
                    chartConfig.options.maintainAspectRatio = false;
                    chartConfig.options.plugins = chartConfig.options.plugins || {};
                    chartConfig.options.plugins.legend = chartConfig.options.plugins.legend || {};
                    chartConfig.options.plugins.legend.labels = {
                        ...chartConfig.options.plugins.legend.labels,
                        usePointStyle: true,
                        padding: 20,
                        font: { size: 11, weight: 'bold' }
                    };
                }
                
                new Chart(ctx, chartConfig);
            </script>
        </body>
        </html>
        `;
    }

    getThemeStyles(theme) {
        const themes = {
            professional: `
                body {
                    margin: 0;
                    padding: 20px;
                    background: #ffffff;
                    font-family: 'Arial', sans-serif;
                }
                .chart-container {
                    width: 800px;
                    height: 500px;
                    background: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                }
                #chart {
                    width: 100% !important;
                    height: 100% !important;
                }
            `,
            institutional: `
                body {
                    margin: 0;
                    padding: 30px;
                    background: #f8fafc;
                    font-family: 'Arial', sans-serif;
                }
                .chart-container {
                    width: 900px;
                    height: 600px;
                    background: white;
                    border: 2px solid #1f2937;
                    padding: 30px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                #chart {
                    width: 100% !important;
                    height: 100% !important;
                }
            `
        };
        
        return themes[theme] || themes.professional;
    }

    getRevenueTrendTemplate() {
        return (data, options) => ({
            type: 'line',
            data: {
                labels: data.periods || ['2022', '2023', '2024', '2025E', '2026E'],
                datasets: [{
                    label: 'Revenue ($B)',
                    data: data.revenue || [282.8, 307.4, 339.7, 375.2, 415.8],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }, {
                    label: 'Net Income ($B)',
                    data: data.net_income || [59.9, 73.8, 88.3, 98.1, 109.2],
                    borderColor: '#059669',
                    backgroundColor: 'rgba(5, 150, 105, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `${data.ticker || 'GOOGL'} - Revenue & Profitability Trend`,
                        font: { size: 18, weight: 'bold' },
                        padding: { bottom: 30 }
                    },
                    legend: {
                        display: true,
                        position: 'top',
                        align: 'end'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: '#374151',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Year',
                            font: { size: 14, weight: 'bold' }
                        },
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Amount ($ Billions)',
                            font: { size: 14, weight: 'bold' }
                        },
                        grid: { color: 'rgba(0, 0, 0, 0.1)' }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    getPeerComparisonTemplate() {
        return (data, options) => ({
            type: 'radar',
            data: {
                labels: ['P/E Ratio', 'EV/EBITDA', 'ROE (%)', 'Revenue Growth (%)', 'Operating Margin (%)'],
                datasets: data.companies?.map((company, index) => ({
                    label: company.name,
                    data: [
                        company.pe_ratio || 0,
                        company.ev_ebitda || 0,
                        company.roe || 0,
                        company.revenue_growth || 0,
                        company.margin || 0
                    ],
                    borderColor: this.getColorPalette()[index % this.getColorPalette().length],
                    backgroundColor: this.getColorPalette()[index % this.getColorPalette().length].replace('1)', '0.2)'),
                    pointBackgroundColor: this.getColorPalette()[index % this.getColorPalette().length],
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: this.getColorPalette()[index % this.getColorPalette().length],
                    borderWidth: 3,
                    pointRadius: 5,
                    pointHoverRadius: 7
                })) || []
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Peer Group Valuation Comparison',
                        font: { size: 18, weight: 'bold' },
                        padding: { bottom: 30 }
                    },
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: { padding: 20 }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: options.maxValue || 50,
                        ticks: {
                            stepSize: 10,
                            font: { size: 10 }
                        },
                        grid: { color: 'rgba(0, 0, 0, 0.1)' },
                        angleLines: { color: 'rgba(0, 0, 0, 0.1)' },
                        pointLabels: {
                            font: { size: 12, weight: 'bold' }
                        }
                    }
                }
            }
        });
    }

    getSegmentBreakdownTemplate() {
        return (data, options) => ({
            type: 'doughnut',
            data: {
                labels: data.segments?.map(s => s.name) || ['Search', 'YouTube', 'Cloud', 'Other Bets'],
                datasets: [{
                    data: data.segments?.map(s => s.revenue) || [175.0, 31.5, 33.1, 1.3],
                    backgroundColor: [
                        '#2563eb',
                        '#059669',
                        '#dc2626',
                        '#7c3aed',
                        '#ea580c'
                    ],
                    borderColor: '#ffffff',
                    borderWidth: 3,
                    hoverBorderWidth: 4
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `${data.ticker || 'GOOGL'} - Revenue Breakdown by Segment`,
                        font: { size: 18, weight: 'bold' },
                        padding: { bottom: 30 }
                    },
                    legend: {
                        display: true,
                        position: 'right',
                        labels: {
                            padding: 20,
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => {
                                        const value = data.datasets[0].data[i];
                                        const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        return {
                                            text: `${label}: $${value}B (${percentage}%)`,
                                            fillStyle: data.datasets[0].backgroundColor[i],
                                            strokeStyle: data.datasets[0].borderColor,
                                            lineWidth: data.datasets[0].borderWidth,
                                            hidden: false,
                                            index: i
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: $${value}B (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    getFinancialTrendsTemplate() {
        return (data, options) => ({
            type: 'line',
            data: {
                labels: data.periods || ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024'],
                datasets: [{
                    label: 'Revenue ($B)',
                    data: data.revenue || [69.8, 74.6, 76.7, 86.2, 80.5],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    yAxisID: 'y',
                    borderWidth: 3,
                    tension: 0.4
                }, {
                    label: 'Operating Margin (%)',
                    data: data.operating_margin || [25.0, 29.0, 24.0, 23.0, 32.0],
                    borderColor: '#dc2626',
                    backgroundColor: 'rgba(220, 38, 38, 0.1)',
                    yAxisID: 'y1',
                    borderWidth: 3,
                    tension: 0.4
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `${data.ticker || 'GOOGL'} - Quarterly Financial Trends`,
                        font: { size: 18, weight: 'bold' },
                        padding: { bottom: 30 }
                    },
                    legend: {
                        display: true,
                        position: 'top',
                        align: 'end'
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Quarter',
                            font: { size: 14, weight: 'bold' }
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Revenue ($ Billions)',
                            font: { size: 14, weight: 'bold' }
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Operating Margin (%)',
                            font: { size: 14, weight: 'bold' }
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
    }

    getColorPalette() {
        return [
            'rgba(37, 99, 235, 1)',   // Blue
            'rgba(220, 38, 38, 1)',   // Red
            'rgba(5, 150, 105, 1)',   // Green
            'rgba(124, 58, 237, 1)',  // Purple
            'rgba(234, 88, 12, 1)',   // Orange
            'rgba(219, 39, 119, 1)',  // Pink
            'rgba(6, 182, 212, 1)',   // Cyan
            'rgba(132, 204, 22, 1)'   // Lime
        ];
    }

    async close() {
        if (this.browser) {
            await this.browser.close();
            console.log('📊 Chart.js + Puppeteer service closed');
        }
    }
}

module.exports = FinancialChartGenerator;