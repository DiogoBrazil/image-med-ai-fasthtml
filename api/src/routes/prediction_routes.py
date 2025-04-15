from fastapi import APIRouter, Request, UploadFile, File
from ..controllers.predction_controller import PredictionController

router = APIRouter(
    prefix="/api/predictions",
    tags=["predictions"],
    responses={404: {"description": "Not found"}},
)

prediction_controller = PredictionController()

@router.post("/respiratory", summary="Prediction of respiratory diseases")
async def predict_respiratory(request: Request, file: UploadFile = File(...)):
    """
    Performs prediction of respiratory diseases in an X-ray image.
    
    - **Requires professional profile**
    - Analyzes X-ray to detect respiratory conditions
    
    Returns the probabilities for each disease class.
    """
    return await prediction_controller.predict_respiratory(request, file)

@router.post("/breast-cancer", summary="Breast cancer detection")
async def detect_breast_cancer(request: Request, file: UploadFile = File(...)):
    """
    Detects possible areas with breast cancer in a mammography.
    
    - **Requires professional profile**
    - Uses Faster R-CNN model to detect masses
    - Returns annotated image with suspicious regions
    
    Returns the detections found and the annotated image in base64.
    """
    return await prediction_controller.detect_breast_cancer(request, file)

@router.post("/tuberculosis", summary="Tuberculosis prediction")
async def predict_tuberculosis(request: Request, file: UploadFile = File(...)):
    """
    Predicts the probability of tuberculosis in an X-ray image.
    
    - **Requires professional profile**
    - Classifies the image as positive or negative for tuberculosis
    
    Returns the predicted class and probabilities.
    """
    return await prediction_controller.predict_tuberculosis(request, file)


@router.post("/osteoporosis", summary="Osteoporosis prediction")
async def predict_osteoporosis(request: Request, file: UploadFile = File(...)):
    """
    Predicts the presence of osteoporosis in an X-ray image.
    
    - **Requires professional profile**
    - Classifies the image into one of three categories: Normal, Osteopenia or Osteoporosis
    
    Returns the predicted class and probabilities for each category.
    """
    return await prediction_controller.prediction_osteoporosis(request, file)


@router.get("/classes", summary="Get possible classes for each prediction model")
async def get_model_classes():
    """
    Returns a list of possible diagnostic results (classes) for each
    type of prediction model available (e.g., 'respiratory', 'tuberculosis').
    Useful for populating selection options in the UI.
    """
    return await prediction_controller.get_model_classes()