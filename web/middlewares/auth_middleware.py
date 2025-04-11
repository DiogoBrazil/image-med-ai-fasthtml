# # web/middlewares/auth_middleware.py
# from fasthtml.common import RedirectResponse

# class AuthMiddleware:
#     def __init__(self, app, secret_key, skip_paths=None):
#         self.app = app
#         self.secret_key = secret_key
#         self.skip_paths = skip_paths or ['/login', '/logout', '/static', '/favicon.ico']
    
#     async def __call__(self, scope, receive, send):
#         """ASGI middleware para verificar autenticação"""
#         if scope["type"] != "http":
#             return await self.app(scope, receive, send)
        
#         path = scope["path"]
        
#         # Ignora caminhos públicos
#         for skip_path in self.skip_paths:
#             if path.startswith(skip_path):
#                 return await self.app(scope, receive, send)
        
#         # Verifica se o usuário está autenticado
#         request = {"scope": scope}
#         session = request["scope"].get("session", {})
        
#         if not session.get('token'):
#             redirect = RedirectResponse('/login', status_code=303)
#             return await redirect(scope, receive, send)
        
#         # Continua para a aplicação
#         return await self.app(scope, receive, send)
# web/middlewares/auth_middleware.py
# web/middlewares/auth_middleware.py
from fasthtml.common import RedirectResponse

def auth_middleware(req, sess):
    """Função Beforeware para verificar autenticação"""
    # Verificamos se estamos em uma rota que deveria ser ignorada
    path = req.url.path
    skip_paths = ['/login', '/logout', '/static', '/favicon.ico', '/live-reload']
    
    for skip_path in skip_paths:
        if path.startswith(skip_path):
            return None  # Continue normalmente, sem redirecionar
    
    # Verifica se há um token na sessão
    if not sess.get('token'):
        # Se não houver token, redireciona para o login
        return RedirectResponse('/login', status_code=303)
    
    # Adicione informações do usuário ao request
    user_profile = sess.get('user_profile')
    user_id = sess.get('user_id')
    user_name = sess.get('user_name')
    
    # Opcional: adicionar informações do usuário ao escopo da requisição
    if not hasattr(req, 'state'):
        req.state = type('State', (), {})()
    
    req.state.user = {
        'profile': user_profile,
        'id': user_id,
        'name': user_name
    }
    
    # Retorna None para continuar o processamento normal
    return None