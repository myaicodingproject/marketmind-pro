// Utility functions for parsing markdown tables and content

export const parseMarkdownTables = (content) => {
  if (!content) return { content, tables: [] };

  const tables = [];
  let processedContent = content;

  // Regex to match markdown tables
  const tableRegex = /\|(.+)\|\n\|[-\s|:]+\|\n((?:\|.+\|\n?)+)/g;
  
  let match;
  let tableIndex = 0;

  while ((match = tableRegex.exec(content)) !== null) {
    const [fullMatch, headerRow, bodyRows] = match;
    
    // Parse headers
    const headers = headerRow.split('|')
      .map(h => h.trim())
      .filter(h => h.length > 0);

    // Parse body rows
    const rows = bodyRows.trim().split('\n')
      .map(row => 
        row.split('|')
          .map(cell => cell.trim())
          .filter(cell => cell.length > 0)
      )
      .filter(row => row.length > 0);

    if (headers.length > 0 && rows.length > 0) {
      const tableId = `table-${tableIndex}`;
      tables.push({
        id: tableId,
        headers,
        data: rows,
        originalMatch: fullMatch
      });

      // Replace the markdown table with a placeholder
      processedContent = processedContent.replace(
        fullMatch, 
        `<div data-table-id="${tableId}"></div>`
      );
      
      tableIndex++;
    }
  }

  return { content: processedContent, tables };
};

export const isNumeric = (value) => {
  if (typeof value === 'string') {
    const cleanValue = value.replace(/[$,%\s]/g, '');
    return !isNaN(parseFloat(cleanValue)) && isFinite(cleanValue);
  }
  return !isNaN(parseFloat(value)) && isFinite(value);
};

export const formatCurrency = (value) => {
  if (!isNumeric(value)) return value;
  
  const numValue = typeof value === 'string' ? 
    parseFloat(value.replace(/[$,%\s]/g, '')) : 
    parseFloat(value);
    
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(numValue);
};

export const formatPercentage = (value) => {
  if (!isNumeric(value)) return value;
  
  const numValue = typeof value === 'string' ? 
    parseFloat(value.replace(/[%\s]/g, '')) : 
    parseFloat(value);
    
  return `${numValue.toFixed(2)}%`;
};

export const detectTableType = (headers, data) => {
  const headerText = headers.join(' ').toLowerCase();
  
  if (headerText.includes('revenue') || headerText.includes('income') || headerText.includes('earnings')) {
    return 'financial';
  }
  
  if (headerText.includes('ratio') || headerText.includes('margin') || headerText.includes('return')) {
    return 'metrics';
  }
  
  if (headerText.includes('year') || headerText.includes('quarter') || headerText.includes('period')) {
    return 'temporal';
  }
  
  return 'general';
};