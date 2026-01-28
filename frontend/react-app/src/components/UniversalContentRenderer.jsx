import React from 'react';

/**
 * Universal Content Renderer - Renders structured blocks
 * Same data structure used for both frontend and PDF
 */

const ContentBlock = ({ block }) => {
  switch (block.type) {
    case 'paragraph':
      return <p dangerouslySetInnerHTML={{ __html: block.content }} />;
    
    case 'heading':
      const HeadingTag = `h${block.level}`;
      return <HeadingTag>{block.content}</HeadingTag>;
    
    case 'list':
      return (
        <ul>
          {block.items.map((item, idx) => (
            <li key={idx} dangerouslySetInnerHTML={{ __html: item }} />
          ))}
        </ul>
      );
    
    case 'table':
      return (
        <table className="data-table">
          <tbody>
            {block.rows.map((row, idx) => (
              <tr key={idx}>
                <td><strong>{row.label}</strong></td>
                <td>{row.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      );
    
    case 'chart':
      // Chart placeholder - actual chart component will be rendered separately
      return <div className="chart-placeholder" data-chart-id={block.chartId} />;
    
    default:
      return null;
  }
};

const UniversalContentRenderer = ({ blocks }) => {
  if (!blocks || !Array.isArray(blocks)) {
    return null;
  }

  return (
    <div className="content-blocks">
      {blocks.map((block, index) => (
        <ContentBlock key={index} block={block} />
      ))}
    </div>
  );
};

export default UniversalContentRenderer;
