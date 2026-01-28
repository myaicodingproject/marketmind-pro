#!/usr/bin/env python3
"""
MarketMind Pro Backend - Project Structure Verification
"""
import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def verify_project_structure():
    """Verify the complete project structure"""
    print("MarketMind Pro Backend - Structure Verification")
    print("=" * 60)
    
    base_path = "/mnt/c/kiro/backend"
    os.chdir(base_path)
    
    # Core files
    core_files = [
        ("requirements.txt", "Dependencies file"),
        (".env", "Environment configuration"),
        ("README.md", "Project documentation"),
        ("alembic.ini", "Database migration config"),
        ("start_server.sh", "Server startup script"),
        ("test_api.py", "API test script"),
        ("simple_test.py", "Basic test script"),
    ]
    
    # Application structure
    app_structure = [
        ("app/__init__.py", "App package init"),
        ("app/main.py", "FastAPI application"),
        ("app/core/__init__.py", "Core package init"),
        ("app/core/config.py", "Configuration settings"),
        ("app/shared/__init__.py", "Shared package init"),
        ("app/shared/database/__init__.py", "Database package init"),
        ("app/shared/database/connection.py", "Database connection"),
        ("app/shared/models/__init__.py", "Models package init"),
        ("app/shared/models/models.py", "SQLAlchemy models"),
        ("app/shared/schemas/__init__.py", "Schemas package init"),
        ("app/shared/schemas/schemas.py", "Pydantic schemas"),
        ("app/shared/utils/__init__.py", "Utils package init"),
        ("app/shared/utils/auth.py", "Authentication utilities"),
        ("app/shared/utils/kiro_integration.py", "Kiro CLI integration"),
        ("app/shared/utils/logging.py", "Logging configuration"),
        ("app/shared/utils/exceptions.py", "Error handling"),
    ]
    
    # Features
    features = [
        ("app/features/__init__.py", "Features package init"),
        ("app/features/auth/__init__.py", "Auth feature init"),
        ("app/features/auth/service.py", "Auth service"),
        ("app/features/auth/router.py", "Auth router"),
        ("app/features/reports/__init__.py", "Reports feature init"),
        ("app/features/reports/service.py", "Reports service"),
        ("app/features/reports/router.py", "Reports router"),
        ("app/features/companies/__init__.py", "Companies feature init"),
        ("app/features/companies/router.py", "Companies router"),
    ]
    
    # Database migrations
    migrations = [
        ("alembic/env.py", "Alembic environment"),
        ("alembic/versions/001_initial_migration.py", "Initial migration"),
    ]
    
    all_files = core_files + app_structure + features + migrations
    
    print("\n📁 Core Files:")
    core_count = sum(check_file_exists(f[0], f[1]) for f in core_files)
    
    print("\n🏗️ Application Structure:")
    app_count = sum(check_file_exists(f[0], f[1]) for f in app_structure)
    
    print("\n🎯 Features:")
    feature_count = sum(check_file_exists(f[0], f[1]) for f in features)
    
    print("\n🗄️ Database Migrations:")
    migration_count = sum(check_file_exists(f[0], f[1]) for f in migrations)
    
    total_files = len(all_files)
    total_found = core_count + app_count + feature_count + migration_count
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY:")
    print(f"   Core Files: {core_count}/{len(core_files)}")
    print(f"   App Structure: {app_count}/{len(app_structure)}")
    print(f"   Features: {feature_count}/{len(features)}")
    print(f"   Migrations: {migration_count}/{len(migrations)}")
    print(f"   TOTAL: {total_found}/{total_files}")
    
    if total_found == total_files:
        print("\n🎉 All files present! Backend foundation is complete.")
        return True
    else:
        print(f"\n⚠️  Missing {total_files - total_found} files. Please check the structure.")
        return False

def check_python_imports():
    """Check if key Python modules can be imported"""
    print("\n🐍 Python Import Verification:")
    print("-" * 40)
    
    imports_to_test = [
        ("fastapi", "FastAPI framework"),
        ("sqlalchemy", "SQLAlchemy ORM"),
        ("pydantic", "Pydantic validation"),
        ("jose", "JWT handling"),
        ("passlib", "Password hashing"),
        ("alembic", "Database migrations"),
    ]
    
    success_count = 0
    for module, description in imports_to_test:
        try:
            __import__(module)
            print(f"✅ {description}: {module}")
            success_count += 1
        except ImportError:
            print(f"❌ {description}: {module} (not installed)")
    
    print(f"\n📊 Import Summary: {success_count}/{len(imports_to_test)} modules available")
    return success_count == len(imports_to_test)

def main():
    """Main verification function"""
    structure_ok = verify_project_structure()
    imports_ok = check_python_imports()
    
    print("\n" + "=" * 60)
    if structure_ok and imports_ok:
        print("🚀 BACKEND FOUNDATION COMPLETE!")
        print("   ✅ Project structure verified")
        print("   ✅ Dependencies installed")
        print("   ✅ Ready for development")
        print("\n📝 Next Steps:")
        print("   1. Configure database connection")
        print("   2. Run database migrations")
        print("   3. Start the server: ./start_server.sh")
        print("   4. Test endpoints: python simple_test.py")
        return True
    else:
        print("❌ SETUP INCOMPLETE")
        print("   Please resolve the issues above before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)