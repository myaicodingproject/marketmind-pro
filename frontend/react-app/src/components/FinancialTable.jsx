import React from 'react';

const FinancialTable = ({ data, headers, caption }) => {
  const isNumeric = (value) => {
    if (typeof value === 'string') {
      // Remove common formatting characters and check if it's a number
      const cleanValue = value.replace(/[$,%\s]/g, '');
      return !isNaN(parseFloat(cleanValue)) && isFinite(cleanValue);
    }
    return !isNaN(parseFloat(value)) && isFinite(value);
  };

  const formatNumber = (value) => {
    if (typeof value === 'number') {
      return value.toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
      });
    }
    
    if (typeof value === 'string' && isNumeric(value)) {
      const cleanValue = value.replace(/[$,%\s]/g, '');
      const numValue = parseFloat(cleanValue);
      return numValue.toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
      });
    }
    
    return value;
  };

  const getCellClass = (value) => {
    const classes = [];
    if (isNumeric(value)) {
      classes.push('numeric');
      const numValue = typeof value === 'string' ? 
        parseFloat(value.replace(/[$,%\s]/g, '')) : 
        parseFloat(value);
      
      if (numValue > 0) classes.push('positive');
      if (numValue < 0) classes.push('negative');
    }
    return classes.join(' ');
  };

  const getHeaderClass = (headerIndex) => {
    // Check if most values in this column are numeric
    const columnValues = data.map(row => row[headerIndex]);
    const numericCount = columnValues.filter(isNumeric).length;
    return numericCount > columnValues.length / 2 ? 'numeric' : '';
  };

  if (!data || !headers || data.length === 0) {
    return null;
  }

  return (
    <div className="table-container">
      {caption && <div className="table-caption">{caption}</div>}
      <table className="financial-table">
        <thead>
          <tr>
            {headers.map((header, idx) => (
              <th key={idx} className={getHeaderClass(idx)}>
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIdx) => (
            <tr key={rowIdx}>
              {row.map((cell, cellIdx) => (
                <td key={cellIdx} className={getCellClass(cell)}>
                  {formatNumber(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FinancialTable;