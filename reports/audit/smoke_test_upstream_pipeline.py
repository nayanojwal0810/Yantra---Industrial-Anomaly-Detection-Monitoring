"""
Minimal technical smoke check for upstream execution:
Runs 1 seed of IsolationForest with default_parameters=True on CloggingDataset
to test CPU feasibility, dependency compatibility, and execution behavior.
"""
import sys
import time
import os
from pathlib import Path

temp_dir = Path(os.environ.get("TEMP", r"C:\Users\nayan\AppData\Local\Temp")) / "fluid-mixing-audit"
sys.path.append(str(temp_dir))
sys.path.append(str(temp_dir / "src"))

try:
    from src.AD_Benchmark.experiments import DirectClassificatorPerformance
    import Constants as const
    
    # Point CONST to temp directory
    const.PROJECT_PATH = temp_dir
    const.DATA_PATH = temp_dir / "data"
    const.RESULTS_PATH = temp_dir / "results"
    const.CONFIGS_PATH = temp_dir / "configs" / "AD_Benchmark"

    print("Attempting to run 1 seed of IsolationForest on CloggingDataset with default parameters...")
    t0 = time.time()
    exp = DirectClassificatorPerformance(dataset='CloggingDataset', model='IsolationForest', seed=42)
    results, model = exp.run_experiment(default_parameters=True)
    elapsed = time.time() - t0
    print(f"Smoke test successful! Elapsed time: {elapsed:.2f} seconds.")
    print("Results:", results)
except Exception as e:
    import traceback
    print("Smoke test failed with exception:")
    traceback.print_exc()
