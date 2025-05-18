# Gunicorn configuration file for Azure App Service deployment
import multiprocessing

# Bind to 0.0.0.0:8000
bind = "0.0.0.0:8000"

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = "sync"

# Timeout in seconds
timeout = 600

# Log level
loglevel = "info"

# Access log format
accesslog = "-"

# Error log
errorlog = "-"

# Application module
app_module = "app:app"
