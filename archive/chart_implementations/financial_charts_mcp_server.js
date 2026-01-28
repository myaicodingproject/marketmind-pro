#!/usr/bin/env node

// MCP Server for Financial Chart Generation
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import puppeteer from 'puppeteer';

class FinancialChartMCPServer {
  constructor() {
    this.server = new Server({
      name: "financial-charts-mcp",
      version: "1.0.0",
    }, {
      capabilities: {
        tools: {},
      },
    });

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "generate_dcf_chart",
          description: "Generate DCF waterfall chart for financial analysis",
          inputSchema: {
            type: "object",
            properties: {
              cashFlows: {
                type: "object",
                description: "Cash flows by year (e.g., {'2024': 1000000, '2025': 1200000})"
              },
              discountRate: {
                type: "number",
                description: "Discount rate (WACC) as decimal (e.g., 0.10 for 10%)"
              },
              terminalValue: {
                type: "number",
                description: "Terminal value in dollars"
              }
            },
            required: ["cashFlows", "discountRate"]
          }
        },
        {
          name: "generate_peer_comparison",
          description: "Generate peer comparison radar chart",
          inputSchema: {
            type: "object",
            properties: {
              companies: {
                type: "array",
                items: {
                  type: "object",
                  properties: {
                    name: { type: "string" },
                    pe_ratio: { type: "number" },
                    ev_ebitda: { type: "number" },
                    pb_ratio: { type: "number" },
                    roe: { type: "number" },
                    debt_equity: { type: "number" }
                  }
                }
              }
            },
            required: ["companies"]
          }
        },
        {
          name: "generate_trend_chart",
          description: "Generate financial trend line chart",
          inputSchema: {
            type: "object",
            properties: {
              data: {
                type: "array",
                items: {
                  type: "object",
                  properties: {
                    period: { type: "string" },
                    revenue: { type: "number" },
                    profit: { type: "number" },
                    margin: { type: "number" }
                  }
                }
              },
              title: { type: "string" }
            },
            required: ["data"]
          }
        }
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "generate_dcf_chart":
            return await this.generateDCFChart(args);
          case "generate_peer_comparison":
            return await this.generatePeerComparison(args);
          case "generate_trend_chart":
            return await this.generateTrendChart(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: `Error generating chart: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async generateDCFChart({ cashFlows, discountRate, terminalValue = 0 }) {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    const years = Object.keys(cashFlows);
    const values = Object.values(cashFlows);
    const pvValues = values.map((cf, i) => cf / Math.pow(1 + discountRate, i));
    
    if (terminalValue > 0) {
      years.push('Terminal');
      pvValues.push(terminalValue / Math.pow(1 + discountRate, years.length - 1));
    }

    const chartConfig = {
      type: 'bar',
      data: {
        labels: years,
        datasets: [{
          label: 'Present Value ($M)',
          data: pvValues.map(v => v / 1000000),
          backgroundColor: '#2563eb',
          borderColor: '#1d4ed8',
          borderWidth: 2
        }]
      },
      options: {
        responsive: false,
        plugins: {
          title: { 
            display: true, 
            text: 'DCF Valuation Analysis',
            font: { size: 18, weight: 'bold' }
          },
          legend: { display: false }
        },
        scales: {
          y: { 
            beginAtZero: true,
            title: { display: true, text: 'Present Value ($M)' }
          }
        }
      }
    };

    const html = this.generateChartHTML(chartConfig);
    await page.setContent(html);
    await page.waitForTimeout(1000);
    
    const canvas = await page.$('#chart');
    const imageBuffer = await canvas.screenshot({ type: 'png' });
    
    await browser.close();

    return {
      content: [
        {
          type: "text",
          text: `DCF chart generated successfully. Enterprise Value: $${(pvValues.reduce((a, b) => a + b, 0) / 1000000).toFixed(1)}M`,
        },
        {
          type: "image",
          data: imageBuffer.toString('base64'),
          mimeType: "image/png",
        },
      ],
    };
  }

  async generatePeerComparison({ companies }) {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    const chartConfig = {
      type: 'radar',
      data: {
        labels: ['P/E Ratio', 'EV/EBITDA', 'P/B Ratio', 'ROE (%)', 'Debt/Equity'],
        datasets: companies.map((company, i) => ({
          label: company.name,
          data: [
            company.pe_ratio || 0,
            company.ev_ebitda || 0,
            company.pb_ratio || 0,
            company.roe || 0,
            company.debt_equity || 0
          ],
          borderColor: `hsl(${i * 60}, 70%, 50%)`,
          backgroundColor: `hsla(${i * 60}, 70%, 50%, 0.2)`,
          pointBackgroundColor: `hsl(${i * 60}, 70%, 50%)`,
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: `hsl(${i * 60}, 70%, 50%)`
        }))
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
          r: { 
            beginAtZero: true,
            max: 30,
            ticks: { stepSize: 5 }
          }
        }
      }
    };

    const html = this.generateChartHTML(chartConfig);
    await page.setContent(html);
    await page.waitForTimeout(1000);
    
    const canvas = await page.$('#chart');
    const imageBuffer = await canvas.screenshot({ type: 'png' });
    
    await browser.close();

    return {
      content: [
        {
          type: "text",
          text: `Peer comparison chart generated for ${companies.length} companies`,
        },
        {
          type: "image",
          data: imageBuffer.toString('base64'),
          mimeType: "image/png",
        },
      ],
    };
  }

  async generateTrendChart({ data, title = "Financial Trends" }) {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    const chartConfig = {
      type: 'line',
      data: {
        labels: data.map(d => d.period),
        datasets: [
          {
            label: 'Revenue ($M)',
            data: data.map(d => d.revenue / 1000000),
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37, 99, 235, 0.1)',
            yAxisID: 'y'
          },
          {
            label: 'Profit ($M)',
            data: data.map(d => d.profit / 1000000),
            borderColor: '#059669',
            backgroundColor: 'rgba(5, 150, 105, 0.1)',
            yAxisID: 'y'
          },
          {
            label: 'Margin (%)',
            data: data.map(d => d.margin * 100),
            borderColor: '#dc2626',
            backgroundColor: 'rgba(220, 38, 38, 0.1)',
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: false,
        plugins: {
          title: { 
            display: true, 
            text: title,
            font: { size: 18, weight: 'bold' }
          }
        },
        scales: {
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            title: { display: true, text: 'Revenue/Profit ($M)' }
          },
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            title: { display: true, text: 'Margin (%)' },
            grid: { drawOnChartArea: false }
          }
        }
      }
    };

    const html = this.generateChartHTML(chartConfig);
    await page.setContent(html);
    await page.waitForTimeout(1000);
    
    const canvas = await page.$('#chart');
    const imageBuffer = await canvas.screenshot({ type: 'png' });
    
    await browser.close();

    return {
      content: [
        {
          type: "text",
          text: `Financial trend chart generated for ${data.length} periods`,
        },
        {
          type: "image",
          data: imageBuffer.toString('base64'),
          mimeType: "image/png",
        },
      ],
    };
  }

  generateChartHTML(chartConfig) {
    return `
      <html>
        <head>
          <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body style="margin: 0; padding: 20px; background: white; font-family: Arial, sans-serif;">
          <canvas id="chart" width="800" height="600"></canvas>
          <script>
            const ctx = document.getElementById('chart').getContext('2d');
            new Chart(ctx, ${JSON.stringify(chartConfig)});
          </script>
        </body>
      </html>
    `;
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Financial Charts MCP server running on stdio");
  }
}

const server = new FinancialChartMCPServer();
server.run().catch(console.error);