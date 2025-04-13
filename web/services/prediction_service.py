# web/services/prediction_service.py
import httpx
from config import API_BASE_URL, API_KEY # Importa configurações
from typing import Dict, Any

class PredictionService:
    """Serviço para interagir com os endpoints de predição da API."""

    @staticmethod
    async def _make_prediction_request(token: str, endpoint: str, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Método auxiliar para enviar a imagem e obter a predição."""
        headers = {
            "api_key": API_KEY,
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        files = {'file': (filename, file_content, 'image/jpeg')} # Ajuste 'image/jpeg' se necessário

        full_url = f"{API_BASE_URL}{endpoint}"

        async with httpx.AsyncClient(timeout=60.0) as client: # Timeout maior
            try:
                # ---- CORREÇÃO APLICADA AQUI ----
                print(f"Enviando para API: POST {full_url}") # Log de depuração corrigido
                response = await client.post(full_url, headers=headers, files=files)
                response.raise_for_status() # Levanta exceção para erros HTTP (4xx, 5xx)

                api_response = response.json()
                if "detail" in api_response and api_response["detail"].get("status_code") == 200:
                     return {"success": True, "data": api_response["detail"]}
                else:
                     error_msg = api_response.get("detail", {}).get("message", "Prediction API request failed")
                     return {"success": False, "message": error_msg}

            except httpx.HTTPStatusError as e:
                error_detail = {"message": str(e)}
                try: error_detail = e.response.json().get("detail", error_detail)
                except: pass
                print(f"Erro HTTP API Predição: {e.response.status_code} - {error_detail}")
                # Retorna a mensagem de erro da API se possível
                return {"success": False, "message": error_detail.get("message", str(e))}
            except Exception as e:
                 # Aqui o erro 'e' seria o NameError antes da correção
                 # Agora deve capturar outros erros (ex: conexão, timeout)
                print(f"Erro Conexão/Outro API Predição: {type(e).__name__} - {e}") # Log mais detalhado
                return {"success": False, "message": f"Error connecting to prediction API: {e}"}

    # --- Métodos específicos (predict_respiratory, etc.) continuam iguais ---
    @staticmethod
    async def predict_respiratory(token: str, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Chama a API para predição de doenças respiratórias."""
        return await PredictionService._make_prediction_request(token, "/predictions/respiratory", file_content, filename)

    @staticmethod
    async def predict_breast_cancer(token: str, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Chama a API para predição de câncer de mama."""
        # Certifique-se que o endpoint na API é /api/predictions/breast-cancer
        return await PredictionService._make_prediction_request(token, "/predictions/breast-cancer", file_content, filename)

    @staticmethod
    async def predict_tuberculosis(token: str, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Chama a API para predição de tuberculose."""
        return await PredictionService._make_prediction_request(token, "/predictions/tuberculosis", file_content, filename)

    @staticmethod
    async def predict_osteoporosis(token: str, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Chama a API para predição de osteoporose."""
        return await PredictionService._make_prediction_request(token, "/predictions/osteoporosis", file_content, filename)