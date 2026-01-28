# Implement Fix

Systematically implement fixes based on root cause analysis for MarketMind Pro issues.

## Purpose
Execute solutions identified through `@rca` analysis with proper testing, validation, and documentation.

## Usage
```bash
@implement-fix
```

Use after completing `@rca` to implement solutions for:
- AI processing failures
- Performance bottlenecks
- Quality issues
- System integration problems
- User experience improvements

## Implementation Process

### 1. Solution Review
- **RCA Reference**: Review root cause analysis findings
- **Solution Validation**: Confirm proposed fix addresses root cause
- **Impact Assessment**: Evaluate potential side effects
- **Resource Requirements**: Estimate time and complexity

### 2. Implementation Planning
- **Approach Strategy**: How to implement the fix
- **Testing Strategy**: How to validate the solution
- **Rollback Plan**: How to revert if issues arise
- **Deployment Method**: Staging vs production approach

### 3. Code Implementation
- **Focused Changes**: Minimal, targeted modifications
- **Code Quality**: Follow MarketMind Pro standards
- **Error Handling**: Robust error management
- **Logging**: Enhanced logging for monitoring

### 4. Testing & Validation
- **Unit Testing**: Test individual components
- **Integration Testing**: Test system interactions
- **Performance Testing**: Validate performance improvements
- **User Acceptance**: Verify user experience improvements

### 5. Deployment & Monitoring
- **Staged Deployment**: Gradual rollout approach
- **Monitoring Setup**: Enhanced monitoring for the fix
- **Success Metrics**: Define success criteria
- **Documentation**: Update relevant documentation

## MarketMind Pro Implementation Areas

### AI Processing Fixes
```python
# Example: Fix Kiro CLI subprocess timeout
def execute_kiro_agent_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ['kiro-cli', 'chat', prompt],
                timeout=300,  # 5 minute timeout
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout
        except subprocess.TimeoutExpired:
            if attempt < max_retries - 1:
                continue
            raise TimeoutError(f"Kiro CLI timeout after {max_retries} attempts")
    return None
```

### Performance Optimization
```python
# Example: Implement caching for financial data
@lru_cache(maxsize=1000)
def get_financial_data(symbol, data_type):
    # Cache financial data to reduce API calls
    return fetch_from_api(symbol, data_type)
```

### Quality Improvements
```python
# Example: Enhanced quality validation
def validate_report_section(section_content):
    quality_checks = [
        check_completeness(section_content),
        check_accuracy(section_content),
        check_formatting(section_content)
    ]
    return all(quality_checks)
```

### Error Handling Enhancement
```python
# Example: Improved error handling
try:
    report = generate_financial_report(symbol)
except APIError as e:
    logger.error(f"API error for {symbol}: {e}")
    return fallback_report_generation(symbol)
except ValidationError as e:
    logger.error(f"Validation error: {e}")
    return retry_with_different_approach(symbol)
```

## Implementation Checklist

### Pre-Implementation
- [ ] RCA analysis completed
- [ ] Solution approach validated
- [ ] Testing strategy defined
- [ ] Rollback plan prepared

### During Implementation
- [ ] Code changes minimal and focused
- [ ] Error handling enhanced
- [ ] Logging added for monitoring
- [ ] Unit tests updated/added

### Post-Implementation
- [ ] Integration tests passed
- [ ] Performance validated
- [ ] Monitoring configured
- [ ] Documentation updated

## Validation Criteria

### Technical Validation
- **Functionality**: Fix resolves the identified issue
- **Performance**: No degradation in system performance
- **Stability**: No new issues introduced
- **Compatibility**: Works with existing system components

### Business Validation
- **User Experience**: Improved user satisfaction
- **Quality Metrics**: Better report quality scores
- **Reliability**: Reduced error rates
- **Efficiency**: Faster processing times

## Documentation Requirements

### Code Documentation
- **Change Summary**: What was changed and why
- **Implementation Details**: How the fix works
- **Testing Results**: Validation outcomes
- **Monitoring Setup**: How to monitor the fix

### Process Documentation
- **Lessons Learned**: Key insights from the fix
- **Prevention Measures**: How to avoid similar issues
- **Monitoring Improvements**: Enhanced detection capabilities
- **Knowledge Sharing**: Team communication about the fix

## Integration with MarketMind Pro Workflow

### Development Process
1. **Issue Identification** → `@rca` analysis
2. **Root Cause Found** → `@implement-fix` execution
3. **Fix Deployed** → Monitor and validate
4. **Success Confirmed** → Document and share learnings

### Quality Assurance
- Use `@code-review` after implementation
- Run `@system-review` to validate system integrity
- Execute `@quality-audit` for report quality validation

### Continuous Improvement
- Update monitoring and alerting based on fixes
- Enhance error handling patterns
- Improve development processes
- Share knowledge with team

This systematic approach ensures reliable, well-tested fixes that improve MarketMind Pro's stability and performance.
