# web/pages/auth/login.py
from fasthtml.common import *
from components.forms import LoginForm
from services.auth_service import AuthService

async def login_page(request):
    """Renderiza a página de login"""
    error_message = None
    
    # Se o usuário já está logado, redireciona para a home
    session = request.scope.get("session", {})
    if session.get('token'):
        return RedirectResponse('/', status_code=303)
    
    # Processa o login no POST
    if request.method == "POST":
        form_data = await request.form()
        email = form_data.get('email')
        password = form_data.get('password')
        
        if not email or not password:
            error_message = "Email and password are required"
        else:
            result = await AuthService.login(email, password)
            
            if result["success"]:
                # Guarda os dados na sessão
                session = request.scope.get("session", {})
                session['token'] = result['token']
                session['user_id'] = result['user']['id']
                session['user_name'] = result['user']['name']
                session['user_profile'] = result['user']['profile']
                print(f"Session========================: {session}")
                # Redireciona para a página inicial após login bem-sucedido
                return RedirectResponse('/', status_code=303)
            else:
                error_message = result.get("message", "Login failed. Please try again.")
    
    # Renderiza o formulário de login
    return Div(
        Div(
            Div(
                H1("Medical Diagnosis System", cls="auth-title"),
                H2("Login", cls="auth-subtitle"),
                LoginForm(error=error_message),
                cls="auth-card"
            ),
            cls="auth-container"
        ),
        Style("""
            body {
                background-color: #f3f4f6;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .auth-container {
                width: 100%;
                max-width: 420px;
                padding: 1rem;
            }
            .auth-card {
                background-color: white;
                border-radius: 0.5rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                padding: 2rem;
            }
            .auth-title {
                color: #2563eb;
                text-align: center;
                margin-bottom: 0.5rem;
            }
            .auth-subtitle {
                text-align: center;
                color: #4b5563;
                font-weight: 500;
                margin-bottom: 2rem;
            }
        """)
    )