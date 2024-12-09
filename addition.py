import time
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("Addition container started")

def perform_addition():
    result = 5 + 3
    with open('/app/addition_result.txt', 'w') as f:
        f.write(str(result))
    logger.info("Addition result written to /app/addition_result.txt")
    
    with open('/app/addition_checkpoint.txt', 'w') as f:
        f.write('addition_done')
    logger.info("Addition checkpoint written to /app/addition_checkpoint.txt")

def main():
    perform_addition()
    logger.info("Addition completed. Keeping container alive.")
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
