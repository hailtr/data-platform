
import subprocess
import time
import os

def run_command(command):
    print(f"\n[Orchestrator] Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print("❌ Failed!")
        exit(1)
    print("✅ Success!")

def main():
    print("=======================================")
    print("   DATA PLATFORM PIPELINE (DEMO) 🚀   ")
    print("=======================================")
    
    # Step 1: Ingest (Simulated by existing data in GCS)
    print("\n1. Checking Data Lake (GCS)...")
    # In a real Airflow DAG, we would wait for a file sensor here.
    # For demo, we assume the Producer is running.
    time.sleep(1) 
    print("✅ Data Detected.")

    # Step 2: Transformation (dbt)
    print("\n2. Starting Transformation Layer (dbt run)...")
    if os.path.basename(os.getcwd()) != 'warehouse':
        os.chdir('warehouse') # Ensure we are in dbt dir
        
    run_command("dbt run")

    # Step 3: Verification
    print("\n3. Verifying Mart Data...")
    run_command("python count_rows.py")

    print("\n=======================================")
    print("   PIPELINE COMPLETE - DASHBOARD READY ")
    print("=======================================")

if __name__ == "__main__":
    main()
