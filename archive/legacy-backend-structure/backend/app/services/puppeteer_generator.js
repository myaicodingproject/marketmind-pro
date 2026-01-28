const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

async function generatePDF() {
    const dataPath = process.argv[2];
    
    if (!dataPath) {
        console.error('Usage: node puppeteer_generator.js <data_file_path>');
        process.exit(1);
    }
    
    try {
        console.log('Starting PDF generation...');
        
        // Read configuration
        const configData = JSON.parse(await fs.readFile(dataPath, 'utf8'));
        const { report_data, output_path, pdf_options, template_path, css_path } = configData;
        
        console.log(`Generating PDF for ${report_data.ticker || 'UNKNOWN'}`);
        
        // Launch browser with optimized settings for PDF generation
        const browser = await puppeteer.launch({
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-extensions',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ],
            timeout: 30000
        });
        
        const page = await browser.newPage();
        
        // Set viewport for consistent rendering
        await page.setViewport({ 
            width: 1200, 
            height: 1600,
            deviceScaleFactor: 2
        });
        
        // Read HTML template
        let htmlContent = await fs.readFile(template_path, 'utf8');
        console.log('Template loaded');
        
        // Process template variables
        htmlContent = processTemplate(htmlContent, report_data);
        
        // Read and inject CSS
        const cssContent = await fs.readFile(css_path, 'utf8');
        htmlContent = htmlContent.replace('/* CSS will be injected here by Puppeteer script */', cssContent);
        
        console.log('Setting page content...');
        
        // Set content with extended timeout
        await page.setContent(htmlContent, { 
            waitUntil: ['networkidle0', 'domcontentloaded'],
            timeout: 30000
        });
        
        // Wait for any dynamic content to load
        await page.waitForTimeout(2000);
        
        console.log('Generating PDF...');
        
        // Generate PDF with enhanced options
        await page.pdf({
            path: output_path,
            format: pdf_options.format || 'A4',
            margin: pdf_options.margin || {
                top: '1in',
                right: '0.75in',
                bottom: '1.25in',
                left: '0.75in'
            },
            printBackground: true,
            preferCSSPageSize: true,
            displayHeaderFooter: false, // Disable default headers/footers
            timeout: 60000
        });
        
        await browser.close();
        
        // Verify PDF was created
        const stats = await fs.stat(output_path);
        console.log(`✅ PDF generated successfully: ${output_path}`);
        console.log(`📄 File size: ${stats.size.toLocaleString()} bytes`);
        
    } catch (error) {
        console.error('❌ PDF generation error:', error.message);
        console.error('Stack trace:', error.stack);
        process.exit(1);
    }
}

function processTemplate(htmlContent, reportData) {
    // Basic template variable replacement
    htmlContent = htmlContent
        .replace(/{{ ticker }}/g, reportData.ticker || 'UNKNOWN')
        .replace(/{{ title }}/g, reportData.title || 'Stock Analysis Report')
        .replace(/{{ generated_date }}/g, reportData.generated_date || new Date().toLocaleDateString());
    
    // Process sections
    let sectionsHtml = '';
    if (reportData.sections) {
        let sectionIndex = 1;
        
        for (const [sectionKey, section] of Object.entries(reportData.sections)) {
            if (!section || !section.title) continue;
            
            const sectionTitle = section.title || formatSectionKey(sectionKey);
            const sectionContent = formatContent(section.content || '');
            
            sectionsHtml += `
                <div class="page-break"></div>
                <div class="report-section">
                    <div class="section-header">
                        <h2 class="section-title">${sectionIndex}. ${sectionTitle}</h2>
                        <div class="section-divider"></div>
                    </div>
                    <div class="section-content">
                        ${sectionContent}
                    </div>
                    ${processSubsections(section.subsections || [])}
                </div>
            `;
            sectionIndex++;
        }
    }
    
    // Replace sections placeholder
    htmlContent = htmlContent.replace('<!-- SECTIONS_PLACEHOLDER -->', sectionsHtml);
    
    return htmlContent;
}

function processSubsections(subsections) {
    if (!Array.isArray(subsections) || subsections.length === 0) {
        return '';
    }
    
    let subsectionsHtml = '';
    for (const subsection of subsections) {
        if (subsection.title && subsection.content) {
            subsectionsHtml += `
                <div class="subsection">
                    <h3 class="subsection-title">${subsection.title}</h3>
                    <div class="subsection-content">
                        ${formatContent(subsection.content)}
                    </div>
                </div>
            `;
        }
    }
    
    return subsectionsHtml;
}

function formatSectionKey(key) {
    return key
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

function formatContent(content) {
    if (!content || typeof content !== 'string') {
        return '<p>Content not available</p>';
    }
    
    // Clean content first
    content = cleanContent(content);
    
    // Convert markdown-style formatting to HTML
    content = content
        // Bold text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/__(.*?)__/g, '<strong>$1</strong>')
        // Italic text
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/_(.*?)_/g, '<em>$1</em>')
        // Headers (convert to appropriate HTML)
        .replace(/^### (.*$)/gm, '<h4>$1</h4>')
        .replace(/^## (.*$)/gm, '<h3>$1</h3>')
        .replace(/^# (.*$)/gm, '<h2>$1</h2>');
    
    // Process lists
    content = processLists(content);
    
    // Process tables
    content = processTables(content);
    
    // Convert paragraphs
    content = processParagraphs(content);
    
    return content;
}

function cleanContent(content) {
    // Remove AI system messages and artifacts
    const cleaningPatterns = [
        /Invoking \d+ subagents in parallel \(using tool: [^)]+\)/g,
        /Searching the web for: [^\n]+\(using tool: web_search\)/g,
        /using tool: [^\n]+/g,
        /> I'll [^\n]+/g,
        /> [^\n]*/g,
        /\d+: \+ \d+:/g,
        /■{3,}/g,
        /━{3,}/g,
        /References:\s*\[\d+\][^\n]*\n/g,
        /\[.*?\]\(.*?\)/g,
        /```[^`]*```/g,
        /`[^`]+`/g,
        /^\s*[-=]{3,}\s*$/gm,
        /^\s*\*\s*\*\s*\*\s*$/gm
    ];
    
    for (const pattern of cleaningPatterns) {
        content = content.replace(pattern, '');
    }
    
    // Clean up excessive whitespace
    content = content
        .replace(/\n{3,}/g, '\n\n')
        .replace(/[ \t]+/g, ' ')
        .replace(/^\s+/gm, '')
        .replace(/\s+$/gm, '')
        .trim();
    
    return content;
}

function processLists(content) {
    // Process bullet lists
    const lines = content.split('\n');
    const processedLines = [];
    let inList = false;
    let listItems = [];
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // Check if line is a bullet point
        if (/^[•\-\*]\s+/.test(line)) {
            if (!inList) {
                inList = true;
                listItems = [];
            }
            const item = line.replace(/^[•\-\*]\s+/, '').trim();
            listItems.push(`<li>${item}</li>`);
        } else {
            // End of list
            if (inList) {
                processedLines.push(`<ul>${listItems.join('')}</ul>`);
                listItems = [];
                inList = false;
            }
            
            if (line) {
                processedLines.push(line);
            }
        }
    }
    
    // Handle list at end of content
    if (inList && listItems.length > 0) {
        processedLines.push(`<ul>${listItems.join('')}</ul>`);
    }
    
    return processedLines.join('\n');
}

function processTables(content) {
    const lines = content.split('\n');
    const processedLines = [];
    let inTable = false;
    let tableRows = [];
    
    for (const line of lines) {
        const trimmed = line.trim();
        
        // Check if line looks like a table row
        if (trimmed.includes('|') && trimmed.split('|').length >= 3) {
            if (!inTable) {
                inTable = true;
                tableRows = [];
            }
            
            // Parse table row
            const cells = trimmed.split('|')
                .map(cell => cell.trim())
                .filter(cell => cell !== '');
            
            // Skip separator rows
            if (cells.every(cell => /^-+$/.test(cell))) {
                continue;
            }
            
            tableRows.push(cells);
        } else {
            // End of table
            if (inTable && tableRows.length > 0) {
                processedLines.push(createHtmlTable(tableRows));
                tableRows = [];
                inTable = false;
            }
            
            processedLines.push(line);
        }
    }
    
    // Handle table at end
    if (inTable && tableRows.length > 0) {
        processedLines.push(createHtmlTable(tableRows));
    }
    
    return processedLines.join('\n');
}

function createHtmlTable(rows) {
    if (rows.length === 0) return '';
    
    let html = '<table class="data-table">';
    
    // Header row
    if (rows.length > 0) {
        html += '<thead><tr>';
        for (const cell of rows[0]) {
            html += `<th>${cell}</th>`;
        }
        html += '</tr></thead>';
    }
    
    // Body rows
    if (rows.length > 1) {
        html += '<tbody>';
        for (let i = 1; i < rows.length; i++) {
            html += '<tr>';
            for (const cell of rows[i]) {
                html += `<td>${cell}</td>`;
            }
            html += '</tr>';
        }
        html += '</tbody>';
    }
    
    html += '</table>';
    return html;
}

function processParagraphs(content) {
    // Split content into paragraphs and wrap in <p> tags
    const paragraphs = content.split(/\n\s*\n/);
    const processedParagraphs = [];
    
    for (let para of paragraphs) {
        para = para.trim();
        if (!para) continue;
        
        // Skip if already HTML
        if (para.startsWith('<') && para.endsWith('>')) {
            processedParagraphs.push(para);
        } else {
            // Wrap in paragraph tags
            processedParagraphs.push(`<p>${para}</p>`);
        }
    }
    
    return processedParagraphs.join('\n\n');
}

// Run the PDF generation
generatePDF().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});