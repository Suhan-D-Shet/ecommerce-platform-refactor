import logging
import os
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Create logger
logger = logging.getLogger("ecommerce")
logger.setLevel(logging.INFO)

# Create file handler with rotation
handler = RotatingFileHandler(
    os.path.join(log_dir, "app.log"),
    maxBytes=2000000,  # 2MB
    backupCount=3
)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(handler)
