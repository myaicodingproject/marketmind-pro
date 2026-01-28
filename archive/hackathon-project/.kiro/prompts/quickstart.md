---
description: Interactive setup wizard for hackathon project configuration
---

# Kiro CLI Quick Start Wizard

## Welcome
🚀 Welcome to the Kiro CLI Quick Start Wizard! This will help you set up your development environment with Kiro CLI by walking you through completing your project's steering documents and understanding all available features.

## Overview
This wizard will help you:
1. **Complete your steering documents** - Fill out the skeleton templates with your project details
2. **Understand your development workflow** - Learn about the available prompts and commands
3. **Explore advanced features** - Discover MCP servers, custom agents, hooks, and more

## Step 1: Complete Steering Documents

You already have skeleton steering documents in `.kiro/steering/`. Let's fill them out with your project details.

### Gather Project Information
**Note**: The more detailed you can be, the better! Specific information about what you're building, who it's for, and the components you want helps create better context for your coding assistant and future development work.

Ask the user these essential questions:

**Core Questions (Required):**
1. **Project Name**: "What's your project name?"
2. **Project Description**: "What does your project do? (1-2 sentences, or more detail if you'd like)"
3. **Target Users**: "Who will use this? (e.g., developers, end users, businesses - feel free to be specific about their needs)"
4. **Main Technology**: "What's your primary technology? (e.g., Python, JavaScript, React, etc.)"

**Optional Details:**
5. **Architecture** (if they want to specify): "Any specific architecture or patterns you're using? (optional - I can suggest based on your tech stack)"
6. **Special Requirements** (if any): "Any specific requirements for testing, deployment, or performance? (optional)"

### Update Steering Documents
After collecting responses, update the existing steering documents with intelligent defaults based on user responses and tech stack recommendations.

## Step 2: Development Workflow Overview

Now that your steering documents are complete, let's review your development workflow. You have access to these powerful prompts:

### Core Development Loop
- **`@prime`** - Load project context and understand your codebase
- **`@plan-feature`** - Create comprehensive implementation plans for new features
- **`@execute`** - Execute development plans with systematic task management
- **`@create-prd`** - Generate Product Requirements Documents

### Quality Assurance & Validation
- **`@code-review`** - Perform technical code reviews for quality and bugs
- **`@code-review-hackathon`** - Evaluate project against hackathon judging criteria
- **`@code-review-fix`** - Fix issues found in code reviews
- **`@execution-report`** - Generate implementation reports for completed work
- **`@system-review`** - Analyze implementation vs plan for process improvements

### GitHub Issue Management
- **`@rca`** - Perform root cause analysis for GitHub issues
- **`@implement-fix`** - Implement fixes based on RCA documents

### Typical Workflow
1. **Start with `@prime`** to understand your project context
2. **Use `@plan-feature`** to plan new features or changes
3. **Execute with `@execute`** to implement the plan systematically
4. **Review with `@code-review`** to ensure quality
5. **Generate reports** with `@execution-report` for documentation

## Step 3: Advanced Kiro Features

Beyond the core prompts, Kiro CLI offers powerful advanced features to enhance your development workflow:

### 🔧 MCP Servers (Model Context Protocol)
Connect external tools and APIs to extend Kiro's capabilities (AWS docs, git operations, database management, custom integrations).

### 🤖 Custom Agents
Create specialized AI assistants for specific workflows (backend specialist, frontend expert, DevOps agent, security reviewer, API designer).

### ⚡ Hooks (Automation)
Automate workflows and processes at specific lifecycle points (pre-commit hooks, post-deployment hooks, agent spawn hooks, tool execution hooks).

### 📚 Context Management
Optimize how Kiro understands your project (agent resources, session context, knowledge bases, context optimization).

## Step 4: Hackathon Success Strategy

### 🏆 Scoring Optimization (100 points total)
- **Application Quality (40 pts)**: Focus on functionality, value, and code quality
- **Kiro CLI Usage (20 pts)**: Extensive use of custom prompts and workflows
- **Documentation (20 pts)**: Complete README and DEVLOG with process transparency
- **Innovation (15 pts)**: Unique approach and creative problem-solving
- **Presentation (5 pts)**: Professional demo video and README

### 📅 7-Day Timeline Strategy
- **Day 1**: Foundation setup using AI-Optimized FastAPI command
- **Days 2-3**: Core feature development using PIV loop
- **Days 4-5**: Advanced features and polish
- **Day 6**: Integration testing and documentation
- **Day 7**: Final review and submission preparation

### ⚡ Immediate Next Steps
1. **Test your setup**: Try `@prime` to load your project context
2. **Plan your first feature**: Use `@plan-feature` for your next development task
3. **Set up foundation**: Execute AI-Optimized FastAPI command for instant production-ready base

## Completion Summary

🎉 **Kiro CLI Quick Start Complete!**

### ✅ What You've Accomplished
- **Steering Documents**: Completed with your project details
- **Development Workflow**: Ready to use 11+ powerful development prompts
- **Hackathon Strategy**: Aligned with 90+ point scoring target

### 🚀 **Your Development Arsenal**
**Core Workflow**: @prime → @plan-feature → @execute → @code-review
**Quality Assurance**: @code-review-hackathon, @code-review-fix, @system-review
**Hackathon Optimization**: Scoring-aware prompts and timeline strategy

### 💡 **Getting Started**
1. **Right now**: Try `@prime` to understand your project
2. **Next**: Use `@plan-feature` to plan your next development task
3. **Then**: Execute AI-Optimized FastAPI command for instant foundation

### 🏆 **Hackathon Reminders**
- **Build Your DEVLOG.md**: Document timeline, decisions, challenges, and Kiro usage
- **Optimize Your .kiro/ Directory**: Custom prompts and steering documents are part of submission
- **Use @code-review-hackathon**: Regular evaluation against judging criteria

**Welcome to supercharged development with Kiro CLI!** 🚀
