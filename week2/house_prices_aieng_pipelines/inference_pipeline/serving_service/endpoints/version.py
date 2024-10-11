# endpoints/version.py

from fastapi import APIRouter
from inference_pipeline.serving_service.model.model import ModelLoader

router = APIRouter()

# Access the model card
model_loader = ModelLoader()
model_card = model_loader.model_card

@router.get("/version", response_model=dict)
async def get_version():
    """
    Get the model version and metadata.
    """
    return {
        "model_version": model_card.get("date_of_training", "unknown"),
        "algorithm": model_card.get("algorithm", "unknown"),
        "project_name": model_card.get("project_name", "unknown"),
        "rmse": model_card.get("rmse", "unknown")
    }
