# web/pages/auth/logout.py
from fasthtml.common import RedirectResponse

async def logout_page(request):
    """Processa o logout do usuário"""
    session = request.scope.get("session", {})
    
    # Limpa a sessão
    if 'token' in session:
        del session['token']
    if 'user_id' in session:
        del session['user_id']
    if 'user_name' in session:
        del session['user_name']
    if 'user_profile' in session:
        del session['user_profile']
    
    # Redireciona para a página de login
    return RedirectResponse('/login', status_code=303)