// Sample chart data generator for testing advanced chart components
export const generateSampleChartData = (ticker = 'AAPL') => {
  return {
    executive_summary: {
      key_metrics: [
        { metric: "Price Target", value: 245, current: 220 },
        { metric: "Upside", value: 11.4, unit: "%" }
      ],
      recommendation: {
        rating: "BUY",
        confidence: 85,
        risk_level: "Medium"
      }
    },
    financial_analysis: {
      revenue_trend: [
        { year: "2022", revenue: 394.3, growth: 7.8, high: 410, base: 394.3, low: 380 },
        { year: "2023", revenue: 383.3, growth: -2.8, high: 395, base: 383.3, low: 370 },
        { year: "2024", revenue: 391.0, growth: 2.0, high: 405, base: 391.0, low: 378 },
        { year: "2025E", revenue: 405.2, growth: 3.6, high: 425, base: 405.2, low: 385 },
        { year: "2026E", revenue: 418.5, growth: 3.3, high: 445, base: 418.5, low: 395 }
      ],
      margins: [
        { metric: "Gross Margin", value: 46.2, trend: "up" },
        { metric: "Operating Margin", value: 29.8, trend: "stable" },
        { metric: "Net Margin", value: 25.1, trend: "up" }
      ],
      segment_breakdown: [
        { segment: "iPhone", revenue: 200.6, percentage: 51.3 },
        { segment: "Services", revenue: 85.2, percentage: 21.8 },
        { segment: "Mac", revenue: 29.4, percentage: 7.5 },
        { segment: "iPad", revenue: 28.3, percentage: 7.2 },
        { segment: "Wearables", revenue: 39.8, percentage: 10.2 }
      ],
      cash_flow_waterfall: [
        { category: "Operating CF", value: 104.0 },
        { category: "Capex", value: -10.7 },
        { category: "Acquisitions", value: -1.5 },
        { category: "Dividends", value: -14.8 },
        { category: "Share Buybacks", value: -77.6 },
        { category: "Net Change", value: -0.6 }
      ]
    },
    valuation_analysis: {
      peer_comparison: [
        { company: "AAPL", pe: 28.5, ev_ebitda: 22.1, price_sales: 7.8 },
        { company: "MSFT", pe: 32.1, ev_ebitda: 26.4, price_sales: 11.6 },
        { company: "GOOGL", pe: 24.8, ev_ebitda: 18.9, price_sales: 5.5 },
        { company: "META", pe: 23.2, ev_ebitda: 16.8, price_sales: 6.2 }
      ],
      dcf_sensitivity: {
        wacc: [8.5, 9.0, 9.2, 9.5, 10.0],
        growth: [2.5, 3.0, 3.5],
        values: [
          [225, 245, 270],
          [218, 235, 255],
          [215, 230, 248],
          [210, 223, 238],
          [203, 213, 225]
        ]
      },
      price_target_breakdown: [
        { method: "DCF", value: 230, weight: 40 },
        { method: "P/E Multiple", value: 243, weight: 30 },
        { method: "EV/EBITDA", value: 193, weight: 20 },
        { method: "Historical", value: 228, weight: 10 }
      ]
    },
    risk_assessment: {
      risk_matrix: [
        { risk: "China Exposure", probability: 40, impact: 8, severity: "High" },
        { risk: "Regulatory", probability: 60, impact: 6, severity: "Medium" },
        { risk: "Market Saturation", probability: 70, impact: 5, severity: "Medium" },
        { risk: "Supply Chain", probability: 30, impact: 7, severity: "Medium" },
        { risk: "Competition", probability: 80, impact: 4, severity: "Low" }
      ],
      scenario_analysis: [
        { scenario: "Bull", probability: 25, price_target: 285, return: 30 },
        { scenario: "Base", probability: 50, price_target: 245, return: 11 },
        { scenario: "Bear", probability: 25, price_target: 175, return: -20 }
      ]
    },
    market_analysis: {
      market_share: [
        { region: "North America", share: 58, growth: 2.1 },
        { region: "Europe", share: 28, growth: 1.5 },
        { region: "China", share: 17, growth: -2.3 },
        { region: "Rest of World", share: 15, growth: 5.8 }
      ],
      competitive_position: [
        { competitor: "Apple", market_share: 21.4, growth: 1.2 },
        { competitor: "Samsung", market_share: 23.1, growth: -0.8 },
        { competitor: "Xiaomi", market_share: 13.2, growth: 0.0 },
        { competitor: "Oppo", market_share: 10.8, growth: -1.5 }
      ]
    },
    // Legacy support for existing charts
    financial_performance: {
      revenue_trend: [
        { year: "2022", revenue: 394300, profit: 99803 },
        { year: "2023", revenue: 383285, profit: 96995 },
        { year: "2024", revenue: 391000, profit: 98000 },
        { year: "2025E", revenue: 405200, profit: 102000 },
        { year: "2026E", revenue: 418500, profit: 105000 }
      ],
      margins: [
        { metric: "Gross Margin", value: 46.2 },
        { metric: "Operating Margin", value: 29.8 },
        { metric: "Net Margin", value: 25.1 }
      ]
    },
    valuation_metrics: {
      peer_comparison: [
        { company: "AAPL", pe_ratio: 28.5, pb_ratio: 39.1 },
        { company: "MSFT", pe_ratio: 32.1, pb_ratio: 12.8 },
        { company: "GOOGL", pe_ratio: 24.8, pb_ratio: 5.9 }
      ]
    },
    risk_factors: [
      { factor: "China Exposure", impact: 8, probability: 4 },
      { factor: "Regulatory Risk", impact: 6, probability: 6 },
      { factor: "Market Saturation", impact: 5, probability: 7 },
      { factor: "Supply Chain", impact: 7, probability: 3 }
    ]
  };
};

// Function to inject sample data into existing reports for testing
export const injectSampleChartData = (report) => {
  if (!report.chart_data) {
    report.chart_data = generateSampleChartData(report.ticker);
  }
  return report;
};