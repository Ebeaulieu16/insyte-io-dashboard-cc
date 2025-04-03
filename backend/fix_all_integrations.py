"""
Master script to fix all integration-related issues.
This script orchestrates the execution of all the fix scripts.
"""

import os
import sys
import logging
import time
import subprocess

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_script(script_name, description):
    """Run a Python script and log the result."""
    logger.info(f"Running {description}...")
    try:
        result = subprocess.run(
            ["python", script_name],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Successfully completed {description}")
        logger.info(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running {description}: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def main():
    """Execute all fix scripts in order."""
    logger.info("Starting integration data fix process")
    
    # Step 1: Fix integrations with missing user_id
    if run_script("fix_integrations_user_id.py", "user ID fix script"):
        logger.info("Successfully fixed integrations with missing user_id")
    else:
        logger.error("Failed to fix integrations with missing user_id")
        return
    
    # Give the database a moment to process changes
    time.sleep(1)
    
    # Step 2: Clean up demo data for users with real integrations
    if run_script("clean_demo_data.py", "demo data cleanup script"):
        logger.info("Successfully cleaned up demo data")
    else:
        logger.error("Failed to clean up demo data")
        return
    
    # Step 3: Show current integrations summary
    if run_script("show_integrations.py", "integrations summary script"):
        logger.info("Successfully displayed integrations summary")
    else:
        logger.error("Failed to display integrations summary")
    
    logger.info("Integration data fix process completed")

if __name__ == "__main__":
    main() 