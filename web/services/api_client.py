# web/services/api_client.py
import httpx
from config import API_BASE_URL, API_KEY

class ApiClient:
    def __init__(self, token=None):
        self.base_url = API_BASE_URL
        self.headers = {
            "api_key": API_KEY,
            "Content-Type": "application/json"
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    async def request(self, method, url, data=None, params=None):
        """Executa uma requisição para a API"""
        async with httpx.AsyncClient() as client:
            full_url = f"{self.base_url}{url}"
            
            try:
                response = await client.request(
                    method=method, 
                    url=full_url, 
                    json=data, 
                    params=params, 
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    # Token expirado ou inválido
                    raise ValueError("Session expired. Please login again.")
                
                error_detail = {"message": str(e)}
                try:
                    error_detail = e.response.json().get("detail", error_detail)
                except:
                    pass
                
                raise ValueError(error_detail.get("message", str(e)))
            except Exception as e:
                raise ValueError(f"Error connecting to API: {str(e)}")
    
    async def get(self, url, params=None):
        """Executa uma requisição GET"""
        return await self.request("GET", url, params=params)
    
    async def post(self, url, data):
        """Executa uma requisição POST"""
        return await self.request("POST", url, data=data)
    
    async def put(self, url, data):
        """Executa uma requisição PUT"""
        return await self.request("PUT", url, data=data)
    
    async def delete(self, url):
        """Executa uma requisição DELETE"""
        return await self.request("DELETE", url)