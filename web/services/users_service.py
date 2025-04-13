# web/services/users_service.py
from services.api_client import ApiClient

class UsersService:
    @staticmethod
    async def get_users(token, admin_id=None):
        """Obtém a lista de usuários"""
        client = ApiClient(token)
        params = {"admin_id": admin_id} if admin_id else None
        try:
            result = await client.get("/users/list/", params)
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
    async def get_professionals_by_admin(token, admin_id=None):
        """Obtém a lista de profissionais associados a um admin."""
        client = ApiClient(token)
        params = {}
        # A API parece pegar o admin_id do token se não for passado,
        # mas podemos passar explicitamente se necessário.
        # if admin_id:
        #    params['admin_id'] = admin_id

        try:
            # Chama o endpoint GET /api/users/professionals/list/
            # Certifique-se que o path está correto (com ou sem barra final)
            result = await client.get("/users/professionals/list/", params=params)

            # A API pode retornar a lista na chave 'professionals' ou 'users'
            professionals_list = None
            if "detail" in result:
                if "professionals" in result["detail"]:
                    professionals_list = result["detail"]["professionals"]
                elif "users" in result["detail"]: # Fallback se usar a mesma chave
                    professionals_list = [u for u in result["detail"]["users"] if u.get("profile") == "professional"]

            if professionals_list is not None:
                return {"success": True, "professionals": professionals_list}
            else:
                error_msg = result.get("detail", {}).get("message", "Failed to retrieve professionals")
                return {"success": False, "message": error_msg}
        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            print(f"Erro inesperado ao buscar profissionais: {e}")
            return {"success": False, "message": f"Unexpected error fetching professionals: {e}"}

    
    @staticmethod
    async def create_user(token, user_data):
        """Cria um usuário novo"""
        client = ApiClient(token)
        
        try:
            result = await client.post("/users/add/", user_data)
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
        """Exclui um usuário chamando a API."""
        client = ApiClient(token)
        try:
            # Chama o endpoint DELETE da API /api/users/{user_id}
            result = await client.delete(f"/users/{user_id}")
            if "detail" in result and result["detail"].get("status_code") == 200:
                return {"success": True, "message": result["detail"].get("message", "User deleted successfully")}
            else:
                error_msg = result.get("detail", {}).get("message", "Failed to delete user")
                return {"success": False, "message": error_msg}
        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            print(f"Erro inesperado ao deletar usuário: {e}")
            return {"success": False, "message": f"Unexpected error deleting user: {e}"}
    

    @staticmethod
    async def get_administrators(token):
        """Obtém a lista de usuários com perfil 'administrator'"""
        client = ApiClient(token)
        try:
            # Certifique-se de que o caminho aqui corresponde EXATAMENTE ao da sua API
            # (com a barra no final, como você mostrou)
            result = await client.get("/users/administrators/list/")
            if "detail" in result and "administrators" in result["detail"]:
                return {"success": True, "administrators": result["detail"]["administrators"]}
            # Fallback (menos provável, baseado na sua confirmação da API)
            elif "detail" in result and "users" in result["detail"]:
                 admins = [u for u in result["detail"]["users"] if u.get("profile") == "administrator"]
                 return {"success": True, "administrators": admins}
            # Captura mensagens de erro da API se não houver 'administrators'
            error_msg = result.get("detail", {}).get("message", "Failed to retrieve administrators")
            return {"success": False, "message": error_msg}
        except ValueError as e:
            # Erros de validação ou conexão do ApiClient
            return {"success": False, "message": str(e)}
        except Exception as e:
            # Erros inesperados
            print(f"Erro inesperado ao buscar administradores: {e}") # Log para depuração
            return {"success": False, "message": f"Unexpected error fetching administrators: {e}"}