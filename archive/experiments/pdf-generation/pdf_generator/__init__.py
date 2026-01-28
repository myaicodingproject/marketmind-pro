"""
MarketMind Pro PDF Generator
TRACK C2-C4: Complete PDF Generation System

Production-ready PDF generation for institutional financial reports
- 30-page comprehensive reports
- Professional charts and tables
- Cover pages and table of contents
- Real-time generation status
- RESTful API interface
"""

from .core import MarketMindPDFGenerator
from .report_builder import InstitutionalReportBuilder
from .api import app

__version__ = "1.0.0"
__author__ = "MarketMind Pro Team"

__all__ = [
    "MarketMindPDFGenerator",
    "InstitutionalReportBuilder", 
    "app"
]