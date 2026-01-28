# Global Rules for MarketMind Pro Development

## Project Context
MarketMind Pro is an AI-powered stock research platform that generates institutional-quality research reports using Kiro CLI for AI processing.

## Core Development Principles

### 1. Code Quality Standards
- **Type Safety**: Use Pydantic models for all data structures
- **Error Handling**: Comprehensive try-catch blocks with meaningful error messages
- **Logging**: Structured logging for all major operations
- **Testing**: Test critical paths before deployment
- **Documentation**: Clear docstrings for all public functions

### 2. Kiro CLI Integration
- **Custom Prompts**: Use specialized prompts for financial analysis tasks
- **Steering Documents**: Maintain up-to-date project context in `.kiro/steering/`
- **Workflow**: Follow `@prime` → `@plan-feature` → `@execute` → `@code-review` cycle
- **Quality Gates**: Use `@code-review-hackathon` before major commits

### 3. Architecture Guidelines
- **Universal Rendering**: Single source of truth for content (structured JSON blocks)
- **Separation of Concerns**: Backend (FastAPI), Frontend (React), Services (modular)
- **API Design**: RESTful endpoints with clear naming and versioning
- **State Management**: Centralized progress tracking for long-running operations

### 4. Content Standards
- **Structured Blocks**: Use typed content blocks (paragraph, heading, list, table, chart)
- **No HTML Strings**: Content as data, not markup
- **Consistency**: Frontend and PDF must render identically
- **Professional Quality**: Institutional-grade formatting and styling

### 5. Performance Requirements
- **Response Time**: API endpoints < 200ms (excluding AI processing)
- **Progress Updates**: Real-time WebSocket updates every 3 seconds
- **Demo Mode**: Complete in ~30 seconds for demo purposes
- **Caching**: Intelligent caching for repeated requests

### 6. Security & Privacy
- **No Sensitive Data**: Use placeholder data in examples
- **Environment Variables**: All secrets in `.env` (not committed)
- **Input Validation**: Validate all user inputs
- **Error Messages**: Don't expose internal details

### 7. Documentation Requirements
- **README.md**: Keep updated with setup instructions
- **DEVLOG.md**: Document all major decisions and changes
- **Code Comments**: Explain complex logic and business rules
- **API Docs**: FastAPI automatic documentation must be complete

### 8. Git Workflow
- **Commit Messages**: Clear, descriptive commit messages
- **Atomic Commits**: One logical change per commit
- **Branch Strategy**: Feature branches for major changes
- **Clean History**: Meaningful commit history for judges

### 9. Hackathon-Specific Rules
- **Demo First**: Ensure demo mode works perfectly
- **Documentation**: Prioritize README and DEVLOG quality
- **Kiro CLI Showcase**: Demonstrate extensive Kiro CLI usage
- **Innovation**: Highlight unique technical solutions
- **Presentation**: Professional, polished user experience

### 10. Testing & Validation
- **Manual Testing**: Test complete user journey before commits
- **Demo Mode**: Always test with "DEMO" ticker
- **Cross-Browser**: Verify in Chrome, Firefox, Safari
- **Fresh Install**: Test setup.sh on clean environment
- **PDF Generation**: Verify PDF quality and charts

## File Organization Rules

### Must Keep in Root
- `README.md` - Project documentation
- `DEVLOG.md` - Development log
- `setup.sh` - Automated setup script
- `deploy_production.sh` - Production deployment
- `complete_production_system.py` - Main backend

### Must Keep in .kiro/
- `steering/` - Project context and guidelines
- `prompts/` - Custom Kiro CLI commands
- `settings/` - Kiro CLI configuration

### Archive When Not Needed
- Test files → `archive/`
- Debug documentation → `archive/`
- Experimental code → `archive/`
- Old versions → `archive/`

## AI Processing Guidelines

### Kiro CLI Usage
- **Context Loading**: Always start with `@prime` for project context
- **Feature Planning**: Use `@plan-feature` for structured planning
- **Implementation**: Use `@execute` for systematic development
- **Quality Review**: Use `@code-review` for validation

### Custom Prompts
- **Naming**: Clear, descriptive prompt names
- **Documentation**: Each prompt should have clear purpose
- **Reusability**: Design prompts for multiple use cases
- **Organization**: Group related prompts in subdirectories

## Deployment Rules

### Before Deployment
1. Test demo mode completely
2. Verify all documentation is current
3. Check all scripts are executable
4. Ensure frontend is built
5. Test fresh installation with setup.sh

### Production Checklist
- [ ] Backend starts without errors
- [ ] Frontend loads correctly
- [ ] Demo mode works (DEMO ticker)
- [ ] PDF generation works
- [ ] All charts render correctly
- [ ] Progress tracking works
- [ ] Health check responds

## Hackathon Submission Rules

### Required Before Submission
1. **Documentation Complete**
   - README.md with setup instructions
   - DEVLOG.md with development timeline
   - All .kiro/ files organized

2. **Code Quality**
   - No commented-out code blocks
   - Clear variable names
   - Proper error handling
   - Meaningful commit messages

3. **Demo Ready**
   - Demo mode works perfectly
   - Progress timing is good for video
   - All features demonstrated
   - Professional appearance

4. **Video Prepared**
   - 3-5 minute demonstration
   - Clear audio and video
   - Shows key features
   - Explains value proposition

## Emergency Procedures

### If Demo Breaks
1. Check backend logs: `tail -f logs/backend.log`
2. Restart services: `./deploy_production.sh`
3. Test with DEMO ticker
4. Check browser console for errors

### If Build Fails
1. Clear node_modules: `rm -rf frontend/react-app/node_modules`
2. Reinstall: `cd frontend/react-app && npm install`
3. Rebuild: `npm run build`
4. Restart deployment

### If Git Issues
1. Check status: `git status`
2. Stash changes: `git stash`
3. Pull latest: `git pull`
4. Apply stash: `git stash pop`

## Success Metrics

### Code Quality
- Clean, readable code
- Proper error handling
- Good documentation
- Meaningful tests

### Kiro CLI Integration
- 50+ custom prompts
- Extensive steering documents
- Clear workflow demonstration
- Innovative usage patterns

### User Experience
- Fast, responsive interface
- Clear progress indication
- Professional appearance
- Intuitive navigation

### Documentation
- Complete README
- Detailed DEVLOG
- Clear setup instructions
- Comprehensive architecture docs

---

**Last Updated**: January 28, 2026  
**Project**: MarketMind Pro  
**Hackathon**: Dynamous Kiro Hackathon 2026
