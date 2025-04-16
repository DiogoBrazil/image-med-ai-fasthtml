from fasthtml.common import *
from components.forms import LoginForm
from services.auth_service import AuthService

async def login_page(request):
    """Renderiza a página de login com elementos de landing page"""
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
    
    # Renderiza a landing page com formulário de login
    return Html(
        Head(
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Title("Medical Diagnosis System - AI-Powered Medical Diagnostics"),
            Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"),
            Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"),
            Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.css"),
            Style("""
                /* Base styles and reset */
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                :root {
                    --primary: #3b82f6;
                    --primary-dark: #1e40af;
                    --secondary: #10b981;
                    --light-bg: #f8faff;
                    --dark-text: #1f2937;
                    --gray-text: #6b7280;
                    --light-text: #f9fafb;
                    --card-bg: #ffffff;
                    --border-color: #e5e7eb;
                    --shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
                    --hover-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
                }
                
                html {
                    scroll-behavior: smooth;
                }
                
                body {
                    background: var(--light-bg);
                    font-family: 'Poppins', sans-serif;
                    color: var(--dark-text);
                    line-height: 1.6;
                }
                
                a {
                    text-decoration: none;
                    color: var(--primary);
                    transition: all 0.3s ease;
                }
                
                a:hover {
                    color: var(--primary-dark);
                }
                
                img {
                    max-width: 100%;
                }
                
                .container {
                    width: 100%;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 0 2rem;
                }
                
                .btn {
                    display: inline-block;
                    padding: 0.8rem 1.5rem;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 1rem;
                    text-align: center;
                    cursor: pointer;
                    transition: all 0.3s;
                    border: none;
                }
                
                .btn-primary {
                    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
                    color: white;
                }
                
                .btn-primary:hover {
                    background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%);
                    box-shadow: 0 8px 15px rgba(37, 99, 235, 0.3);
                    transform: translateY(-2px);
                }
                
                .btn-outline {
                    background: transparent;
                    color: var(--primary);
                    border: 2px solid var(--primary);
                }
                
                .btn-outline:hover {
                    background: var(--primary);
                    color: white;
                }
                
                .section {
                    padding: 5rem 0;
                }
                
                .text-center {
                    text-align: center;
                }
                
                /* Header / Navigation */
                header {
                    background-color: white;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
                    position: fixed;
                    width: 100%;
                    top: 0;
                    z-index: 1000;
                }
                
                .navbar {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 1rem 0;
                }
                
                .logo {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                
                .logo-icon {
                    font-size: 1.8rem;
                    color: var(--primary);
                }
                
                .logo-text {
                    font-size: 1.3rem;
                    font-weight: 700;
                    color: var(--dark-text);
                }
                
                .nav-links {
                    display: flex;
                    gap: 2rem;
                }
                
                .nav-links a {
                    color: var(--dark-text);
                    font-weight: 500;
                    font-size: 1rem;
                }
                
                .nav-links a:hover {
                    color: var(--primary);
                }
                
                .menu-toggle {
                    display: none;
                    font-size: 1.5rem;
                    cursor: pointer;
                }
                
                /* Hero Section */
                .hero {
                    background: linear-gradient(135deg, #f6f9ff 0%, #e9f2ff 100%);
                    padding: 10rem 0 5rem;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                }
                
                .hero-container {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 4rem;
                    align-items: center;
                }
                
                .hero-content {
                    max-width: 550px;
                }
                
                .hero-title {
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 1.5rem;
                    line-height: 1.2;
                    color: var(--dark-text);
                }
                
                .hero-title span {
                    color: var(--primary);
                }
                
                .hero-subtitle {
                    font-size: 1.1rem;
                    color: var(--gray-text);
                    margin-bottom: 2rem;
                }
                
                .hero-buttons {
                    display: flex;
                    gap: 1rem;
                    margin-bottom: 3rem;
                }
                
                .features-preview {
                    display: flex;
                    gap: 2rem;
                }
                
                .feature-item {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                
                .feature-icon {
                    font-size: 1.2rem;
                    color: var(--primary);
                }
                
                .feature-text {
                    font-size: 0.9rem;
                    font-weight: 500;
                }
                
                /* Login Card */
                .login-card {
                    background: white;
                    border-radius: 12px;
                    padding: 2.5rem;
                    box-shadow: var(--shadow);
                    transition: all 0.3s;
                }
                
                .login-card:hover {
                    box-shadow: var(--hover-shadow);
                    transform: translateY(-5px);
                }
                
                .login-title {
                    font-size: 1.5rem;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                    color: var(--dark-text);
                }
                
                .login-subtitle {
                    font-size: 0.95rem;
                    color: var(--gray-text);
                    margin-bottom: 2rem;
                }
                
                /* Custom submit button styling que será aplicado manualmente */
                .form-submit-btn {
                    width: 100%;
                    padding: 1rem;
                    font-size: 1rem;
                    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s;
                    font-family: 'Poppins', sans-serif;
                }

                .form-submit-btn:hover {
                    background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%);
                    box-shadow: 0 8px 15px rgba(37, 99, 235, 0.3);
                    transform: translateY(-2px);
                }
                
                /* Form styling */
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
                    border: 1px solid var(--border-color);
                    border-radius: 8px;
                    font-size: 1rem;
                    transition: all 0.3s;
                    font-family: 'Poppins', sans-serif;
                }
                
                .form-control:focus {
                    border-color: var(--primary);
                    outline: none;
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
                }
                
                .form-icon {
                    position: absolute;
                    left: 1rem;
                    top: 50%;
                    transform: translateY(-50%);
                    color: var(--gray-text);
                    font-size: 1.1rem;
                }
                
                label {
                    display: block;
                    margin-bottom: 0.5rem;
                    font-weight: 500;
                    color: var(--dark-text);
                    font-size: 0.95rem;
                }
                
                .error-message {
                    color: #ef4444;
                    font-size: 0.875rem;
                    margin-top: 0.5rem;
                    display: block;
                }
                
                .form-help {
                    display: flex;
                    justify-content: space-between;
                    font-size: 0.85rem;
                    margin-bottom: 1.5rem;
                }
                
                .remember-me {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                
                .forgot-password {
                    color: var(--primary);
                }
                
                .btn-login {
                    width: 100%;
                    padding: 1rem;
                    font-size: 1rem;
                }
                
                .register-prompt {
                    text-align: center;
                    font-size: 0.9rem;
                    margin-top: 1.5rem;
                    color: var(--gray-text);
                }
                
                .register-link {
                    color: var(--primary);
                    font-weight: 500;
                }
                
                /* Features Section */
                .section-title {
                    font-size: 2rem;
                    font-weight: 700;
                    margin-bottom: 1rem;
                    text-align: center;
                }
                
                .section-subtitle {
                    font-size: 1.1rem;
                    color: var(--gray-text);
                    margin-bottom: 3rem;
                    text-align: center;
                    max-width: 700px;
                    margin-left: auto;
                    margin-right: auto;
                }
                
                .features-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 2rem;
                    margin-top: 4rem;
                }
                
                .feature-card {
                    background: white;
                    border-radius: 12px;
                    padding: 2rem;
                    box-shadow: var(--shadow);
                    transition: all 0.3s;
                    position: relative;
                    overflow: hidden;
                }
                
                .feature-card:hover {
                    box-shadow: var(--hover-shadow);
                    transform: translateY(-5px);
                }
                
                .feature-card::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 5px;
                    height: 100%;
                    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
                }
                
                .feature-card-icon {
                    width: 60px;
                    height: 60px;
                    background: rgba(59, 130, 246, 0.1);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 1.5rem;
                }
                
                .feature-card-icon i {
                    font-size: 1.8rem;
                    color: var(--primary);
                }
                
                .feature-card-title {
                    font-size: 1.2rem;
                    font-weight: 600;
                    margin-bottom: 1rem;
                }
                
                .feature-card-text {
                    color: var(--gray-text);
                    font-size: 0.95rem;
                }
                
                /* AI Models Section */
                .ai-models {
                    background: linear-gradient(135deg, #f6f9ff 0%, #e9f2ff 100%);
                    padding: 7rem 0;
                }
                
                .models-wrapper {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 1.5rem;
                }
                
                .model-card {
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: var(--shadow);
                    transition: all 0.3s;
                }
                
                .model-card:hover {
                    box-shadow: var(--hover-shadow);
                    transform: translateY(-5px);
                }
                
                .model-img {
                    height: 200px;
                    background-size: cover;
                    background-position: center;
                }
                
                .respiratory-img {
                    background-image: url('https://via.placeholder.com/400x200/3b82f6/ffffff?text=Respiratory+Disease');
                }
                
                .tuberculosis-img {
                    background-image: url('https://via.placeholder.com/400x200/10b981/ffffff?text=Tuberculosis');
                }
                
                .osteoporosis-img {
                    background-image: url('https://via.placeholder.com/400x200/f59e0b/ffffff?text=Osteoporosis');
                }
                
                .breast-cancer-img {
                    background-image: url('https://via.placeholder.com/400x200/ef4444/ffffff?text=Breast+Cancer');
                }
                
                .model-content {
                    padding: 1.5rem;
                }
                
                .model-title {
                    font-size: 1.2rem;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                    color: var(--dark-text);
                }
                
                .model-description {
                    font-size: 0.9rem;
                    color: var(--gray-text);
                    margin-bottom: 1.5rem;
                }
                
                .model-accuracy {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    margin-bottom: 1rem;
                }
                
                .accuracy-icon {
                    color: var(--secondary);
                    font-size: 1.1rem;
                }
                
                .accuracy-text {
                    font-weight: 600;
                    color: var(--secondary);
                }
                
                .model-categories {
                    font-size: 0.85rem;
                    color: var(--gray-text);
                }
                
                /* Benefits Section */
                .benefits {
                    background: white;
                    padding: 7rem 0;
                }
                
                .benefits-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 3rem;
                }
                
                .benefit-item {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                }
                
                .benefit-icon {
                    width: 80px;
                    height: 80px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 1.5rem;
                    color: white;
                    font-size: 2rem;
                }
                
                .benefit-title {
                    font-size: 1.2rem;
                    font-weight: 600;
                    margin-bottom: 1rem;
                }
                
                .benefit-description {
                    font-size: 0.95rem;
                    color: var(--gray-text);
                    max-width: 300px;
                }
                
                /* CTA Section */
                .cta {
                    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
                    color: var(--light-text);
                    padding: 5rem 0;
                    text-align: center;
                }
                
                .cta-title {
                    font-size: 2rem;
                    font-weight: 700;
                    margin-bottom: 1.5rem;
                }
                
                .cta-text {
                    font-size: 1.1rem;
                    max-width: 700px;
                    margin: 0 auto 2.5rem;
                    opacity: 0.9;
                }
                
                .cta-buttons {
                    display: flex;
                    gap: 1rem;
                    justify-content: center;
                }
                
                .btn-white {
                    background: white;
                    color: var(--primary);
                }
                
                .btn-white:hover {
                    background: rgba(255, 255, 255, 0.9);
                    transform: translateY(-2px);
                }
                
                .btn-outline-white {
                    border: 2px solid white;
                    color: white;
                    background: transparent;
                }
                
                .btn-outline-white:hover {
                    background: rgba(255, 255, 255, 0.1);
                }
                
                /* Footer */
                footer {
                    background: var(--dark-text);
                    color: var(--light-text);
                    padding: 5rem 0 2rem;
                }
                
                .footer-content {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 3rem;
                    margin-bottom: 3rem;
                }
                
                .footer-column h4 {
                    font-size: 1.1rem;
                    font-weight: 600;
                    margin-bottom: 1.5rem;
                    position: relative;
                    padding-bottom: 0.5rem;
                }
                
                .footer-column h4::after {
                    content: '';
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    width: 50px;
                    height: 2px;
                    background: var(--primary);
                }
                
                .footer-links {
                    display: flex;
                    flex-direction: column;
                    gap: 0.5rem;
                }
                
                .footer-links a {
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 0.9rem;
                    transition: all 0.3s;
                }
                
                .footer-links a:hover {
                    color: white;
                    padding-left: 5px;
                }
                
                .footer-about {
                    font-size: 0.9rem;
                    color: rgba(255, 255, 255, 0.7);
                    margin-bottom: 1.5rem;
                }
                
                .social-links {
                    display: flex;
                    gap: 1rem;
                }
                
                .social-icon {
                    width: 36px;
                    height: 36px;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.1);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 1rem;
                    transition: all 0.3s;
                }
                
                .social-icon:hover {
                    background: var(--primary);
                    transform: translateY(-3px);
                }
                
                .footer-bottom {
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                    padding-top: 2rem;
                    text-align: center;
                    font-size: 0.9rem;
                    color: rgba(255, 255, 255, 0.7);
                }
                
                /* Responsive styles */
                @media (max-width: 992px) {
                    .hero-container {
                        grid-template-columns: 1fr;
                        gap: 3rem;
                    }
                    
                    .hero-content {
                        order: 2;
                        text-align: center;
                        margin: 0 auto;
                    }
                    
                    .login-card {
                        max-width: 500px;
                        margin: 0 auto;
                    }
                    
                    .hero-buttons {
                        justify-content: center;
                    }
                    
                    .features-preview {
                        justify-content: center;
                    }
                    
                    .hero-title {
                        font-size: 2.2rem;
                    }
                }
                
                @media (max-width: 768px) {
                    .section {
                        padding: 4rem 0;
                    }
                    
                    .navbar {
                        position: relative;
                    }
                    
                    .menu-toggle {
                        display: block;
                    }
                    
                    .nav-links {
                        position: absolute;
                        top: 100%;
                        left: 0;
                        right: 0;
                        background: white;
                        flex-direction: column;
                        padding: 1.5rem;
                        gap: 1.5rem;
                        box-shadow: 0 5px 10px rgba(0, 0, 0, 0.05);
                        display: none;
                    }
                    
                    .nav-links.active {
                        display: flex;
                    }
                    
                    .hero-title {
                        font-size: 2rem;
                    }
                    
                    .section-title {
                        font-size: 1.8rem;
                    }
                    
                    .cta-title {
                        font-size: 1.8rem;
                    }
                    
                    .features-preview {
                        flex-direction: column;
                        align-items: center;
                        gap: 1rem;
                    }
                }
                
                @media (max-width: 576px) {
                    .hero {
                        padding: 8rem 0 3rem;
                    }
                    
                    .container {
                        padding: 0 1rem;
                    }
                    
                    .hero-title {
                        font-size: 1.8rem;
                    }
                    
                    .hero-subtitle {
                        font-size: 1rem;
                    }
                    
                    .hero-buttons {
                        flex-direction: column;
                    }
                    
                    .section-title {
                        font-size: 1.6rem;
                    }
                    
                    .section-subtitle {
                        font-size: 1rem;
                    }
                    
                    .cta-buttons {
                        flex-direction: column;
                    }
                }
            """),
            Script(src="https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.js"),
        ),
        Body(
            # Header / Navigation
            Header(
                Div(
                    Div(
                        Div(
                            A(
                                I(cls="fas fa-heartbeat logo-icon"),
                                Span("MedDiagnosis", cls="logo-text"),
                                href="/",
                                cls="logo"
                            ),
                            Div(
                                A("Home", href="#"),
                                A("Features", href="#features"),
                                A("Models", href="#models"),
                                A("Benefits", href="#benefits"),
                                A("Contact", href="#contact"),
                                cls="nav-links"
                            ),
                            I(cls="fas fa-bars menu-toggle"),
                            cls="navbar"
                        ),
                        cls="container"
                    )
                )
            ),
            
            # Hero Section / Login
            Section(
                Div(
                    Div(
                        Div(
                            Div(
                                H1(
                                    "Diagnostico Médico com Inteligência ",
                                    Span("Artificial", cls="text-primary"),
                                    cls="hero-title"
                                ),
                                P("Sistema avançado de diagnóstico médico com análise impulsionada por IA para profissionais de saúde, fornecendo predições precisas para doenças respiratórias, tuberculose, osteoporose e câncer de mama.", cls="hero-subtitle"),
                                Div(
                                    A("Saiba Mais", href="#features", cls="btn btn-primary"),
                                    A("Contato", href="#contact", cls="btn btn-outline"),
                                    cls="hero-buttons"
                                ),
                                Div(
                                    Div(
                                        I(cls="fas fa-check-circle feature-icon"),
                                        Span("Predição Precisa", cls="feature-text"),
                                        cls="feature-item"
                                    ),
                                    Div(
                                        I(cls="fas fa-shield-alt feature-icon"),
                                        Span("Seguro & Confiável", cls="feature-text"),
                                        cls="feature-item"
                                    ),
                                    cls="features-preview"
                                ),
                                cls="hero-content"
                            ),
                            Div(
                                Div(
                                    H2("Acesse sua Conta", cls="login-title"),
                                    P("Entre com suas credenciais para acessar o sistema", cls="login-subtitle"),
                                    # Aqui usamos apenas o parâmetro error que o componente LoginForm aceita
                                    Div(
                                        LoginForm(error=error_message),
                                        Style("""
                                            /* Estilização customizada para o botão de login */
                                            form button[type="submit"] {
                                                width: 100%;
                                                padding: 1rem;
                                                font-size: 1rem;
                                                background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
                                                color: white;
                                                border: none;
                                                border-radius: 8px;
                                                font-weight: 600;
                                                cursor: pointer;
                                                transition: all 0.3s;
                                                font-family: 'Poppins', sans-serif;
                                            }
                                            
                                            form button[type="submit"]:hover {
                                                background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%);
                                                box-shadow: 0 8px 15px rgba(37, 99, 235, 0.3);
                                                transform: translateY(-2px);
                                            }
                                        """)
                                    ),
                                    P(
                                        "Não tem uma conta? ",
                                        A("Registre-se aqui", href="/auth/register", cls="register-link"),
                                        cls="register-prompt"
                                    ),
                                    cls="login-card"
                                ),
                                cls="hero-form"
                            ),
                            cls="hero-container"
                        ),
                        cls="container"
                    ),
                    cls="hero", id="home"
                ),
            ),
            
            # Features Section
            Section(
                Div(
                    H2("Recursos Principais", cls="section-title"),
                    P("Nossa plataforma combina tecnologia de ponta em inteligência artificial com interface intuitiva para oferecer diagnósticos médicos precisos e eficientes.", cls="section-subtitle"),
                    Div(
                        Div(
                            Div(
                                I(cls="fas fa-brain", ), 
                                cls="feature-card-icon"
                            ),
                            H3("Análise por IA", cls="feature-card-title"),
                            P("Modelos de aprendizado profundo treinados com milhares de imagens médicas para fornecer diagnósticos precisos e confiáveis.", cls="feature-card-text"),
                            cls="feature-card", **{"data-aos": "fade-up", "data-aos-delay": "100"}
                        ),
                        Div(
                            Div(
                                I(cls="fas fa-hospital-user", ), 
                                cls="feature-card-icon"
                            ),
                            H3("Gestão de Atendimentos", cls="feature-card-title"),
                            P("Crie e gerencie atendimentos médicos, vincule unidades de saúde e mantenha um histórico completo de diagnósticos para cada paciente.", cls="feature-card-text"),
                            cls="feature-card", **{"data-aos": "fade-up", "data-aos-delay": "200"}
                        ),
                        Div(
                            Div(
                                I(cls="fas fa-chart-line", ), 
                                cls="feature-card-icon"
                            ),
                            H3("Estatísticas & Análises", cls="feature-card-title"),
                            P("Visualize dados estatísticos detalhados para auxiliar na tomada de decisões com base em tendências e padrões identificados.", cls="feature-card-text"),
                            cls="feature-card", **{"data-aos": "fade-up", "data-aos-delay": "300"}
                        ),
                        Div(
                            Div(
                                I(cls="fas fa-hospital", ), 
                                cls="feature-card-icon"
                            ),
                            H3("Integração com Unidades", cls="feature-card-title"),
                            P("Vincule unidades de saúde ao sistema para facilitar o gerenciamento e a distribuição de recursos médicos.", cls="feature-card-text"),
                            cls="feature-card", **{"data-aos": "fade-up", "data-aos-delay": "400"}
                        ),
                        Div(
                            Div(
                                I(cls="fas fa-mobile-alt", ), 
                                cls="feature-card-icon"
                            ),
                            H3("Interface Responsiva", cls="feature-card-title"),
                            P("Acesse o sistema de qualquer dispositivo com uma interface intuitiva e responsiva, projetada para médicos e profissionais de saúde.", cls="feature-card-text"),
                            cls="feature-card", **{"data-aos": "fade-up", "data-aos-delay": "500"}
                        ),
                        cls="features-grid"
                    ),
                    cls="container"
                ),
                cls="section", id="features"
            ),
            
            # AI Models Section
            Section(
                Div(
                    H2("Modelos de IA para Diagnóstico", cls="section-title"),
                    P("Nossa plataforma utiliza redes neurais convolucionais de última geração para fornecer diagnósticos precisos em diferentes áreas da medicina.", cls="section-subtitle"),
                    Div(
                        Div(
                            Div(cls="model-img respiratory-img"),
                            Div(
                                H3("Doenças Respiratórias", cls="model-title"),
                                P("Diagnóstico de condições respiratórias a partir de raio-x torácico, incluindo COVID-19, pneumonia bacteriana e pneumonia viral.", cls="model-description"),
                                Div(
                                    I(cls="fas fa-chart-pie accuracy-icon"),
                                    Span("95% de precisão", cls="accuracy-text"),
                                    cls="model-accuracy"
                                ),
                                P("Classificação: Normal, COVID-19, Pneumonia Bacteriana, Pneumonia Viral", cls="model-categories"),
                                cls="model-content"
                            ),
                            cls="model-card", **{"data-aos": "zoom-in"}
                        ),
                        Div(
                            Div(cls="model-img tuberculosis-img"),
                            Div(
                                H3("Tuberculose", cls="model-title"),
                                P("Detecção de tuberculose a partir de raio-x torácico, fornecendo resultado positivo ou negativo com alta precisão.", cls="model-description"),
                                Div(
                                    I(cls="fas fa-chart-pie accuracy-icon"),
                                    Span("93% de precisão", cls="accuracy-text"),
                                    cls="model-accuracy"
                                ),
                                P("Classificação: Positivo, Negativo", cls="model-categories"),
                                cls="model-content"
                            ),
                            cls="model-card", **{"data-aos": "zoom-in", "data-aos-delay": "100"}
                        ),
                        Div(
                            Div(cls="model-img osteoporosis-img"),
                            Div(
                                H3("Osteoporose", cls="model-title"),
                                P("Análise de raios-x do joelho e canela para identificação de osteoporose e osteopenia em diversos estágios.", cls="model-description"),
                                Div(
                                    I(cls="fas fa-chart-pie accuracy-icon"),
                                    Span("91% de precisão", cls="accuracy-text"),
                                    cls="model-accuracy"
                                ),
                                P("Classificação: Normal, Osteopenia, Osteoporose", cls="model-categories"),
                                cls="model-content"
                            ),
                            cls="model-card", **{"data-aos": "zoom-in", "data-aos-delay": "200"}
                        ),
                        Div(
                            Div(cls="model-img breast-cancer-img"),
                            Div(
                                H3("Câncer de Mama", cls="model-title"),
                                P("Detecção de câncer de mama a partir de mamografias, auxiliando no diagnóstico precoce e aumentando as chances de tratamento.", cls="model-description"),
                                Div(
                                    I(cls="fas fa-chart-pie accuracy-icon"),
                                    Span("94% de precisão", cls="accuracy-text"),
                                    cls="model-accuracy"
                                ),
                                P("Classificação detalhada de lesões e anomalias", cls="model-categories"),
                                cls="model-content"
                            ),
                            cls="model-card", **{"data-aos": "zoom-in", "data-aos-delay": "300"}
                        ),
                        cls="models-wrapper"
                    ),
                    cls="container"
                ),
                cls="section ai-models", id="models"
            ),
            
            # Benefits Section
            Section(
                Div(
                    H2("Benefícios do Sistema", cls="section-title"),
                    P("Nossa plataforma oferece vantagens significativas para instituições de saúde e profissionais médicos.", cls="section-subtitle"),
                    Div(
                        Div(
                            Div(
                                I(cls="fas fa-clock"),
                                cls="benefit-icon"
                            ),
                            H3("Diagnóstico Rápido", cls="benefit-title"),
                            P("Reduza o tempo de diagnóstico com análises automatizadas de imagens médicas em segundos.", cls="benefit-description"),
                            cls="benefit-item", **{"data-aos": "fade-up"}
                        ),
                        Div(
                            Div(
                                I(cls="fas fa-check-double"),
                                cls="benefit-icon"
                            ),
                            H3("Alta Precisão", cls="benefit-title"),
                            P("Modelos de IA treinados com grandes volumes de dados para fornecer diagnósticos com elevada taxa de acerto.", cls="benefit-description"),
                            cls="benefit-item", **{"data-aos": "fade-up", "data-aos-delay": "100"}
                        ),
                        Div(
                            Div(
                                I(cls="fas fa-database"),
                                cls="benefit-icon"
                            ),
                            H3("Dados Estatísticos", cls="benefit-title"),
                            P("Obtenha insights valiosos através de relatórios estatísticos detalhados para melhorar a tomada de decisão.", cls="benefit-description"),
                            cls="benefit-item", **{"data-aos": "fade-up", "data-aos-delay": "200"}
                        ),
                        cls="benefits-grid"
                    ),
                    cls="container"
                ),
                cls="section benefits", id="benefits"
            ),
            
            # CTA Section
            Section(
                Div(
                    H2("Comece a Utilizar Hoje Mesmo", cls="cta-title"),
                    P("Transforme a forma como sua instituição realiza diagnósticos médicos com nosso avançado sistema de inteligência artificial.", cls="cta-text"),
                    Div(
                        A("Registre-se Agora", href="/auth/register", cls="btn btn-white"),
                        A("Entre em Contato", href="#contact", cls="btn btn-outline-white"),
                        cls="cta-buttons"
                    ),
                    cls="container"
                ),
                cls="section cta"
            ),
            
            # Footer
            Footer(
                Div(
                    Div(
                        Div(
                            H4("Sobre Nós"),
                            P("Sistema avançado de diagnóstico médico com inteligência artificial, fornecendo análises precisas para profissionais de saúde.", cls="footer-about"),
                            Div(
                                A(I(cls="fab fa-facebook-f"), href="#", cls="social-icon"),
                                A(I(cls="fab fa-twitter"), href="#", cls="social-icon"),
                                A(I(cls="fab fa-linkedin-in"), href="#", cls="social-icon"),
                                A(I(cls="fab fa-instagram"), href="#", cls="social-icon"),
                                cls="social-links"
                            ),
                            cls="footer-column"
                        ),
                        Div(
                            H4("Links Rápidos"),
                            Div(
                                A("Início", href="#home"),
                                A("Recursos", href="#features"),
                                A("Modelos", href="#models"),
                                A("Benefícios", href="#benefits"),
                                A("Contato", href="#contact"),
                                cls="footer-links"
                            ),
                            cls="footer-column"
                        ),
                        Div(
                            H4("Modelos"),
                            Div(
                                A("Doenças Respiratórias", href="#models"),
                                A("Tuberculose", href="#models"),
                                A("Osteoporose", href="#models"),
                                A("Câncer de Mama", href="#models"),
                                cls="footer-links"
                            ),
                            cls="footer-column"
                        ),
                        Div(
                            H4("Contato", id="contact"),
                            Div(
                                P(I(cls="fas fa-map-marker-alt"), " Rua dos Diagnósticos, 123"),
                                P(I(cls="fas fa-phone"), " +55 (11) 9876-5432"),
                                P(I(cls="fas fa-envelope"), " contato@meddiagnosis.com"),
                                cls="footer-links"
                            ),
                            cls="footer-column"
                        ),
                        cls="footer-content"
                    ),
                    Div(
                        P("© 2025 Medical Diagnosis System. Todos os direitos reservados."),
                        cls="footer-bottom"
                    ),
                    cls="container"
                )
            ),
            
            # JavaScript
            Script("""
                // Menu Toggle
                document.addEventListener('DOMContentLoaded', function() {
                    const menuToggle = document.querySelector('.menu-toggle');
                    const navLinks = document.querySelector('.nav-links');
                    
                    menuToggle.addEventListener('click', function() {
                        navLinks.classList.toggle('active');
                    });
                    
                    // Initialize AOS
                    AOS.init({
                        duration: 800,
                        easing: 'ease-in-out',
                        once: true
                    });
                    
                    // Smooth scrolling
                    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                        anchor.addEventListener('click', function (e) {
                            e.preventDefault();
                            
                            const target = document.querySelector(this.getAttribute('href'));
                            
                            if (target) {
                                window.scrollTo({
                                    top: target.offsetTop - 80,
                                    behavior: 'smooth'
                                });
                                
                                // Close mobile menu if open
                                navLinks.classList.remove('active');
                            }
                        });
                    });
                });
            """)
        )
    )