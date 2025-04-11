# web/services/attendance_service.py
from services.api_client import ApiClient

class AttendanceService:
    @staticmethod
    async def create_attendance(token, attendance_data):
        """Cria um novo atendimento médico"""
        client = ApiClient(token)
        
        try:
            result = await client.post("/attendances", attendance_data)
            if "detail" in result and result["detail"].get("status_code") in [200, 201]:
                return {
                    "success": True,
                    "attendance_id": result["detail"].get("attendance_id")
                }
            return {"success": False, "message": "Failed to create attendance record"}
        except ValueError as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    async def get_attendances(token, health_unit_id=None, model_used=None, page=1, per_page=10):
        """Obtém a lista de atendimentos médicos"""
        client = ApiClient(token)
        
        params = {
            "page": page,
            "per_page": per_page
        }
        
        if health_unit_id:
            params["health_unit_id"] = health_unit_id
        
        if model_used:
            params["model_used"] = model_used
        
        try:
            result = await client.get("/attendances", params)
            if "detail" in result and "attendances" in result["detail"]:
                return {
                    "success": True,
                    "attendances": result["detail"]["attendances"],
                    "pagination": result["detail"].get("pagination", {})
                }
            return {"success": False, "message": "Failed to retrieve attendances"}
        except ValueError as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    async def get_attendance_by_id(token, attendance_id, include_image=False):
        """Obtém um atendimento médico pelo ID"""
        client = ApiClient(token)
        
        params = {"include_image": include_image}
        
        try:
            result = await client.get(f"/attendances/{attendance_id}", params)
            if "detail" in result and "attendance" in result["detail"]:
                return {"success": True, "attendance": result["detail"]["attendance"]}
            return {"success": False, "message": "Attendance not found"}
        except ValueError as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    async def update_attendance(token, attendance_id, attendance_data):
        """Atualiza um atendimento médico existente"""
        client = ApiClient(token)
        
        try:
            result = await client.put(f"/attendances/{attendance_id}", attendance_data)
            if "detail" in result and result["detail"].get("status_code") == 200:
                return {"success": True}
            return {"success": False, "message": "Failed to update attendance"}
        except ValueError as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    async def delete_attendance(token, attendance_id):
        """Exclui um atendimento médico"""
        client = ApiClient(token)
        
        try:
            result = await client.delete(f"/attendances/{attendance_id}")
            if "detail" in result and result["detail"].get("status_code") == 200:
                return {"success": True}
            return {"success": False, "message": "Failed to delete attendance"}
        except ValueError as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    async def get_statistics(token, start_date, end_date):
        """Obtém estatísticas dos atendimentos"""
        client = ApiClient(token)
        
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        
        try:
            result = await client.get("/attendances/statistics/summary", params)
            if "detail" in result and "statistics" in result["detail"]:
                return {"success": True, "statistics": result["detail"]["statistics"]}
            return {"success": False, "message": "Failed to retrieve statistics"}
        except ValueError as e:
            return {"success": False, "message": str(e)}