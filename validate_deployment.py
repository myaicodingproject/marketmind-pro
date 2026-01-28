#!/usr/bin/env python3
"""
Pre-deployment validation for MarketMind Pro clean system
Checks all components before starting production
"""

import sys
import os
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if required file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} MISSING: {filepath}")
        return False

def check_dependencies():
    """Check required Python packages"""
    required = {
        'plotly': 'Chart generation',
        'jinja2': 'Template rendering',
        'markdown': 'Markdown parsing',
        'bs4': 'HTML parsing',
        'weasyprint': 'PDF generation',
        'pydantic': 'Data validation',
        'psycopg2': 'PostgreSQL',
        'fastapi': 'API framework'
    }
    
    print("\n📦 Checking Dependencies...")
    all_ok = True
    for package, description in required.items():
        try:
            __import__(package)
            print(f"✅ {package}: {description}")
        except ImportError:
            print(f"❌ {package} MISSING: {description}")
            all_ok = False
    
    return all_ok

def check_database():
    """Check database schema"""
    print("\n🗄️ Checking Database Schema...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            "postgresql://postgres:postgres@localhost:5432/marketmind"
        )
        cur = conn.cursor()
        
        # Check for new columns
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'report_sections' 
            AND column_name IN ('tables_data', 'charts_data', 'metrics_data')
        """)
        columns = [row[0] for row in cur.fetchall()]
        
        if len(columns) == 3:
            print(f"✅ Database schema updated: {columns}")
            
            # Check chart_images table
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'chart_images'
                )
            """)
            if cur.fetchone()[0]:
                print("✅ chart_images table exists")
                conn.close()
                return True
            else:
                print("❌ chart_images table missing")
                conn.close()
                return False
        else:
            print(f"❌ Missing columns: {3 - len(columns)}")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def check_clean_system():
    """Check clean system components"""
    print("\n🏗️ Checking Clean System Components...")
    
    components = {
        'enhanced_models.py': 'Data models',
        'content_parser_service.py': 'Content parser',
        'chart_image_service.py': 'Chart generator',
        'template_service.py': 'Template renderer',
        'app/templates/section.html': 'Section template',
        'app/templates/report.html': 'Report template',
        'frontend-react/src/styles/print.css': 'Print CSS'
    }
    
    all_ok = True
    for filepath, description in components.items():
        if not check_file_exists(filepath, description):
            all_ok = False
    
    return all_ok

def check_css_system():
    """Check CSS files"""
    print("\n🎨 Checking CSS System...")
    
    css_files = [
        'frontend-react/src/styles/typography.css',
        'frontend-react/src/styles/colors.css',
        'frontend-react/src/styles/tables.css',
        'frontend-react/src/styles/sections.css',
        'frontend-react/src/styles/markdown.css',
        'frontend-react/src/styles/print.css'
    ]
    
    all_ok = True
    for css_file in css_files:
        if not check_file_exists(css_file, Path(css_file).name):
            all_ok = False
    
    return all_ok

def main():
    """Run all validation checks"""
    print("🔍 MarketMind Pro - Pre-Deployment Validation")
    print("=" * 60)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Database", check_database),
        ("Clean System", check_clean_system),
        ("CSS System", check_css_system)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Validation Summary:")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All checks passed! System ready for deployment.")
        print("👉 Run: ./deploy_production.sh")
        return 0
    else:
        print("\n⚠️ Some checks failed. Fix issues before deploying.")
        print("👉 Check error messages above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
