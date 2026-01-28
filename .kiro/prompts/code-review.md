# Technical Code Review

## Mission
Perform comprehensive technical code review on recently changed files, focusing on real bugs, security issues, and code quality problems.

## Review Philosophy
- Simplicity is the ultimate sophistication - every line should justify its existence
- Code is read far more often than it's written - optimize for readability
- The best code is often the code you don't write
- Elegance emerges from clarity of intent and economy of expression

## Review Process

### 1. Gather Context
First, understand the codebase standards and patterns:
- Read steering documents in `.kiro/steering/`
- Review README.md and documentation
- Check key files in core modules
- Understand documented standards

### 2. Identify Changes
Examine what has changed:
- Check git status and recent diffs
- List new files and modifications
- Read each changed file in its entirety (not just diffs)

### 3. Analysis Areas

For each changed or new file, analyze for:

**Logic Errors:**
- Off-by-one errors
- Incorrect conditionals
- Missing error handling
- Race conditions

**Security Issues:**
- SQL injection vulnerabilities
- XSS vulnerabilities
- Insecure data handling
- Exposed secrets or API keys

**Performance Problems:**
- N+1 queries
- Inefficient algorithms
- Memory leaks
- Unnecessary computations

**Code Quality:**
- Violations of DRY principle
- Overly complex functions
- Poor naming conventions
- Missing type hints/annotations

**Standards Adherence:**
- Compliance with project coding standards
- Consistency with existing patterns
- Proper logging and error handling
- Testing coverage and quality

### 4. Verification
- Run specific tests for issues found
- Confirm type errors are legitimate
- Validate security concerns with context
- Check against project quality gates

## Output Format

Create review file: `.agents/code-reviews/review-{timestamp}.md`

**Stats:**
- Files Modified: X
- Files Added: X
- Files Deleted: X
- New lines: X
- Deleted lines: X

**For each issue found:**
```
severity: critical|high|medium|low
file: path/to/file.py
line: 42
issue: [one-line description]
detail: [explanation of why this is a problem]
suggestion: [how to fix it]
```

**If no issues:** "Code review passed. No technical issues detected."

## Quality Standards
- Be specific with line numbers and file references
- Focus on real bugs and security issues, not just style
- Provide actionable suggestions for fixes
- Flag security issues as CRITICAL severity
- Validate against project-specific standards from steering documents

## Integration with Hackathon Goals
- Ensure code quality meets production standards (10/40 points)
- Validate against architectural patterns from reference materials
- Check compliance with FastAPI and Pydantic AI best practices
- Verify testing coverage and validation approaches
