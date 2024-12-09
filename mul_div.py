import os
import time
import logging
import signal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SHARED_VOLUME_PATH = '/app/shared'  # This should match the mount path in your deployment
CHECKPOINT_FILE = os.path.join(SHARED_VOLUME_PATH, 'checkpoint.txt')
MUL_RESULT_FILE = os.path.join(SHARED_VOLUME_PATH, 'mul_result.txt')
DIV_RESULT_FILE = os.path.join(SHARED_VOLUME_PATH, 'div_result.txt')
MIGRATION_FLAG_FILE = os.path.join(SHARED_VOLUME_PATH, 'migration_flag.txt')

def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}. Exiting gracefully.")
    exit(0)

def read_checkpoint():
    try:
        with open(CHECKPOINT_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.info("Checkpoint file not found. Checking for multiplication result file.")
        if os.path.exists(MUL_RESULT_FILE):
            logger.info("Multiplication result file found. Assuming multiplication is done.")
            return 'multiplication_done'
        else:
            logger.info("No multiplication result file. Starting from the beginning.")
            return None
    except IOError as e:
        logger.error(f"Error reading checkpoint file: {e}")
        return None

def write_checkpoint(state):
    try:
        os.makedirs(SHARED_VOLUME_PATH, exist_ok=True)
        with open(CHECKPOINT_FILE, 'w') as f:
            f.write(state)
        logger.info(f"Checkpoint written: {state}")
    except IOError as e:
        logger.error(f"Error writing checkpoint file: {e}")

def write_result(file_path, result):
    try:
        os.makedirs(SHARED_VOLUME_PATH, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(str(result))
        logger.info(f"Result written to {file_path}")
    except IOError as e:
        logger.error(f"Error writing result to {file_path}: {e}")

def perform_multiplication():
    logger.info("Starting multiplication")
    try:
        result = 4 * 6
        write_result(MUL_RESULT_FILE, result)
        logger.info("Multiplication completed")
        write_checkpoint('multiplication_done')
    except Exception as e:
        logger.error(f"Error during multiplication: {e}")
        write_checkpoint('multiplication_failed')

def perform_division():
    logger.info("Starting division")
    try:
        with open(MUL_RESULT_FILE, 'r') as f:
            mul_result = int(f.read().strip())
        result = mul_result / 2
        write_result(DIV_RESULT_FILE, result)
        logger.info("Division completed")
        write_checkpoint('division_done')
    except Exception as e:
        logger.error(f"Error during division: {e}")
        write_checkpoint('division_failed')

def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        checkpoint = read_checkpoint()

        if checkpoint is None or checkpoint == 'multiplication_failed':
            perform_multiplication()
        elif checkpoint == 'multiplication_done':
            logger.info("Multiplication already completed. Proceeding with division.")
            perform_division()
        elif checkpoint == 'division_done':
            logger.info("All operations already completed.")
        else:
            logger.info(f"Unknown checkpoint state: {checkpoint}. Starting from multiplication.")
            perform_multiplication()

        time.sleep(10)

if __name__ == "__main__":
    main()
