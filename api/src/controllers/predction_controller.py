from fastapi import Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import base64
from ..utils.logger import get_logger
from ..usecases.prediction_usecases import PredictionUseCases
from ..utils.credentials_middleware import AuthMiddleware

logger = get_logger(__name__)

class PredictionController:
    def __init__(self):
        self.prediction_use_cases = PredictionUseCases()
        self.auth_middleware = AuthMiddleware()
    
    async def predict_respiratory(self, request: Request, file: UploadFile):
        """
        Controls the prediction flow for respiratory diseases.
        
        Args:
            request: FastAPI Request object
            file: Image file uploaded by the user
            
        Returns:
            dict: Prediction result
        """
        try:
            # Verifica a autenticação
            await self.auth_middleware.verify_request(request)
            
            # Verifica se o usuário é um profissional
            if request.state.user.get("profile") != "professional":
                logger.warning(f"User {request.state.user.get('user_id')} without professional privileges attempted to access prediction")
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": {
                            "message": "Only healthcare professionals can access predictions",
                            "status_code": 403
                        }
                    }
                )
            
            # Lê o conteúdo do arquivo
            image_data = await file.read()
            
            # Realiza a predição
            prediction_result = await self.prediction_use_cases.predict_respiratory(image_data)
            
            # Log de auditoria
            audit_data = {
                "user_id": request.state.user.get("user_id"),
                "action": "respiratory_prediction",
                "ip_address": request.client.host,
                "file_name": file.filename
            }
            logger.info(f"Respiratory prediction completed: {audit_data}")
            
            # Return the result
            return {
                "detail": {
                    "message": "Prediction successfully completed",
                    "model": "respiratory",
                    "prediction": prediction_result,
                    "status_code": 200
                }
            }
            
        except HTTPException as e:
            # Propaga exceções HTTP
            raise e
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error processing respiratory prediction: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": {
                        "message": "Internal error processing the prediction",
                        "status_code": 500
                    }
                }
            )
    
    async def detect_breast_cancer(self, request: Request, file: UploadFile):
        """
        Controls the detection flow for breast cancer using Faster R-CNN.
        
        Args:
            request: FastAPI Request object
            file: Image file uploaded by the user
            
        Returns:
            dict: Detection result with annotated image
        """
        try:
            # Verifica a autenticação
            await self.auth_middleware.verify_request(request)
            
            # Verifica se o usuário é um profissional
            if request.state.user.get("profile") != "professional":
                logger.warning(f"User {request.state.user.get('user_id')} without professional privileges attempted to access breast cancer detection")
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": {
                            "message": "Only healthcare professionals can access detections",
                            "status_code": 403
                        }
                    }
                )
            
            # Lê o conteúdo do arquivo
            image_data = await file.read()
            
            # Realiza a detecção
            detection_result = await self.prediction_use_cases.detect_breast_cancer(image_data)
            
            # Codifica a imagem em base64 para retorno
            image_base64 = base64.b64encode(detection_result["image_base64"]).decode('utf-8')
            
            # Log de auditoria
            audit_data = {
                "user_id": request.state.user.get("user_id"),
                "action": "breast_cancer_detection",
                "ip_address": request.client.host,
                "file_name": file.filename,
                "detections_count": len(detection_result["detections"])
            }
            logger.info(f"Breast cancer detection completed: {audit_data}")
            
            # Return the result
            return {
                "detail": {
                    "message": "Detection successfully completed",
                    "model": "breast",
                    "detections": detection_result["detections"],
                    "bounding_boxes": detection_result["bounding_boxes"],
                    "image_base64": image_base64,
                    "status_code": 200
                }
            }
            
        except HTTPException as e:
            # Propaga exceções HTTP
            raise e
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error processing breast cancer detection: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": {
                        "message": "Internal error processing the detection",
                        "status_code": 500
                    }
                }
            )
    
    async def predict_tuberculosis(self, request: Request, file: UploadFile):
        """
        Controls the prediction flow for tuberculosis.
        
        Args:
            request: FastAPI Request object
            file: Image file uploaded by the user
            
        Returns:
            dict: Prediction result
        """
        try:
            # Verifica a autenticação
            await self.auth_middleware.verify_request(request)
            
            # Verifica se o usuário é um profissional
            if request.state.user.get("profile") != "professional":
                logger.warning(f"User {request.state.user.get('user_id')} without professional privileges attempted to access tuberculosis prediction")
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": {
                            "message": "Only healthcare professionals can access predictions",
                            "status_code": 403
                        }
                    }
                )
            
            # Lê o conteúdo do arquivo
            image_data = await file.read()
            
            # Realiza a predição
            result = await self.prediction_use_cases.predict_tuberculosis(image_data)
            
            # Log de auditoria
            audit_data = {
                "user_id": request.state.user.get("user_id"),
                "action": "tuberculosis_prediction",
                "ip_address": request.client.host,
                "file_name": file.filename,
                "result": result["class_pred"]
            }
            logger.info(f"Tuberculosis prediction completed: {audit_data}")
            
            # Return the result
            return {
                "detail": {
                    "message": "Prediction successfully completed",
                    "model": "tuberculosis",
                    "prediction": result,
                    "status_code": 200
                }
            }
            
        except HTTPException as e:
            # Propaga exceções HTTP
            raise e
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error processing tuberculosis prediction: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": {
                        "message": "Internal error processing the prediction",
                        "status_code": 500
                    }
                }
            )
    

    async def prediction_osteoporosis(self, request: Request, file: UploadFile):
        """
        Controls the prediction flow for osteoporosis.
        
        Args:
            request: FastAPI Request object
            file: Image file uploaded by the user
            
        Returns:
            dict: Prediction result
        """
        try:
            # Verifica a autenticação
            await self.auth_middleware.verify_request(request)
            
            # Verifica se o usuário é um profissional
            if request.state.user.get("profile") != "professional":
                logger.warning(f"User {request.state.user.get('user_id')} without professional privileges attempted to access osteoporosis prediction")
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": {
                            "message": "Only healthcare professionals can access predictions",
                            "status_code": 403
                        }
                    }
                )
            
            # Lê o conteúdo do arquivo
            image_data = await file.read()
            
            # Realiza a predição
            result = await self.prediction_use_cases.predict_osteoporosis(image_data)
            
            # Log de auditoria
            audit_data = {
                "user_id": request.state.user.get("user_id"),
                "action": "osteoporosis_prediction",
                "ip_address": request.client.host,
                "file_name": file.filename,
                "result": result["class_pred"]
            }
            logger.info(f"Osteoporosis prediction completed: {audit_data}")
            
            # Return the result
            return {
                "detail": {
                    "message": "Prediction successfully completed",
                    "model": "osteoporosis",
                    "prediction": result,
                    "status_code": 200
                }
            }
            
        except HTTPException as e:
            # Propaga exceções HTTP
            raise e
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error processing osteoporosis prediction: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": {
                        "message": "Internal error processing the prediction",
                        "status_code": 500
                    }
                }
            )
    
    async def get_model_classes(self):
        """
        Retrieves the possible diagnostic classes for each model type.
        """
        # Não precisa de autenticação complexa aqui, é informação estática
        logger.info("Fetching available model classes")
        try:
            # Chama o método síncrono do use case
            classes = self.prediction_use_cases.get_available_classes()
            return {
                "detail": {
                    "message": "Model classes retrieved successfully",
                    "classes_by_model": classes,
                    "status_code": 200
                }
            }
        except Exception as e:
             logger.error(f"Error fetching model classes: {e}", exc_info=True)
             # Usar raise_http_error para consistência
             from ..utils.error_handler import raise_http_error
             raise_http_error(500, "Failed to retrieve model classes")