# web/components/layout.py
from fasthtml.common import *

# ATUALIZADO: Define itens específicos para admins e mantém CSS aprimorado
def MainLayout(title, *content, active_page=None, user_profile=None):
    """Layout principal da aplicação com navegação condicional por perfil e estilo aprimorado"""

    # Define os itens de navegação VISÍVEIS APENAS PARA ADMINS
    admin_nav_items = [
        {"url": "/", "label": "Dashboard", "id": "dashboard", "profiles": ["administrator", "general_administrator"]},
        {"url": "/users", "label": "Users", "id": "users", "profiles": ["administrator", "general_administrator"]},
        {"url": "/health-units", "label": "Health Units", "id": "health-units", "profiles": ["administrator", "general_administrator"]},
        {"url": "/attendances", "label": "Attendances", "id": "attendances", "profiles": ["administrator", "general_administrator"]},
    ]

    # Filtra os itens de navegação que devem ser exibidos para o perfil atual
    # Só mostrará itens se o perfil for admin
    nav_items_to_display = [
        item for item in admin_nav_items if user_profile in item.get("profiles", [])
    ]

    # Constrói a lista de navegação (Ul) - Ficará vazia para não-admins
    nav_ul = Ul(*[
        Li(
            A(item["label"], href=item["url"],
              # Marca como ativo se o ID da página corresponder
              cls="active" if active_page == item["id"] else "")
        ) for item in nav_items_to_display # Usa a lista filtrada
    ], cls="nav-links")

    # Retorna a estrutura completa do layout HTML
    return [
        Title(f"{title} - Medical Diagnosis System"), # Título da página no navegador
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        Main(
            Header( # Cabeçalho principal
                Div( H1(A("⚕️ Med Diag AI", href="/"), cls="logo"), cls="brand" ), # Logo sempre visível
                Nav( # Navegação
                    nav_ul, # Renderiza a lista de links (vazia para professional)
                    Div( # Container para botão de logout
                        # Botão Logout visível para QUALQUER perfil logado
                        A("Logout", href="/logout", cls="logout-btn") if user_profile else "",
                        cls="logout-container"
                    ),
                    # Botão de menu mobile (só mostra se houver links para exibir)
                    Button("☰", cls="menu-toggle", onclick="toggleMobileMenu()") if nav_items_to_display else "",
                    cls="main-nav"
                ),
                cls="main-header"
            ),
            Div(*content, cls="content-container"), # O conteúdo específico da página vai aqui
            Footer( # Rodapé
                Div("© 2025 Medical Diagnosis System. All rights reserved.", cls="footer-text"),
                cls="main-footer"
            ),
            cls="container" # Container principal
        ),
        # Bloco CSS completo para o layout (Mantido da resposta anterior)
        Style("""
            /* --- Variáveis Globais --- */
            :root {
                --primary-color: #3B82F6; /* Azul primário */
                --primary-darker: #2563EB;
                --secondary-color: #1F2937; /* Cinza escuro texto */
                --accent-color: #10B981; /* Verde para sucesso */
                --bg-color: #F9FAFB; /* Fundo cinza muito claro */
                --card-bg: #FFFFFF;
                --text-color: #374151;
                --border-color: #E5E7EB;
                --nav-hover-bg: #EBF4FF;
                --nav-active-bg: var(--primary-color);
                --nav-active-text: white;
                --header-height: 65px; /* Altura do cabeçalho */
            }
            /* --- Reset Básico & Globais --- */
            *, *::before, *::after { box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
                background-color: var(--bg-color);
                color: var(--text-color);
                margin: 0;
                padding: 0;
                line-height: 1.6;
                font-size: 16px;
            }
            a { color: var(--primary-color); text-decoration: none; transition: color 0.2s; }
            a:hover { color: var(--primary-darker); }
            img { max-width: 100%; height: auto; display: block; }
            h1, h2, h3, h4, h5, h6 { margin-top: 0; margin-bottom: 0.8rem; color: var(--secondary-color); font-weight: 600; }
            h1 { font-size: 1.8rem; }
            h2 { font-size: 1.5rem; }
            h3 { font-size: 1.25rem; }

            /* --- Estrutura Principal --- */
            .container { display: flex; flex-direction: column; min-height: 100vh; }
            .content-container {
                flex: 1;
                padding: 2rem; /* Padding padrão */
                max-width: 1300px;
                margin: var(--header-height) auto 0 auto; /* Espaço para header fixo e centralização */
                width: 100%;
            }

            /* --- Cabeçalho (Header) --- */
            .main-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 2rem; /* Padding horizontal */
                background-color: var(--card-bg);
                box-shadow: 0 2px 4px rgba(0,0,0,0.06);
                position: fixed; /* Fixa no topo */
                top: 0;
                left: 0;
                width: 100%;
                height: var(--header-height); /* Altura fixa */
                z-index: 1000; /* Garante que fique sobre o conteúdo */
            }
            .brand .logo {
                color: var(--primary-color);
                text-decoration: none;
                font-size: 1.6rem; /* Tamanho do logo */
                font-weight: 700; /* Mais peso */
                display: flex;
                align-items: center;
            }

            /* --- Navegação Principal --- */
            .main-nav { display: flex; align-items: center; gap: 1.5rem; /* Espaço entre nav e logout */ }
            .nav-links { display: flex; list-style: none; margin: 0; padding: 0; gap: 0.5rem; /* Espaço entre links */ }
            .nav-links li a {
                color: var(--secondary-color);
                text-decoration: none;
                padding: 0.6rem 1rem; /* Padding nos links */
                font-weight: 500;
                border-radius: 6px; /* Bordas arredondadas */
                transition: background-color 0.2s, color 0.2s;
                white-space: nowrap; /* Impede quebra */
                font-size: 0.95rem;
            }
            .nav-links li a:hover { background-color: var(--nav-hover-bg); color: var(--primary-darker); }
            .nav-links li a.active { background-color: var(--nav-active-bg); color: var(--nav-active-text); font-weight: 600; }

            /* Botão de Logout */
            .logout-container { /* Necessário para alinhar */ }
            .logout-btn {
                background-color: transparent;
                color: var(--primary-color);
                border: 1px solid var(--primary-color);
                padding: 0.5rem 1rem;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.2s;
                white-space: nowrap;
                font-size: 0.95rem;
            }
            .logout-btn:hover { background-color: var(--primary-color); color: white; }

            /* Botão de Menu Mobile (inicialmente escondido) */
            .menu-toggle {
                 display: none; /* Escondido por padrão */
                 background: none; border: none; font-size: 1.8rem; cursor: pointer; color: var(--secondary-color);
            }

            /* --- Rodapé (Footer) --- */
            .main-footer {
                background-color: #E5E7EB;
                padding: 1.2rem 2rem;
                text-align: center;
                color: #4B5563;
                font-size: 0.875rem;
                margin-top: auto; /* Empurra para baixo */
            }

            /* --- Estilos Comuns para Componentes (Reutilizáveis) --- */
            .card { background-color: var(--card-bg); border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 1.5rem; overflow: hidden; }
            .card [role=heading], .card header { padding: 1rem 1.5rem; background-color: #F9FAFB; border-bottom: 1px solid var(--border-color); margin: 0; font-size: 1.15rem; font-weight: 600; }
            .card > div:not(header):not(footer) { padding: 1.5rem; } /* Padding padrão para conteúdo */
            .card footer { padding: 1rem 1.5rem; background-color: #F9FAFB; border-top: 1px solid var(--border-color); }
            .btn { display: inline-block; background-color: var(--primary-color); color: white; padding: 0.7rem 1.4rem; border-radius: 6px; text-decoration: none; font-weight: 500; border: none; cursor: pointer; transition: background-color 0.2s, transform 0.1s; text-align: center; line-height: 1.2; font-size: 1rem; }
            .btn:hover { background-color: var(--primary-darker); transform: translateY(-1px); }
            .btn-secondary { background-color: #6b7280; }
            .btn-secondary:hover { background-color: #4b5563; }
            .btn-danger { background-color: #EF4444; }
            .btn-danger:hover { background-color: #DC2626; }
            .alert { padding: 1rem; border-radius: 6px; margin-bottom: 1.5rem; border: 1px solid transparent; font-size: 0.95rem; }
            .alert-success { background-color: #D1FAE5; color: #065F46; border-color: #A7F3D0; }
            .alert-error { background-color: #FEE2E2; color: #B91C1C; border-color: #FECACA; }
            .alert-warning { background-color: #FFFBEB; color: #92400E; border-color: #FEF3C7; }
            .alert-info { background-color: #DBEAFE; color: #1E40AF; border-color: #BFDBFE; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; background-color: var(--card-bg); }
            table th, table td { padding: 0.8rem 1rem; text-align: left; border-bottom: 1px solid var(--border-color); font-size: 0.95rem; }
            table th { background-color: #F9FAFB; font-weight: 600; color: #4B5563;}
            .table-container { overflow-x: auto; }

            /* --- Responsividade --- */
            @media (max-width: 992px) { /* Telas médias */
                 .main-header { padding: 0 1rem; }
                 .content-container { padding: 1.5rem; margin-top: var(--header-height); }
                 .nav-links li a { padding: 0.5rem 0.8rem; font-size: 0.9rem; }
            }

            @media (max-width: 768px) { /* Tablets e Celulares Grandes */
                 .main-header { /* Preparação para menu mobile */ }
                 .nav-links {
                     display: none; /* Esconde links por padrão */
                     flex-direction: column;
                     position: absolute;
                     top: var(--header-height); /* Abaixo do header */
                     left: 0;
                     width: 100%;
                     background-color: var(--card-bg);
                     box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                     padding: 1rem 0; /* Padding vertical */
                     gap: 0; /* Remove gap no modo coluna */
                 }
                 .nav-links.active { display: flex; } /* Mostra quando ativo (via JS) */
                 .nav-links li { width: 100%; }
                 .nav-links li a {
                     display: block; /* Ocupa largura total */
                     text-align: center;
                     padding: 0.8rem 1rem;
                     border-radius: 0; /* Remove borda */
                     border-bottom: 1px solid var(--border-color);
                 }
                 .nav-links li:last-child a { border-bottom: none; }
                 .logout-container {
                      /* Move o logout para dentro do menu mobile se ele estiver ativo */
                      /* Ou mantenha fora se preferir */
                 }
                 .menu-toggle { display: block; } /* Mostra o botão hambúrguer */
            }

             @media (max-width: 480px) { /* Celulares Pequenos */
                 .main-header { padding: 0 0.8rem; }
                 .content-container { padding: 1rem; margin-top: calc(var(--header-height) - 5px); } /* Ajusta se header encolher */
                 .brand .logo { font-size: 1.4rem; }
                 .btn { padding: 0.6rem 1rem; font-size: 0.9rem; }
                 h1 { font-size: 1.6rem; }
                 h2 { font-size: 1.3rem; }
                 .logout-container { padding-right: 0.5rem; }
                 .logout-btn { padding: 0.4rem 0.8rem; font-size: 0.85rem;}
             }
        """),
        # Script JS Simples para Toggle
        Script("""
            function toggleMobileMenu() {
                const navLinks = document.querySelector('.nav-links');
                if (navLinks) {
                    navLinks.classList.toggle('active');
                }
            }
        """)
    ]