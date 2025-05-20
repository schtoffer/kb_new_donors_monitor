import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from app import app
    logger.info("Successfully imported app")
except Exception as e:
    logger.error(f"Error importing app: {e}")
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