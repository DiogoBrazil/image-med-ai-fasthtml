# web/services/auth_service.py
from services.api_client import ApiClient

class AuthService:
    @staticmethod
    async def login(email, password):
        """Faz login e retorna o token"""
        client = ApiClient()
        data = {"email": email, "password": password}
        
        try:
            result = await client.post("/users/login", data)
            if "detail" in result and result["detail"].get("token"):
                return {
                    "success": True,
                    "token": result["detail"]["token"],
                    "user": {
                        "id": result["detail"]["user_id"],
                        "name": result["detail"]["user_name"],
                        "profile": result["detail"]["profile"]
                    }
                }
            return {"success": False, "message": "Invalid response from server"}
        except ValueError as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def is_admin(profile):
        """Verifica se o perfil é de administrador"""
        return profile in ["administrator", "general_administrator"]
    
    @staticmethod
    def is_professional(profile):
        """Verifica se o perfil é de profissional"""
        return profile == "professional"