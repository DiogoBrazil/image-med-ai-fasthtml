# web/services/users_service.py
from services.api_client import ApiClient

class UsersService:
    @staticmethod
    async def get_users(token, admin_id=None):
        """Obtém a lista de usuários"""
        client = ApiClient(token)
        params = {"admin_id": admin_id} if admin_id else None
        print("CHEGOU AQUI=====================================")
        try:
            result = await client.get("/users", params)
            if "detail" in result and "users" in result["detail"]:
                return {"success": True, "users": result["detail"]["users"]}
            return {"success": False, "message": "Failed to retrieve users"}
        except ValueError as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    async def get_user_by_id(token, user_id):
        """Obtém um usuário pelo ID"""
        client = ApiClient(token)
        
        try:
            result = await client.get(f"/users/{user_id}")
            if "detail" in result and "user" in result["detail"]:
                return {"success": True, "user": result["detail"]["user"]}
            return {"success": False, "message": "User not found"}
        except ValueError as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    async def create_user(token, user_data):
        """Cria um usuário novo"""
        client = ApiClient(token)
        
        try:
            result = await client.post("/users", user_data)
            if "detail" in result and result["detail"].get("user_id"):
                return {"success": True, "user_id": result["detail"]["user_id"]}
            return {"success": False, "message": "Failed to create user"}
        except ValueError as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    async def update_user(token, user_id, user_data):
        """Atualiza um usuário existente"""
        client = ApiClient(token)
        
        try:
            result = await client.put(f"/users/{user_id}", user_data)
            if "detail" in result and result["detail"].get("status_code") == 200:
                return {"success": True}
            return {"success": False, "message": "Failed to update user"}
        except ValueError as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    async def delete_user(token, user_id):
        """Exclui um usuário"""
        client = ApiClient(token)
        
        try:
            result = await client.delete(f"/users/{user_id}")
            if "detail" in result and result["detail"].get("status_code") == 200:
                return {"success": True}
            return {"success": False, "message": "Failed to delete user"}
        except ValueError as e:
            return {"success": False, "message": str(e)}