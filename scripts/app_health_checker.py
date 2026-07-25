#!/usr/bin/env python3
import sys
import time
import argparse
import logging
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AppHealthChecker")

def check_app_health(url, timeout=5):
    try:
        start_time = time.time()
        # Wisecow lacks standard HTTP headers (like Content-Length), but requests handles the raw socket close.
        # We specify a timeout to ensure it doesn't hang if netcat stays open,
        # and we pass Connection: close to ensure clean teardown of the TCP stream.
        headers = {'Connection': 'close'}
        response = requests.get(url, headers=headers, timeout=timeout)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            logger.info(f"SUCCESS: Service {url} is UP. Status Code: {response.status_code}. Response Time: {duration:.2f}s")
            return True, response.status_code
        else:
            logger.warning(f"FAILURE: Service {url} is DOWN. Status Code: {response.status_code}. Response Time: {duration:.2f}s")
            return False, response.status_code
            
    except requests.exceptions.Timeout:
        logger.error(f"FAILURE: Service {url} is DOWN. Reason: Connection Timeout after {timeout}s.")
        return False, "Timeout"
    except requests.exceptions.ConnectionError as e:
        logger.error(f"FAILURE: Service {url} is DOWN. Reason: Connection Refused/Failed. Details: {e}")
        return False, "ConnectionError"
    except requests.exceptions.RequestException as e:
        logger.error(f"FAILURE: Service {url} is DOWN. Reason: Request Exception. Details: {e}")
        return False, "Exception"

def main():
    parser = argparse.ArgumentParser(description="Wisecow Application Health Checker")
    parser.add_argument("--url", default="http://localhost:4499", help="URL of the service to check")
    parser.add_argument("--interval", type=int, default=10, help="Interval between checks in seconds")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    logger.info(f"Starting Wisecow Health Checker targeting: {args.url} (Interval: {args.interval}s)")

    if args.once:
        is_up, _ = check_app_health(args.url)
        sys.exit(0 if is_up else 1)

    try:
        while True:
            check_app_health(args.url)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logger.info("Health checker stopped by user.")

if __name__ == "__main__":
    main()
