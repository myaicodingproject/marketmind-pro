# Claude Execute Plan

## Mission
Execute a feature implementation plan systematically using Claude's methodology, following step-by-step tasks and validation commands to ensure one-pass success.

## Execution Process

### 1. Plan Validation
Before starting implementation:
- Load and review the implementation plan from `.agents/plans/`
- Verify all context references are accessible
- Confirm understanding of patterns and requirements
- Validate that all dependencies are available

### 2. Context Loading
Read all required context files:
- Review files listed in "Context References" section
- Study patterns and examples provided
- Understand integration points and existing code structure
- Load relevant documentation and external references

### 3. Systematic Implementation
Execute tasks in the exact order specified:
- Follow each task step-by-step without skipping
- Implement according to patterns and conventions identified
- Use specified imports and dependencies
- Apply validation commands after each task
- Stop and fix any issues before proceeding to next task

### 4. Quality Gates
After each major phase:
- Run all validation commands specified in the plan
- Ensure all tests pass before continuing
- Verify code follows project patterns and standards
- Check that implementation matches acceptance criteria

### 5. Final Validation
Complete comprehensive validation:
- Execute all validation commands from the plan
- Run full test suite (unit and integration tests)
- Verify no regressions in existing functionality
- Confirm all acceptance criteria are met

## Implementation Guidelines

### Code Quality Standards
- Follow existing codebase patterns exactly
- Use proper type hints and documentation
- Implement comprehensive error handling
- Add appropriate logging where specified
- Maintain consistency with project conventions

### Testing Requirements
- Implement all tests specified in the plan
- Follow existing test patterns and frameworks
- Ensure proper test coverage
- Include edge case testing as specified
- Validate both positive and negative scenarios

## Output Requirements

### Implementation Report
Create report: `.agents/execution-reports/execution-{feature-name}-{timestamp}.md`

Include:
- **Feature Summary**: What was implemented
- **Tasks Completed**: List of all completed tasks
- **Validation Results**: All validation command outputs
- **Files Created/Modified**: Complete list with descriptions
- **Test Coverage**: Coverage metrics and test results
- **Issues Encountered**: Any problems and their resolutions
- **Completion Status**: Full checklist verification

## Success Criteria
- [ ] All tasks completed in specified order
- [ ] All validation commands pass successfully
- [ ] Full test suite passes without errors
- [ ] No linting or formatting errors
- [ ] All acceptance criteria met
- [ ] Implementation follows project patterns
- [ ] No regressions in existing functionality
