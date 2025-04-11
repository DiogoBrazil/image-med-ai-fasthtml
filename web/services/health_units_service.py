# web/services/health_units_service.py
from services.api_client import ApiClient

class HealthUnitsService:
    @staticmethod
    async def get_health_units(token):
        """Obtém a lista de unidades de saúde"""
        client = ApiClient(token)
        
        try:
            result = await client.get("/health-units")
            if "detail" in result and "health_units" in result["detail"]:
                return {"success": True, "health_units": result["detail"]["health_units"]}
            return {"success": False, "message": "Failed to retrieve health units"}
        except ValueError as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    async def get_health_unit_by_id(token, unit_id):
        """Obtém uma unidade de saúde pelo ID"""
        client = ApiClient(token)
        
        try:
            result = await client.get(f"/health-units/{unit_id}")
            if "detail" in result and "health_unit" in result["detail"]:
                return {"success": True, "health_unit": result["detail"]["health_unit"]}
            return {"success": False, "message": "Health unit not found"}
        except ValueError as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    async def create_health_unit(token, unit_data):
        """Cria uma nova unidade de saúde"""
        client = ApiClient(token)
        
        try:
            result = await client.post("/health-units", unit_data)
            if "detail" in result and result["detail"].get("unit_id"):
                return {"success": True, "unit_id": result["detail"]["unit_id"]}
            return {"success": False, "message": "Failed to create health unit"}
        except ValueError as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    async def update_health_unit(token, unit_id, unit_data):
        """Atualiza uma unidade de saúde existente"""
        client = ApiClient(token)
        
        try:
            result = await client.put(f"/health-units/{unit_id}", unit_data)
            if "detail" in result and result["detail"].get("status_code") == 200:
                return {"success": True}
            return {"success": False, "message": "Failed to update health unit"}
        except ValueError as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    async def delete_health_unit(token, unit_id):
        """Exclui uma unidade de saúde"""
        client = ApiClient(token)
        
        try:
            result = await client.delete(f"/health-units/{unit_id}")
            if "detail" in result and result["detail"].get("status_code") == 200:
                return {"success": True}
            return {"success": False, "message": "Failed to delete health unit"}
        except ValueError as e:
            return {"success": False, "message": str(e)}