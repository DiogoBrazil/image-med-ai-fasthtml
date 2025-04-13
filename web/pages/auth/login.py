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
                # Redireciona para a página inicial após login bem-sucedido
                return RedirectResponse('/', status_code=303)
            else:
                error_message = result.get("message", "Login failed. Please try again.")
    
    # Renderiza o formulário de login
    return Div(
        Div(
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"),
            Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"),
            Div(
                Div(
                    Div(
                        I(cls="fas fa-heartbeat logo-icon"),
                        H1("Medical Diagnosis System", cls="auth-title"),
                        cls="logo-container"
                    ),
                    Div(
                        H2("Sign In", cls="auth-subtitle"),
                        P("Enter your credentials to access your account", cls="auth-description"),
                        LoginForm(error=error_message),
                        Div(
                            A("Forgot your password?", href="/auth/reset-password", cls="forgot-password"),
                            cls="help-links"
                        ),
                        cls="auth-form-container"
                    ),
                    P(
                        "Don't have an account? ",
                        A("Register here", href="/auth/register", cls="register-link"),
                        cls="register-text"
                    ),
                    cls="auth-card"
                ),
                Div(
                    H2("Your Health, Our Priority", cls="banner-title"),
                    P("Advanced medical diagnostic platform with AI-powered analysis for healthcare professionals.", cls="banner-text"),
                    cls="auth-banner"
                ),
                cls="auth-content"
            ),
            cls="auth-container"
        ),
        Style("""
            /* Base styles and reset */
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                background: linear-gradient(135deg, #f8faff 0%, #e9f2ff 100%);
                font-family: 'Poppins', sans-serif;
                color: #333;
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            /* Container styling */
            .auth-container {
                width: 100%;
                max-width: 1200px;
                padding: 2rem;
                margin: 0 auto;
            }
            
            .auth-content {
                display: flex;
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
                overflow: hidden;
            }
            
            /* Card styling */
            .auth-card {
                flex: 1;
                padding: 3rem 2.5rem;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            
            /* Banner styling */
            .auth-banner {
                flex: 1;
                background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
                color: white;
                padding: 3rem;
                display: flex;
                flex-direction: column;
                justify-content: center;
                position: relative;
                overflow: hidden;
            }
            
            .auth-banner::before {
                content: '';
                position: absolute;
                top: 0;
                right: 0;
                bottom: 0;
                left: 0;
                background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB2aWV3Qm94PSIwIDAgODAwIDgwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxjaXJjbGUgc3Ryb2tlPSIjZmZmIiBzdHJva2Utb3BhY2l0eT0iLjEiIGN4PSI0MDAiIGN5PSI0MDAiIHI9IjE1MCIvPjxjaXJjbGUgc3Ryb2tlPSIjZmZmIiBzdHJva2Utb3BhY2l0eT0iLjEiIGN4PSI0MDAiIGN5PSI0MDAiIHI9IjI1MCIvPjxjaXJjbGUgc3Ryb2tlPSIjZmZmIiBzdHJva2Utb3BhY2l0eT0iLjEiIGN4PSI0MDAiIGN5PSI0MDAiIHI9IjM1MCIvPjwvZz48L3N2Zz4=');
                background-size: cover;
                background-position: center;
                opacity: 0.2;
            }
            
            .banner-title {
                font-size: 1.8rem;
                font-weight: 600;
                margin-bottom: 1rem;
                position: relative;
            }
            
            .banner-text {
                font-size: 1rem;
                line-height: 1.6;
                opacity: 0.9;
                position: relative;
                max-width: 80%;
            }
            
            /* Logo styling */
            .logo-container {
                display: flex;
                align-items: center;
                gap: 0.8rem;
                margin-bottom: 2rem;
            }
            
            .logo-icon {
                font-size: 2rem;
                color: #3b82f6;
            }
            
            .auth-title {
                color: #3b82f6;
                font-size: 1.5rem;
                font-weight: 600;
            }
            
            /* Form container */
            .auth-form-container {
                margin-bottom: 2rem;
            }
            
            .auth-subtitle {
                font-size: 1.8rem;
                color: #1f2937;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }
            
            .auth-description {
                color: #6b7280;
                margin-bottom: 2rem;
                font-size: 0.95rem;
            }
            
            /* Form styling (assuming these styles apply to the LoginForm component) */
            form {
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
                margin-bottom: 1.5rem;
            }
            
            .form-group {
                position: relative;
            }
            
            .form-control {
                width: 100%;
                padding: 1rem 1.2rem 1rem 2.8rem;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                font-size: 1.05rem;
                transition: all 0.3s;
                font-family: 'Poppins', sans-serif;
                height: 3.5rem;
            }
            
            .form-control:focus {
                border-color: #3b82f6;
                outline: none;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
            }
            
            .form-icon {
                position: absolute;
                left: 1rem;
                top: 50%;
                transform: translateY(-50%);
                color: #9ca3af;
                font-size: 1.2rem;
            }
            
            label {
                display: block;
                margin-bottom: 0.5rem;
                font-weight: 500;
                color: #4b5563;
                font-size: 1rem;
            }
            
            .error-message {
                color: #ef4444;
                font-size: 0.875rem;
                margin-top: 0.5rem;
                display: block;
            }
            
            .btn {
                padding: 1rem 1.5rem;
                border-radius: 8px;
                font-weight: 600;
                font-size: 1.05rem;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
                border: none;
                width: 100%;
                font-family: 'Poppins', sans-serif;
                height: 3.5rem;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
                color: white;
                letter-spacing: 0.5px;
            }
            
            .btn-primary:hover {
                background: linear-gradient(135deg, #4338ca 0%, #2563eb 100%);
                box-shadow: 0 8px 15px rgba(37, 99, 235, 0.3);
                transform: translateY(-2px);
            }
            
            /* Helper links */
            .help-links {
                display: flex;
                justify-content: flex-end;
                margin-top: 1rem;
            }
            
            .forgot-password {
                color: #6b7280;
                font-size: 0.875rem;
                text-decoration: none;
                transition: color 0.3s;
            }
            
            .forgot-password:hover {
                color: #3b82f6;
                text-decoration: underline;
            }
            
            .register-text {
                text-align: center;
                color: #6b7280;
                font-size: 0.9rem;
            }
            
            .register-link {
                color: #3b82f6;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s;
            }
            
            .register-link:hover {
                text-decoration: underline;
            }
            
            /* Responsive styles */
            @media (max-width: 1024px) {
                .auth-banner {
                    padding: 2rem;
                }
            }
            
            @media (max-width: 768px) {
                .auth-content {
                    flex-direction: column;
                }
                
                .auth-banner {
                    display: none;
                }
                
                .auth-card {
                    padding: 2rem;
                }
            }
            
            @media (max-width: 480px) {
                .auth-container {
                    padding: 1rem;
                }
                
                .auth-card {
                    padding: 1.5rem;
                }
                
                .auth-title {
                    font-size: 1.3rem;
                }
                
                .auth-subtitle {
                    font-size: 1.6rem;
                }
            }
        """)
    )