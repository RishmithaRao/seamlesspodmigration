import os
import logging

logger = logging.getLogger(__name__)

def checkpoint_state(state, filename):
    try:
        with open(filename, 'w') as f:
            f.write(state)
        logger.info(f"State checkpointed to {filename}")
    except IOError as e:
        logger.error(f"Error writing checkpoint to {filename}: {e}")

def restore_state(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return f.read().strip()
        else:
            logger.warning(f"Checkpoint file {filename} not found")
            return None
    except IOError as e:
        logger.error(f"Error reading checkpoint from {filename}: {e}")
        return None
