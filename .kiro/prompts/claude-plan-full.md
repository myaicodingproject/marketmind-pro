# Claude Plan Feature (Full Version)

## Feature: $ARGUMENTS

## Mission
Transform a feature request into a **comprehensive implementation plan** through systematic codebase analysis, external research, and strategic planning using Claude's full methodology.

**Core Principle**: We do NOT write code in this phase. Our goal is to create a context-rich implementation plan that enables one-pass implementation success for ai agents.

**Key Philosophy**: Context is King. The plan must contain ALL information needed for implementation - patterns, mandatory reading, documentation, validation commands - so the execution agent succeeds on the first attempt.

## Planning Process

### Phase 1: Feature Understanding

**Deep Feature Analysis:**
- Extract the core problem being solved
- Identify user value and business impact
- Determine feature type: New Capability/Enhancement/Refactor/Bug Fix
- Assess complexity: Low/Medium/High
- Map affected systems and components

**Create User Story Format Or Refine If Story Was Provided By The User:**
```
As a <type of user>
I want to <action/goal>
So that <benefit/value>
```

### Phase 2: Codebase Intelligence Gathering

**1. Project Structure Analysis**
- Detect primary language(s), frameworks, and runtime versions
- Map directory structure and architectural patterns
- Identify service/component boundaries and integration points
- Locate configuration files (pyproject.toml, package.json, etc.)
- Find environment setup and build processes

**2. Pattern Recognition**
- Search for similar implementations in codebase
- Identify coding conventions from steering documents in `.kiro/steering/`
- Extract common patterns for the feature's domain
- Document anti-patterns to avoid
- Check project-specific rules and conventions

**3. Dependency Analysis**
- Catalog external libraries relevant to feature
- Understand how libraries are integrated (check imports, configs)
- Find relevant documentation in docs/, ai_docs/, .agents/reference or ai-wiki if available
- Note library versions and compatibility requirements

**4. Testing Patterns**
- Identify test framework and structure (pytest, jest, etc.)
- Find similar test examples for reference
- Understand test organization (unit vs integration)
- Note coverage requirements and testing standards

**5. Integration Points**
- Identify existing files that need updates
- Determine new files that need creation and their locations
- Map router/API registration patterns
- Understand database/model patterns if applicable
- Identify authentication/authorization patterns if relevant

### Phase 3: External Research & Documentation

**Documentation Gathering:**
- Research latest library versions and best practices
- Find official documentation with specific section anchors
- Locate implementation examples and tutorials
- Identify common gotchas and known issues
- Check for breaking changes and migration guides

**Technology Trends:**
- Research current best practices for the technology stack
- Find relevant blog posts, guides, or case studies
- Identify performance optimization patterns
- Document security considerations

### Phase 4: Deep Strategic Thinking

**Think Harder About:**
- How does this feature fit into the existing architecture?
- What are the critical dependencies and order of operations?
- What could go wrong? (Edge cases, race conditions, errors)
- How will this be tested comprehensively?
- What performance implications exist?
- Are there security considerations?
- How maintainable is this approach?

**Design Decisions:**
- Choose between alternative approaches with clear rationale
- Design for extensibility and future modifications
- Plan for backward compatibility if needed
- Consider scalability implications

### Phase 5: Plan Structure Generation

Create comprehensive plan following Claude's full template structure with:
- Feature Description & User Story
- Context References with specific file:line numbers
- Implementation Plan with phased approach
- Step-by-Step Tasks (atomic and testable)
- Testing Strategy
- Validation Commands (executable)
- Acceptance Criteria

## Output Format
**Filename**: `.agents/plans/{kebab-case-descriptive-name}.md`

## Success Metrics
**One-Pass Implementation**: Execution agent can complete feature without additional research or clarification
**Validation Complete**: Every task has at least one working validation command
**Context Rich**: The Plan passes "No Prior Knowledge Test"
**Confidence Score**: #/10 that execution will succeed on first attempt
