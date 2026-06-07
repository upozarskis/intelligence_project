import os
import time
from dotenv import load_dotenv

#  IMPORT PIPELINE COGS
# Because the 'pipeline' directory is at the root, Python allows clean package imports.
# We import the exact entry-point functions we built for each Medallion tier.
try:
    from pipeline.extract import run_extraction
except ImportError:
    # Safe fallback if your extract script uses a different function name
    from pipeline.extract import main as run_extraction

from pipeline.transform import transform_google_trends, transform_news_data
from pipeline.gold import create_gold_analytics

# Load environmental configs
load_dotenv()

def run_master_orchestrator():
    """Manages the end-to-end execution of the Medallion Data Pipeline"""
    print(" [Orchestrator] Initiating Automated Pipeline Execution...")
    start_total_time = time.time()

    # ──────────────────────────────────────────────────────────
    #  PHASE 1: BRONZE LAYER (RAW INGESTION)
    # ──────────────────────────────────────────────────────────
    print("\n======  PHASE 1: BRONZE LAYER (EXTRACTION) ======")
    start_bronze = time.time()
    try:
        run_extraction()
        print(f" Bronze Layer processing completed in {time.time() - start_bronze:.2f}s")
    except Exception as e:
        print(f" CRITICAL ERROR in Bronze Stage: {e}")
        print(" Pipeline aborted to prevent downstream corruption.")
        return

    # ──────────────────────────────────────────────────────────
    #  PHASE 2: SILVER LAYER (CLEANING & STANDARDIZATION)
    # ──────────────────────────────────────────────────────────
    print("\n======  PHASE 2: SILVER LAYER (TRANSFORMATION) ======")
    start_silver = time.time()
    try:
        transform_google_trends()
        print("---")
        transform_news_data()
        print(f" Silver Layer processing completed in {time.time() - start_silver:.2f}s")
    except Exception as e:
        print(f" CRITICAL ERROR in Silver Stage: {e}")
        print(" Pipeline aborted. Unable to parse clean data for Gold metrics.")
        return

    # ──────────────────────────────────────────────────────────
    #  PHASE 3: GOLD LAYER (BUSINESS INTELLIGENCE & KPIS)
    # ──────────────────────────────────────────────────────────
    print("\n======  PHASE 3: GOLD LAYER (AGGREGATION) ======")
    start_gold = time.time()
    try:
        create_gold_analytics()
        print(f" Gold Layer processing completed in {time.time() - start_gold:.2f}s")
    except Exception as e:
        print(f" CRITICAL ERROR in Gold Stage: {e}")
        return

    # ──────────────────────────────────────────────────────────
    #  PIPELINE SUCCESS REPORT
    # ──────────────────────────────────────────────────────────
    total_duration = time.time() - start_total_time
    print("\n=======================================================")
    print(f" SUCCESS: Full Medallion Pipeline executed in {total_duration:.2f}s!")
    print("=======================================================")

if __name__ == "__main__":
    run_master_orchestrator()