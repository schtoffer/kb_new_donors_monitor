import os
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Log system information
logger.info(f'WSGI startup - Python version: {sys.version}')
logger.info(f'WSGI startup - Platform: {sys.platform}')
logger.info(f'WSGI startup - Current working directory: {os.getcwd()}')
logger.info(f'WSGI startup - Environment variables: {[k for k in os.environ.keys()]}')
logger.info(f'WSGI startup - Python path: {sys.path}')

# Check if we're running in Azure
is_azure = 'WEBSITE_SITE_NAME' in os.environ
logger.info(f'Running in Azure: {is_azure}')

# Check for critical directories
instance_path = os.path.join(os.getcwd(), 'instance')
logger.info(f'Instance path: {instance_path}')
if os.path.exists(instance_path):
    logger.info(f'Instance directory exists')
    if os.access(instance_path, os.W_OK):
        logger.info(f'Instance directory is writable')
    else:
        logger.error(f'Instance directory is not writable')
else:
    logger.info(f'Instance directory does not exist')
    try:
        os.makedirs(instance_path, exist_ok=True)
        logger.info(f'Created instance directory')
    except Exception as e:
        logger.error(f'Failed to create instance directory: {e}')

try:
    logger.info("Attempting to import app...")
    from app import app
    logger.info("Successfully imported app")
except Exception as e:
    logger.error(f"Error importing app: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    # Print the Python path to help with debugging
    logger.error(f"Python path: {sys.path}")
    raise

# For Azure App Service
application = app

if __name__ == "__main__":
    try:
        # Get port from environment variable or use default 8000
        port = int(os.environ.get('PORT', 8000))
        logger.info(f"Starting application on port {port}")
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        raise