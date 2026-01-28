# Root Symlinks Archive

**Moved Date**: January 27, 2026  
**Reason**: Removing confusing symlinks for professional structure

## What Was Moved Here

### Symlinks from Root Directory
- **template_service.py** → services/template_service.py
- **chart_image_service.py** → services/chart_image_service.py  
- **content_parser_service.py** → services/content_parser_service.py
- **enhanced_models.py** → models/enhanced_models.py

## Why Moved
- **Professional Appearance**: Symlinks in root look unprofessional
- **Import Clarity**: Direct imports are clearer than symlinks
- **Deployment Simplicity**: Flat structure works better
- **Judge Confusion**: Symlinks confuse hackathon judges

## Recovery Instructions
If symlinks are needed again:
```bash
ln -s services/template_service.py template_service.py
ln -s services/chart_image_service.py chart_image_service.py
ln -s services/content_parser_service.py content_parser_service.py
ln -s models/enhanced_models.py enhanced_models.py
```

## Current Import Pattern
Instead of symlinks, use direct imports:
```python
from services.template_service import TemplateService
from services.chart_image_service import ChartImageService
from models.enhanced_models import ReportData
```
