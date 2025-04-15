from typing import Dict, List
import numpy as np
from PIL import Image, UnidentifiedImageError, ImageDraw, ImageFont
import os
import io
import cv2
import torch
import torch.nn.functional as F
import torchvision.transforms as T
from torchvision.transforms import ToTensor
from torchvision.ops import nms
from fastapi import HTTPException
from ..utils.logger import get_logger
from ..neural_network_weights.load_models import load_model_respiratory_diseases, load_model_breast_cancer, load_model_tuberculosis, load_model_osteoporosis
from ..utils.load_files import load_file_to_dictionary

logger = get_logger(__name__)

# Load models globally to avoid reloading them on each request
try:
    logger.info("Initializing AI models...")
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    logger.info(f"Using device: {device}")
    
    # Model for respiratory diagnosis
    model = load_model_respiratory_diseases()
    logger.info("Respiratory model loaded successfully")
    
    # Model for breast cancer with Faster R-CNN
    model_breast_cancer_faster_rcnn = load_model_breast_cancer(device)
    logger.info("Breast cancer model loaded successfully")
    
    # Model for tuberculosis
    model_tb = load_model_tuberculosis(device)
    logger.info("Tuberculosis model loaded successfully")

    # Model for osteoporosis
    model_osteoporosis = load_model_osteoporosis(device)
    logger.info("Osteoporosis model loaded successfully")
except Exception as e:
    logger.error(f"Error loading models: {str(e)}")
    raise

class PredictionUseCases:
    def __init__(self):
        pass  # Models are already loaded globally

    async def predict_respiratory(self, image_data: bytes):
        """
        Performs prediction of respiratory diseases in an image.
        
        Args:
            image_data: bytes of the image to be analyzed
            
        Returns:
            dict: Dictionary with probabilities for each class
        """
        try:
            logger.info("Starting image prediction for respiratory diagnosis")
            
            # Carrega a imagem a partir dos bytes
            image = Image.open(io.BytesIO(image_data))

            if not image:
                logger.error("Failed to process image - invalid image")
                raise HTTPException(
                    status_code=400, 
                    detail={
                        "message": "An error occurred while processing the image. Please check if the image is in the correct format and try again.",
                        "status_code": 400
                    }
                )
            
            # Realiza a predição usando o modelo
            prediction = model(image)

            if not prediction[0]:
                logger.error("Failed to process prediction - empty result")
                raise HTTPException(
                    status_code=400, 
                    detail={
                        "message": "An error occurred while processing the image. Please check if the image is in the correct format and try again.",
                        "status_code": 400
                    }
                )

            # Salva os resultados em um arquivo temporário
            prediction[0].save_txt('results.txt')

            # Carrega os resultados do arquivo para um dicionário
            result_dict = load_file_to_dictionary('results.txt')
            
            # Remove o arquivo temporário
            if os.path.exists('results.txt'):
                os.remove('results.txt')
                
            logger.info("Respiratory image prediction completed successfully")
            return result_dict

        except UnidentifiedImageError:
            logger.error("Error identifying image format")
            raise HTTPException(
                status_code=400, 
                detail={
                    "message": "An error occurred while processing the image. Please check if the image is in the correct format and try again.",
                    "status_code": 400
                }
            )
        
        except HTTPException as http_exc:
            raise http_exc
        
        except Exception as e:
            logger.error(f"Unexpected error during prediction: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail={
                    "message": "Internal server error during image processing.",
                    "status_code": 500
                }
            )

    async def detect_breast_cancer(self, image_data: bytes):
        """
        Detects breast cancer in a mammography using Faster R-CNN.
        
        Args:
            image_data: bytes of the image to be analyzed
            
        Returns:
            dict: Dictionary with detections and annotated image
        """
        try:
            logger.info("Starting breast cancer detection with Faster R-CNN")
            
            # Carrega a imagem a partir dos bytes
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            
            # Normaliza o tamanho da imagem
            max_dimension = 1024  # Dimensão máxima permitida
            width, height = image.size
            
            # Calcula a nova dimensão mantendo a proporção
            if width > max_dimension or height > max_dimension:
                if width > height:
                    new_width = max_dimension
                    new_height = int((height * max_dimension) / width)
                else:
                    new_height = max_dimension
                    new_width = int((width * max_dimension) / height)
                
                # Redimensiona a imagem mantendo a qualidade
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
            image_np = np.array(image)

            if image_np.size == 0:
                logger.error("Empty or unprocessable image")
                raise HTTPException(
                    status_code=400, 
                    detail={
                        "message": "The image is empty or cannot be processed.",
                        "status_code": 400
                    }
                )

            # Prepara a imagem para o modelo
            transform = ToTensor()
            img_tensor = transform(image).to(device)

            # Realiza a predição
            with torch.no_grad():
                prediction = model_breast_cancer_faster_rcnn([img_tensor])

            # Processa as predições
            boxes = prediction[0]['boxes']
            labels = prediction[0]['labels']
            scores = prediction[0]['scores']

            # Aplica limiar de confiança
            score_threshold = 0.7
            keep = scores >= score_threshold

            boxes = boxes[keep]
            labels = labels[keep]
            scores = scores[keep]

            # Aplica Non-Maximum Suppression para remover detecções sobrepostas
            nms_threshold = 0.7
            indices = nms(boxes, scores, nms_threshold)

            boxes = boxes[indices]
            labels = labels[indices]
            scores = scores[indices]

            # Converte para numpy para processamento posterior
            boxes = boxes.cpu().numpy()
            labels = labels.cpu().numpy()
            scores = scores.cpu().numpy()

            # Prepara lista para armazenar as detecções
            detections = []
            bounding_boxes = []
            
            if len(boxes) > 0:
                # Anota a imagem
                image_with_boxes = image.copy()
                draw = ImageDraw.Draw(image_with_boxes)

                labels_map = {1: 'Mass'}

                # Calcula dimensões mínimas garantidas para visualização
                image_width, image_height = image.size
                min_line_width = max(3, int(min(image_width, image_height) * 0.005))
                min_font_size = max(16, int(min(image_width, image_height) * 0.02))

                for box, label, score in zip(boxes, labels, scores):
                    xmin, ymin, xmax, ymax = box
                    xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)

                    # Calcula a largura e altura da caixa delimitadora
                    box_width = xmax - xmin
                    box_height = ymax - ymin

                    # Define espessura da linha proporcional à imagem, com mínimo garantido
                    line_width = max(min_line_width, int(min(box_width, box_height) * 0.02))

                    # Define tamanho da fonte proporcional à imagem, com mínimo garantido
                    font_size = max(min_font_size, int(min(box_width, box_height) * 0.1))

                    try:
                        font = ImageFont.truetype("arial.ttf", size=font_size)
                    except IOError:
                        # Se arial.ttf não estiver disponível, tenta DejaVuSans
                        try:
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size=font_size)
                        except IOError:
                            font = ImageFont.load_default()

                    # Desenha a caixa delimitadora com borda dupla para maior destaque
                    # Borda externa preta
                    draw.rectangle([(xmin-line_width, ymin-line_width), 
                                  (xmax+line_width, ymax+line_width)], 
                                  outline='black', width=line_width+2)
                    # Borda interna colorida
                    draw.rectangle([(xmin, ymin), (xmax, ymax)], 
                                 outline='red', width=line_width)

                    # Obtém o nome da classe
                    class_name = labels_map.get(label, 'desconhecido')

                    # Cria o texto com a pontuação
                    text = f"{score:.2f}"

                    # Calcula a posição e o tamanho do texto
                    text_size = draw.textbbox((0, 0), text, font=font)
                    text_width = text_size[2] - text_size[0]
                    text_height = text_size[3] - text_size[1]

                    # Adiciona padding ao texto para melhor legibilidade
                    padding = max(4, int(text_height * 0.2))

                    # Coordenadas para o fundo do texto
                    text_xmin = xmin
                    text_ymin = max(0, ymin - text_height - padding * 2)  # Garante que não saia da imagem
                    text_xmax = xmin + text_width + padding * 2
                    text_ymax = text_ymin + text_height + padding * 2

                    # Se o texto ficaria fora da imagem no topo, coloca abaixo da caixa
                    if text_ymin < 0:
                        text_ymin = min(ymax, image_height - text_height - padding * 2)
                        text_ymax = text_ymin + text_height + padding * 2

                    # Desenha um contorno preto ao redor do fundo do texto
                    draw.rectangle([(text_xmin-2, text_ymin-2), (text_xmax+2, text_ymax+2)], 
                                 fill='yellow')
                    # Desenha o retângulo de fundo para o texto
                    draw.rectangle([(text_xmin, text_ymin), (text_xmax, text_ymax)], 
                                 fill='red')

                    # Escreve o texto com contorno preto para maior contraste
                    for offset in [(1,1), (-1,-1), (1,-1), (-1,1)]:
                        draw.text((text_xmin + padding + offset[0], text_ymin + padding + offset[1]),
                                text, fill='black', font=font)
                    # Texto principal em branco
                    draw.text((text_xmin + padding, text_ymin + padding),
                             text, fill='white', font=font)

                    # Adiciona a detecção à lista
                    detections.append({
                        "class_id": int(label),
                        "confidence": float(score),
                        "bbox": [xmin, ymin, xmax, ymax]
                    })
                    
                    # Adiciona a bounding box para o formato esperado pela API
                    bounding_boxes.append({
                        "x": xmin,
                        "y": ymin,
                        "width": box_width,
                        "height": box_height,
                        "confidence": float(score),
                        "observations": f"Mass detected with {score:.2f} confidence"
                    })

                # Converte a imagem anotada para formato OpenCV
                annotated_image = np.array(image_with_boxes)
                annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
            else:
                annotated_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

            # Codifica a imagem em bytes
            success, img_encoded = cv2.imencode('.jpg', annotated_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
            if not success:
                logger.error("Failed to encode the annotated image")
                raise HTTPException(
                    status_code=500, 
                    detail={
                        "message": "Failed to encode the image.",
                        "status_code": 500
                    }
                )
            img_bytes = img_encoded.tobytes()

            logger.info(f"Breast cancer detection completed successfully. {len(detections)} detections found.")
            return {
                "image_base64": img_bytes,
                "detections": detections,
                "bounding_boxes": bounding_boxes
            }

        except UnidentifiedImageError:
            logger.error("Error identifying image format for breast cancer detection")
            raise HTTPException(
                status_code=400, 
                detail={
                    "message": "Error processing the image. Please check if the format is correct and try again.",
                    "status_code": 400
                }
            )
            
        except HTTPException as http_exc:
            raise http_exc
            
        except Exception as exc:
            logger.error(f"Unexpected error during breast cancer detection: {str(exc)}")
            raise HTTPException(
                status_code=500, 
                detail={
                    "message": "An error occurred while processing the image. Please try again later.",
                    "status_code": 500
                }
            )

    async def predict_tuberculosis(self, image_data: bytes):
        """
        Predicts if an image contains signs of tuberculosis.
        
        Args:
            image_data: bytes of the image to be analyzed
            
        Returns:
            dict: Dictionary with the predicted class and probabilities
        """
        try:
            logger.info("Starting tuberculosis prediction")
            
            # Carrega a imagem a partir dos bytes
            image = Image.open(io.BytesIO(image_data)).convert("RGB")

            # Define as transformações para pre-processamento
            transform = T.Compose([
                T.Resize((224,224)),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406],
                            std=[0.229, 0.224, 0.225])
            ])

            # Prepara a imagem para o modelo
            img_tensor = transform(image).unsqueeze(0).to(device)

            # Roda o modelo
            with torch.no_grad():
                logits = model_tb(img_tensor)
                probs = F.softmax(logits, dim=1)
                _, pred_idx = torch.max(logits, dim=1)

            # Mapeia o índice da classe para o nome da classe
            classes = ["negative", "positive"]
            pred_class = classes[pred_idx.item()]

            # Extrai as probabilidades
            prob_negative = probs[0,0].item() * 100
            prob_positive = probs[0,1].item() * 100

            logger.info(f"Tuberculosis prediction completed: {pred_class} ({prob_positive:.2f}% positive)")
            
            result = {
                "class_pred": pred_class,
                "probabilities": {
                    "negative": round(prob_negative, 2),
                    "positive": round(prob_positive, 2) 
                }
            }
            return result

        except UnidentifiedImageError:
            logger.error("Error identifying image format for tuberculosis detection")
            raise HTTPException(
                status_code=400, 
                detail={
                    "message": "Invalid or corrupted image.",
                    "status_code": 400
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error during tuberculosis prediction: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail={
                    "message": f"Internal error: {str(e)}",
                    "status_code": 500
                }
            )
    

    async def predict_osteoporosis(self, image_data: bytes):
        """
        Predicts if an image contains signs of osteoporosis and classifies it as Normal, Osteopenia or Osteoporosis.
        
        Args:
            image_data: bytes of the image to be analyzed
            
        Returns:
            dict: Dictionary with the predicted class and probabilities
        """
        try:
            logger.info("Starting osteoporosis prediction")
            
            # Carrega a imagem a partir dos bytes
            image = Image.open(io.BytesIO(image_data)).convert("RGB")

            # Define as transformações para pre-processamento
            transform = T.Compose([
                T.Resize((224,224)),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406],
                            std=[0.229, 0.224, 0.225])
            ])

            # Prepara a imagem para o modelo
            img_tensor = transform(image).unsqueeze(0).to(device)

            # Roda o modelo
            with torch.no_grad():
                logits = model_osteoporosis(img_tensor)
                probs = F.softmax(logits, dim=1)
                _, pred_idx = torch.max(logits, dim=1)

            # Mapeia o índice da classe para o nome da classe
            classes = ["Normal", "Osteopenia", "Osteoporosis"]
            pred_class = classes[pred_idx.item()]

            # Extrai as probabilidades para cada classe
            prob_normal = probs[0,0].item() * 100
            prob_osteopenia = probs[0,1].item() * 100
            prob_osteoporosis = probs[0,2].item() * 100

            logger.info(f"Osteoporosis prediction completed: {pred_class} (Normal: {prob_normal:.2f}%, Osteopenia: {prob_osteopenia:.2f}%, Osteoporosis: {prob_osteoporosis:.2f}%)")
            
            result = {
                "class_pred": pred_class,
                "probabilities": {
                    "Normal": round(prob_normal, 2),
                    "Osteopenia": round(prob_osteopenia, 2),
                    "Osteoporosis": round(prob_osteoporosis, 2)
                }
            }
            return result

        except UnidentifiedImageError:
            logger.error("Error identifying image format for osteoporosis detection")
            raise HTTPException(
                status_code=400, 
                detail={
                    "message": "Invalid or corrupted image.",
                    "status_code": 400
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error during osteoporosis prediction: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail={
                    "message": f"Internal error: {str(e)}",
                    "status_code": 500
                }
            )
    

    def get_available_classes(self) -> Dict[str, List[str]]:
        # Nota: Para 'respiratory', precisaríamos saber as classes exatas do YOLO.
        # Se forem fixas, podemos adicionar aqui. Se dinâmicas, seria mais complexo.
        # Assumindo que as classes do YOLO sejam, por exemplo, 'Pneumonia', 'Normal', 'COVID-19'
        respiratory_classes_example = ["Pneumonia Viral", "Normal", "Covid-19", "Pneumonia Bacteriana"] 
        tuberculosis_classes_example = ["negative", "positive"]
        osteoporosis_classes_example = ["Normal", "Osteopenia", "Osteoporosis"]
        breast_classes_example = ["nódulo encontrado", "nódulo não encontrado"]

        return {
            "respiratory": respiratory_classes_example,
            "tuberculosis": tuberculosis_classes_example,
            "osteoporosis": osteoporosis_classes_example,
            "breast": breast_classes_example
        }