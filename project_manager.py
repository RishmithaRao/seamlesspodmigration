import os
import time
import logging
import signal
from kubernetes import client, config

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
        logger.warning("Checkpoint file not found. Starting from the beginning.")
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

def initiate_migration():
    logger.info("Initiating migration")
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    
    try:
        # Create a new mul-div pod
        new_pod = v1.create_namespaced_pod(
            namespace='default',
            body=client.V1Pod(
                metadata=client.V1ObjectMeta(
                    generate_name='mul-div-',
                    labels={'app': 'mul-div'}
                ),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name='mul-div',
                            image='rishmitha88/mul-div-container:latest',
                            volume_mounts=[
                                client.V1VolumeMount(
                                    name='shared-volume',
                                    mount_path='/app/shared'
                                )
                            ]
                        )
                    ],
                    volumes=[
                        client.V1Volume(
                            name='shared-volume',
                            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                claim_name='shared-pvc'
                            )
                        )
                    ]
                )
            )
        )

        # Wait for the new pod to be ready
        while True:
            pod = v1.read_namespaced_pod(new_pod.metadata.name, 'default')
            if pod.status.phase == 'Running':
                break
            time.sleep(1)

        # Set migration flag
        with open(MIGRATION_FLAG_FILE, 'w') as f:
            f.write('completed')

        logger.info(f"Migration completed. New pod: {new_pod.metadata.name}")
        return new_pod
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        return None

def is_pod_ready(pod):
    try:
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        pod_status = v1.read_namespaced_pod_status(pod.metadata.name, 'default')
        return pod_status.status.phase == 'Running'
    except Exception as e:
        logger.error(f"Error checking pod status: {e}")
        return False

def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        checkpoint = read_checkpoint()

        if checkpoint is None or checkpoint == 'multiplication_failed':
            logger.info("Waiting for multiplication to complete...")
            time.sleep(10)
        elif checkpoint == 'multiplication_done':
            logger.info("Multiplication completed. Initiating migration...")
            new_pod = initiate_migration()
            if new_pod:
                while not is_pod_ready(new_pod):
                    time.sleep(5)
                logger.info("New pod is ready. Division should start automatically.")
            else:
                logger.error("Failed to create new pod. Exiting.")
                break
        elif checkpoint == 'division_done':
            logger.info("All operations completed.")
            break
        else:
            logger.info(f"Unknown checkpoint state: {checkpoint}. Waiting...")
            time.sleep(10)

    logger.info("Project manager exiting.")

if __name__ == "__main__":
    main()
