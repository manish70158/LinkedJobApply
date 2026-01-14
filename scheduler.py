"""
Scheduler for running the LinkedIn Auto Job Applier on a schedule
Useful for Azure Container Instances continuous deployment
"""

import schedule
import time
import subprocess
import logging
from datetime import datetime
import os

# Setup logging
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/scheduler.log'),
        logging.StreamHandler()
    ]
)

def run_job_applier():
    """Execute the LinkedIn Auto Job Applier"""
    try:
        logging.info("="*60)
        logging.info("Starting LinkedIn Auto Job Applier scheduled run")
        logging.info("="*60)
        
        start_time = datetime.now()
        
        # Run the bot
        result = subprocess.run(
            ['python', 'runAiBot.py'],
            capture_output=True,
            text=True,
            timeout=7200  # 2 hour timeout
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logging.info(f"Bot completed in {duration:.2f} seconds")
        
        if result.returncode == 0:
            logging.info("✓ Bot completed successfully")
            logging.info(f"Output preview: {result.stdout[:500]}")
        else:
            logging.error(f"✗ Bot failed with exit code {result.returncode}")
            logging.error(f"Error output: {result.stderr}")
        
        # Upload results to Azure if configured
        if os.getenv('AZURE_STORAGE_CONNECTION_STRING'):
            logging.info("Uploading results to Azure Storage...")
            try:
                subprocess.run(
                    ['python', 'upload_logs_to_azure.py'],
                    timeout=300
                )
                logging.info("✓ Results uploaded successfully")
            except Exception as e:
                logging.error(f"✗ Failed to upload results: {e}")
        
        logging.info("="*60)
        
    except subprocess.TimeoutExpired:
        logging.error("Bot execution timed out after 2 hours")
    except Exception as e:
        logging.error(f"Scheduler error: {e}", exc_info=True)

def main():
    """Main scheduler function"""
    logging.info("LinkedIn Auto Job Applier Scheduler Started")
    logging.info(f"Current time: {datetime.now()}")
    
    # Get schedule configuration from environment
    schedule_hours = int(os.getenv('SCHEDULE_HOURS', '6'))
    run_immediately = os.getenv('RUN_IMMEDIATELY', 'true').lower() == 'true'
    
    logging.info(f"Configured to run every {schedule_hours} hours")
    
    # Schedule the job
    schedule.every(schedule_hours).hours.do(run_job_applier)
    
    # Run immediately on startup if configured
    if run_immediately:
        logging.info("Running job immediately on startup...")
        run_job_applier()
    
    logging.info(f"Next scheduled run: {schedule.next_run()}")
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
