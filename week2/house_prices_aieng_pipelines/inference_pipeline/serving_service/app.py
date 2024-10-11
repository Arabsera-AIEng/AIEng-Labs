from fastapi import FastAPI
from endpoints import prediction, health, version, submit_actual  # Import the new endpoint
import logging

import warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="House Price Prediction API",
    description="API for predicting house prices and submitting actual prices.",
    version="1.0.0",
)

# Include the routers with prefixes
app.include_router(prediction.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(version.router, prefix="/api")
app.include_router(submit_actual.router, prefix="/api")  # Include the new endpoint
