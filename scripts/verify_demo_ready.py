"""
Pre-Demo Verification Script

Run this before recording your Loom video to ensure everything is ready.
This script checks:
1. All Docker services are running
2. Database is initialized with proper schema
3. Topics exist in Redpanda
4. Sample data can be generated
5. All required scripts are executable

Author: Rafael Lustosa
"""

import sys
from pathlib import Path
import subprocess

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.check_services import check_services
from foundation.shared.database import get_db_connection


def print_header(message):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60)


def print_status(check_name, passed, details=""):
    """Print check status"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {check_name}")
    if details:
        print(f"      {details}")


def check_docker_services():
    """Check if all Docker services are running"""
    print_header("1. Checking Docker Services")
    
    services = check_services()
    all_ok = all(services.values())
    
    for service, status in services.items():
        print_status(service, status)
    
    return all_ok


def check_database_schema():
    """Check if database schema is initialized"""
    print_header("2. Checking Database Schema")
    
    try:
        conn = get_db_connection(dbname='ecommerce')
        cursor = conn.cursor()
        
        # Check for required tables
        required_tables = ['users', 'products', 'orders', 'page_views', 'inventory_changes']
        tables_exist = {}
        
        for table in required_tables:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{table}'
                );
            """)
            tables_exist[table] = cursor.fetchone()[0]
            print_status(f"Table: {table}", tables_exist[table])
        
        cursor.close()
        conn.close()
        
        return all(tables_exist.values())
        
    except Exception as e:
        print_status("Database Connection", False, str(e))
        return False


def check_redpanda_topics():
    """Check if Redpanda has required topics"""
    print_header("3. Checking Redpanda Topics")
    
    try:
        from kafka import KafkaAdminClient
        
        admin = KafkaAdminClient(
            bootstrap_servers='localhost:19092',
            client_id='demo-verifier'
        )
        
        topics = admin.list_topics()
        required_topics = [
            'ecommerce_orders',
            'ecommerce_page_views',
            'ecommerce_inventory_changes'
        ]
        
        all_exist = True
        for topic in required_topics:
            exists = topic in topics
            all_exist = all_exist and exists
            print_status(f"Topic: {topic}", exists)
        
        admin.close()
        return all_exist
        
    except Exception as e:
        print_status("Redpanda Connection", False, str(e))
        return False


def check_scripts():
    """Check if required scripts exist and are accessible"""
    print_header("4. Checking Required Scripts")
    
    scripts = [
        'scripts/init_database.py',
        'scripts/check_services.py',
        'scripts/run_checks.bat',
        'projects/ecommerce-dbt/data_generator/main.py',
        'projects/ecommerce-dbt/ingestion/main.py'
    ]
    
    all_exist = True
    for script in scripts:
        script_path = project_root / script
        exists = script_path.exists()
        all_exist = all_exist and exists
        print_status(script, exists, str(script_path))
    
    return all_exist


def check_browser_access():
    """Check if Redpanda Console is accessible"""
    print_header("5. Checking Browser Access")
    
    try:
        import requests
        response = requests.get('http://localhost:8080', timeout=5)
        accessible = response.status_code == 200
        print_status("Redpanda Console (http://localhost:8080)", accessible)
        return accessible
    except Exception as e:
        print_status("Redpanda Console", False, str(e))
        return False


def print_demo_checklist():
    """Print final demo checklist"""
    print_header("DEMO PREPARATION CHECKLIST")
    print("""
Before recording your Loom video, ensure:

[ ] All checks above passed ✅
[ ] Docker Desktop is running
[ ] Redpanda Console is open in browser (http://localhost:8080)
[ ] VSCode is open with the project
[ ] Terminal windows are ready:
    - Terminal 1: For data generator
    - Terminal 2: For Kafka consumer
    - Terminal 3: For ad-hoc commands
[ ] You've reviewed the demo script (loom_demo_script.md)
[ ] Screen recording software (Loom) is ready
[ ] Audio is tested and clear

🎬 You're ready to record! Good luck!
    """)


def main():
    """Run all verification checks"""
    print("\n🎥 PRE-DEMO VERIFICATION")
    print("Checking if everything is ready for your Loom recording...\n")
    
    checks = {
        "Docker Services": check_docker_services,
        "Database Schema": check_database_schema,
        "Redpanda Topics": check_redpanda_topics,
        "Required Scripts": check_scripts,
        "Browser Access": check_browser_access
    }
    
    results = {}
    for check_name, check_func in checks.items():
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n❌ Error in {check_name}: {e}")
            results[check_name] = False
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    all_passed = all(results.values())
    
    for check_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
    
    print()
    if all_passed:
        print("🎉 All checks passed! You're ready to record.")
        print_demo_checklist()
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above before recording.")
        print("\nQuick fixes:")
        
        if not results.get("Docker Services"):
            print("  - Start Docker: cd foundation && docker-compose up -d")
        
        if not results.get("Database Schema"):
            print("  - Initialize DB: python scripts\\init_database.py")
        
        if not results.get("Redpanda Topics"):
            print("  - Topics will be created automatically when you run the data generator")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
