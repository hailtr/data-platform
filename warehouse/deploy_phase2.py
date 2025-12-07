
from dbt.cli.main import dbtRunner
import os

if os.path.basename(os.getcwd()) != 'warehouse':
    os.chdir('warehouse')

runner = dbtRunner()
print("1. Refreshing Source (Adding Context Column)...")
res1 = runner.invoke(['run-operation', 'stage_external_sources'])
if not res1.success:
    print("FAILED to refresh source.")
    exit(1)

print("2. Running Full Pipeline (V2 Logic)...")
res2 = runner.invoke(['run'])
if not res2.success:
    print("FAILED to run pipeline.")
    exit(1)

print("SUCCESS: Phase 2 Deployed.")
