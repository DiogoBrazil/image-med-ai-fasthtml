# web/components/layout.py
from fasthtml.common import *

# ATUALIZADO: Recebe user_profile para filtrar a navegação
def MainLayout(title, *content, active_page=None, user_profile=None):
    """Layout principal da aplicação com navegação condicional"""

    # Define todos os itens de navegação possíveis e os perfis que podem vê-los
    all_nav_items = [
        {"url": "/", "label": "Dashboard", "id": "dashboard", "profiles": ["professional", "administrator", "general_administrator"]},
        {"url": "/users", "label": "Users", "id": "users", "profiles": ["administrator", "general_administrator"]},
        {"url": "/health-units", "label": "Health Units", "id": "health-units", "profiles": ["administrator", "general_administrator"]},
        {"url": "/attendances", "label": "Attendances", "id": "attendances", "profiles": ["administrator", "general_administrator"]},
        # Adicione aqui outros itens de menu se necessário.
        # Exemplo: Link direto para iniciar uma predição (útil para profissional)
        # {"url": "/predict/select", "label": "New Prediction", "id": "predict", "profiles": ["professional"]},
    ]

    # Filtra os itens de navegação que devem ser exibidos para o perfil atual
    # Se user_profile for None (ex: antes do login), a lista ficará vazia (exceto se permitir itens públicos)
    nav_items_for_user = [
        item for item in all_nav_items if user_profile in item["profiles"]
    ]

    # Constrói a lista de navegação (Ul)
    nav_ul = Ul(*[
        Li(
            A(item["label"], href=item["url"],
              # Marca como ativo se o ID da página corresponder
              cls="active" if active_page == item["id"] else "")
        ) for item in nav_items_for_user # Usa a lista filtrada
    ])

    # Retorna a estrutura completa do layout HTML
    return [
        Title(f"{title} - Medical Diagnosis System"), # Título da página no navegador
        Main(
            Header( # Cabeçalho principal
                Div( H1(A("Medical Diagnosis System", href="/"), cls="logo"), cls="brand" ),
                Nav( # Navegação
                    nav_ul, # A lista de links filtrada
                    A("Logout", href="/logout", cls="logout-btn"), # Botão de logout sempre visível para logados
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
        # Bloco CSS completo para o layout
        Style("""
            /* --- Variáveis de Cor (Exemplo) --- */
            :root {
                --primary-color: #2563eb;
                --secondary-color: #1e3a8a;
                --bg-color: #f3f4f6;
                --text-color: #1f2937;
                --border-color: #e5e7eb;
                --success-color: #10b981;
                --error-color: #ef4444;
                --warning-color: #f59e0b;
                --nav-hover-color: #dbeafe; /* Azul bem claro para hover */
            }
            /* --- Estilos Globais --- */
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
                margin: 0;
                padding: 0;
                line-height: 1.5;
            }
            a {
                color: var(--primary-color);
                text-decoration: none;
                transition: color 0.2s;
            }
            a:hover {
                color: var(--secondary-color);
            }
            img {
                 max-width: 100%;
                 height: auto;
            }
            /* --- Estrutura Principal --- */
            .container {
                display: flex;
                flex-direction: column;
                min-height: 100vh;
            }
            .content-container {
                flex: 1; /* Faz o conteúdo ocupar o espaço restante */
                padding: 1.5rem 2rem; /* Padding responsivo */
                max-width: 1300px; /* Largura máxima para conteúdo */
                margin: 0 auto; /* Centraliza */
                width: 100%;
                box-sizing: border-box; /* Inclui padding na largura */
            }
             @media (max-width: 768px) {
                 .content-container {
                     padding: 1rem;
                 }
             }

            /* --- Cabeçalho (Header) --- */
            .main-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.8rem 2rem; /* Padding vertical menor */
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05); /* Sombra mais sutil */
                position: sticky; /* Fixa no topo */
                top: 0;
                z-index: 100; /* Garante que fique sobre o conteúdo */
            }
            .brand .logo {
                color: var(--primary-color);
                text-decoration: none;
                font-size: 1.4rem; /* Tamanho do logo */
                font-weight: 600; /* Peso da fonte */
            }

            /* --- Navegação Principal --- */
            .main-nav {
                display: flex;
                align-items: center;
            }
            .main-nav ul {
                display: flex;
                list-style: none;
                margin: 0 1.5rem 0 0; /* Espaço antes do botão Logout */
                padding: 0;
            }
            .main-nav ul li {
                margin-right: 0.5rem; /* Espaço entre itens */
            }
            .main-nav ul li a {
                color: var(--text-color);
                text-decoration: none;
                padding: 0.6rem 0.8rem; /* Padding nos links */
                font-weight: 500;
                border-radius: 0.375rem; /* Bordas arredondadas */
                transition: background-color 0.2s, color 0.2s;
            }
            .main-nav ul li a:hover {
                background-color: var(--nav-hover-color);
                color: var(--primary-color);
            }
            .main-nav ul li a.active {
                background-color: var(--primary-color);
                color: white;
                font-weight: 600;
            }
            /* Botão de Logout */
            .logout-btn {
                background-color: #f8fafc; /* Fundo claro */
                color: var(--primary-color);
                border: 1px solid var(--primary-color);
                padding: 0.5rem 1rem;
                border-radius: 0.375rem;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.2s;
                white-space: nowrap; /* Impede quebra de linha */
            }
            .logout-btn:hover {
                background-color: var(--primary-color);
                color: white;
            }

            /* --- Rodapé (Footer) --- */
            .main-footer {
                background-color: #e5e7eb; /* Cinza um pouco mais escuro */
                padding: 1rem 2rem;
                text-align: center;
                color: #4b5563; /* Cor do texto do rodapé */
                font-size: 0.85rem;
                margin-top: 2rem; /* Espaço acima do rodapé */
            }

            /* --- Estilos Comuns para Componentes (Reutilizáveis) --- */
            /* Cards */
            .card {
                background-color: white;
                border-radius: 0.5rem;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05), 0 2px 4px rgba(0,0,0,0.05);
                margin-bottom: 1.5rem;
                overflow: hidden; /* Para conter elementos internos */
            }
             .card .card-header, .card [role=heading] { /* Suporte a header e heading role */
                 padding: 1rem 1.5rem;
                 background-color: #f9fafb; /* Fundo levemente cinza */
                 border-bottom: 1px solid var(--border-color);
                 margin: 0; /* Remove margens padrão de Hx */
                 font-size: 1.1rem;
                 font-weight: 600;
             }
             .card .card-body {
                 padding: 1.5rem;
             }
             .card .card-footer {
                 padding: 1rem 1.5rem;
                 background-color: #f9fafb;
                 border-top: 1px solid var(--border-color);
             }

             /* Botões */
            .btn {
                display: inline-block;
                background-color: var(--primary-color);
                color: white;
                padding: 0.6rem 1.2rem; /* Padding padrão */
                border-radius: 0.375rem;
                text-decoration: none;
                font-weight: 500;
                border: none;
                cursor: pointer;
                transition: background-color 0.2s, transform 0.1s;
                text-align: center;
                line-height: 1.2; /* Ajuste para alinhamento vertical */
            }
            .btn:hover {
                background-color: var(--secondary-color);
                transform: translateY(-1px); /* Leve efeito ao passar o mouse */
            }
            .btn-secondary { background-color: #6b7280; }
            .btn-secondary:hover { background-color: #4b5563; }
            .btn-danger { background-color: var(--error-color); }
            .btn-danger:hover { background-color: #dc2626; }
            .btn-primary { background-color: var(--primary-color); }
            .btn-primary:hover { background-color: var(--secondary-color); }

             /* Formulários */
            .form-group { margin-bottom: 1.25rem; }
            .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #374151; }
            .form-group input, .form-group select, .form-group textarea {
                 width: 100%; padding: 0.6rem 0.75rem; border: 1px solid #d1d5db;
                 border-radius: 0.375rem; box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
                 box-sizing: border-box; font-size: 1rem; line-height: 1.5;
             }
             .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
                  border-color: var(--primary-color, #2563eb); outline: none;
                  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
             }
            .form-group .btn-secondary { margin-left: 1rem; }

            /* Alertas */
            .alert { padding: 1rem; border-radius: 0.375rem; margin-bottom: 1.5rem; border: 1px solid transparent; }
            .alert-success { background-color: #d1fae5; color: #065f46; border-color: #a7f3d0; }
            .alert-error { background-color: #fee2e2; color: #b91c1c; border-color: #fecaca; }
            .alert-warning { background-color: #fffbeb; color: #92400e; border-color: #fef3c7; }
            .alert-info { background-color: #dbeafe; color: #1e40af; border-color: #bfdbfe; }

             /* Tabela - Estilos básicos */
            table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
            table th, table td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid var(--border-color); }
            table th { background-color: #f9fafb; font-weight: 600; color: #4b5563;}
            .table-container { overflow-x: auto; } /* Permite scroll horizontal em tabelas largas */

        """)
    ]