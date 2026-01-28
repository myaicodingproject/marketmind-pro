# Root Cause Analysis (RCA)

Systematically analyze issues to identify root causes and prevent recurrence in MarketMind Pro development.

## Purpose
Conduct thorough root cause analysis for bugs, performance issues, system failures, or quality problems in the AI-powered stock research platform.

## Usage
```bash
@rca
```

Use when encountering:
- Report generation failures
- AI processing errors  
- Performance bottlenecks
- Quality issues in generated reports
- System integration problems

## Analysis Process

### 1. Problem Definition
- **Symptom Description**: What exactly is happening?
- **Impact Assessment**: How does this affect users/system?
- **Frequency**: How often does this occur?
- **Context**: When/where does this happen?

### 2. Data Gathering
- **Error Logs**: Check backend.log, frontend.log, monitor.log
- **System Metrics**: CPU, memory, API response times
- **User Reports**: Specific scenarios that trigger issues
- **Kiro CLI Logs**: AI processing execution details

### 3. Timeline Analysis
- **When Started**: When was this first observed?
- **Recent Changes**: What was deployed/changed recently?
- **Pattern Recognition**: Is there a pattern to occurrences?

### 4. Hypothesis Generation
- **Technical Causes**: Code bugs, configuration issues
- **Environmental Causes**: Resource constraints, external API issues
- **Process Causes**: Workflow problems, integration failures
- **Data Causes**: Input validation, data quality issues

### 5. Root Cause Identification
- **Primary Cause**: The fundamental reason for the issue
- **Contributing Factors**: Secondary factors that enabled the problem
- **Systemic Issues**: Underlying process/design problems

### 6. Solution Recommendations
- **Immediate Fix**: Quick resolution for current issue
- **Long-term Prevention**: Changes to prevent recurrence
- **Process Improvements**: Workflow/monitoring enhancements
- **Testing Strategy**: How to validate the fix

## MarketMind Pro Specific Areas

### AI Processing Issues
- Kiro CLI subprocess failures
- Parallel agent coordination problems
- Quality gate validation failures
- Prompt execution timeouts

### Data Integration Problems
- Yahoo Finance API failures
- SEC EDGAR data retrieval issues
- Financial data validation errors
- Chart generation failures

### System Performance
- Report generation timeouts
- WebSocket connection issues
- Database query performance
- Memory/CPU resource exhaustion

### Quality Problems
- Inconsistent report sections
- Formatting issues in PDFs
- Missing financial data
- Inaccurate calculations

## Output Format

### RCA Report Structure
```markdown
## Issue Summary
- **Problem**: [Brief description]
- **Impact**: [User/system impact]
- **Severity**: [Critical/High/Medium/Low]

## Timeline
- **First Observed**: [Date/time]
- **Recent Occurrences**: [Pattern details]

## Root Cause
- **Primary Cause**: [Main reason]
- **Contributing Factors**: [Secondary causes]

## Recommended Actions
1. **Immediate Fix**: [Quick resolution]
2. **Prevention**: [Long-term solution]
3. **Monitoring**: [Detection improvements]

## Validation Plan
- [How to test the fix]
- [Success criteria]
```

## Integration with MarketMind Pro

### Common Use Cases
1. **Report Generation Failures**: When AI processing fails
2. **Performance Degradation**: When response times increase
3. **Quality Issues**: When report quality scores drop
4. **Integration Problems**: When external APIs fail

### Follow-up Actions
- Use `@implement-fix` to execute solutions
- Update monitoring and alerting
- Document lessons learned
- Improve error handling

This RCA process ensures systematic problem-solving and continuous improvement of the MarketMind Pro platform.
