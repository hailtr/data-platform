
import os
from dbt.cli.main import dbtRunner

# Ensure we are in the warehouse directory where dbt_project.yml is
if os.path.basename(os.getcwd()) != 'warehouse':
    os.chdir('warehouse')

print("Running dbt debug...")
res = dbtRunner().invoke(['debug'])

if res.success:
    print("\nSUCCESS: Connected to BigQuery!")
else:
    print("\nFAILURE: Could not connect.")
    exit(1)
