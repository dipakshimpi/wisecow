#!/usr/bin/env python3
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import psutil

# Configuration (Thresholds)
CPU_THRESHOLD = 80.0       # in percent
MEMORY_THRESHOLD = 80.0    # in percent
DISK_THRESHOLD = 90.0      # in percent
PROCESS_THRESHOLD = 300    # number of processes

# Log configuration
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "health_monitor.log")

# Setup logging to both console and a rotating log file
logger = logging.getLogger("SystemHealthMonitor")
logger.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Rotating File Handler (max 5MB, keep 3 backup files)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

def check_system_health():
    try:
        # Get metrics
        cpu_usage = psutil.cpu_percent(interval=1.0)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        process_count = len(psutil.pids())

        logger.info(f"System Health Status: CPU: {cpu_usage}%, Memory: {memory_usage}%, Disk: {disk_usage}%, Processes: {process_count}")

        # Check thresholds
        alerts = []
        if cpu_usage > CPU_THRESHOLD:
            alerts.append(f"CRITICAL: CPU usage is at {cpu_usage}% (Threshold: {CPU_THRESHOLD}%)")
        
        if memory_usage > MEMORY_THRESHOLD:
            alerts.append(f"CRITICAL: Memory usage is at {memory_usage}% (Threshold: {MEMORY_THRESHOLD}%)")
            
        if disk_usage > DISK_THRESHOLD:
            alerts.append(f"CRITICAL: Disk usage is at {disk_usage}% (Threshold: {DISK_THRESHOLD}%)")
            
        if process_count > PROCESS_THRESHOLD:
            alerts.append(f"CRITICAL: Process count is at {process_count} (Threshold: {PROCESS_THRESHOLD})")

        # Log alerts if any
        if alerts:
            for alert in alerts:
                logger.warning(alert)
            return False
        
        return True

    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting System Health Check...")
    # Allow overriding thresholds via env vars for demonstration/testing
    CPU_THRESHOLD = float(os.getenv("CPU_THRESHOLD", CPU_THRESHOLD))
    MEMORY_THRESHOLD = float(os.getenv("MEMORY_THRESHOLD", MEMORY_THRESHOLD))
    DISK_THRESHOLD = float(os.getenv("DISK_THRESHOLD", DISK_THRESHOLD))
    PROCESS_THRESHOLD = int(os.getenv("PROCESS_THRESHOLD", PROCESS_THRESHOLD))

    check_system_health()
