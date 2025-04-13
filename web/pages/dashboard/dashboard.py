# web/pages/dashboard/dashboard.py
from fasthtml.common import *
# Importações corrigidas/adicionadas
from components.layout import MainLayout
from components.ui import Card, Alert # Importa Alert junto com Card
from services.api_client import ApiClient # Usado para buscar stats (admin)
from services.auth_service import AuthService # Para checar perfil
from datetime import datetime, timedelta # Para datas das estatísticas

async def dashboard_page(request):
    """Renderiza o dashboard principal baseado no perfil do usuário"""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_profile = session.get('user_profile')
    user_name = session.get('user_name', 'User') # Nome do usuário logado

    # Verifica os perfis
    is_admin = AuthService.is_admin(user_profile)
    is_professional = AuthService.is_professional(user_profile)

    page_title = "Dashboard"
    content = []
    api_error = None # Variável para armazenar erros da API

    # Cabeçalho de boas-vindas
    content.append(
         Header(
            H1(f"Welcome, {user_name}!"),
            P(f"Your main dashboard."),
            cls="dashboard-header"
        )
    )

    # --- Conteúdo Condicional ---
    if is_admin:
        # --- Lógica para Administradores ---
        stats = {}
        model_usage = {}
        model_accuracy = {}
        try:
            client = ApiClient(token) # Cliente API com token
            today = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            # Chama o endpoint de estatísticas (verifique se o path está correto no serviço/cliente)
            stats_response = await client.get(
                f"/attendances/statistics/summary/?start_date={start_date}&end_date={today}"
            )
            # Verifica se a resposta foi bem sucedida (status_code pode variar)
            if stats_response.get("detail", {}).get("status_code") in [200, 204]: # 204 se não houver dados
                 stats = stats_response.get("detail", {}).get("statistics", {})
                 model_usage = stats.get("model_usage", {})
                 model_accuracy = stats.get("model_accuracy", {})
                 if stats_response.get("detail", {}).get("status_code") == 204:
                     # Guarda uma mensagem informativa se não houver dados
                     api_error = stats_response.get("detail", {}).get("message", "No statistics data found for the period.")
            else:
                 # Guarda a mensagem de erro da API
                 api_error = stats_response.get("detail", {}).get("message", "Could not load statistics.")

        except Exception as e:
            # Captura erros de conexão ou outros
            api_error = f"Error loading statistics: {e}"
            print(f"Dashboard API Error: {e}") # Log

        # Exibe Alerta de erro/informativo se houver
        if api_error:
             # Agora 'Alert' está definido e pode ser usado
             alert_type = "warning" if "No statistics data found" in api_error else "error"
             content.append(Alert(api_error, type=alert_type))

        # Card de Uso por Modelo
        usage_card_content = [H3("Total Attendances (Last 30 Days)")]
        if model_usage:
            total_attendances = sum(model_usage.values())
            usage_by_model = [P(f"{model.capitalize()}: {count}") for model, count in model_usage.items()]
            usage_card_content.extend([
                P(Span(str(total_attendances), cls="stat-number"), cls="stat-main"),
                *usage_by_model
            ])
        else:
             usage_card_content.append(P("No usage data available."))
        content.append(Div(Card(*usage_card_content, cls="dashboard-card"), cls="grid-item")) # Adiciona ao grid

        # Card de Precisão do Modelo
        accuracy_card_content = [H3("Model Accuracy (Last 30 Days)")]
        if model_accuracy:
            accuracy_items = []
            for model, data in model_accuracy.items():
                accuracy = data.get("accuracy_percentage", 0)
                accuracy_items.append(P(
                    f"{model.capitalize()}: {accuracy}% "
                    f"({data.get('correct', 0)}/{data.get('total', 0)})"
                ))
            accuracy_card_content.extend(accuracy_items if accuracy_items else P("No accuracy data available."))
        else:
             accuracy_card_content.append(P("No accuracy data available."))
        content.append(Div(Card(*accuracy_card_content, cls="dashboard-card"), cls="grid-item")) # Adiciona ao grid

    elif is_professional:
        # --- Lógica para Profissionais ---
        page_title = "Start New Prediction"
        prediction_options = [
            {"id": "respiratory", "name": "Respiratory Diseases", "icon": "lungs", "desc": "Analyze chest X-rays."},
            {"id": "tuberculosis", "name": "Tuberculosis", "icon": "virus", "desc": "Detect Tuberculosis in X-rays."},
            {"id": "osteoporosis", "name": "Osteoporosis", "icon": "bone", "desc": "Analyze bone density scans."},
            {"id": "breast-cancer", "name": "Breast Cancer", "icon": "ribbon", "desc": "Analyze mammograms."}
        ]

        prediction_cards = []
        for option in prediction_options:
            # Você pode adicionar SVGs reais aqui se quiser
            icon_placeholder = Span(f"🩺", style="font-size: 2.5rem; margin-bottom: 0.5rem; display: block;")
            prediction_cards.append(
                A( # Card clicável
                    Card(
                        icon_placeholder,
                        H3(option["name"]),
                        P(option["desc"], cls="card-description"),
                        cls="prediction-card"
                    ),
                    href=f"/predict/{option['id']}" # Link para a página de predição
                )
            )
        # Adiciona os cards ao conteúdo dentro de um container grid
        content.append(Div(*prediction_cards, cls="dashboard-grid"))

    else:
        # Caso para outros perfis ou se não for admin/profissional
        content.append(P("Welcome! Select an option from the menu."))

    # Adiciona CSS
    content.append(
        Style("""
            .dashboard-header { margin-bottom: 2rem; }
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                gap: 1.5rem;
            }
            .grid-item { /* Para garantir que os cards de admin fiquem no grid */
                 /* Nenhum estilo específico necessário se o card já estiver ok */
            }
            .dashboard-card { /* Estilo para cards de admin (stats) */
                min-height: 180px;
                display: flex;
                flex-direction: column;
                background-color: white; /* Garante fundo branco */
                padding: 1.5rem; /* Padding interno */
                border-radius: 0.5rem; /* Bordas arredondadas */
                box-shadow: 0 1px 3px rgba(0,0,0,0.1); /* Sombra */
            }
             .dashboard-card h3 {
                 margin-top: 0; /* Remove margem do título */
                 margin-bottom: 1rem;
                 font-size: 1.1rem;
                 color: #4b5563; /* Cor do título */
             }
            .stat-number { font-size: 2.2rem; font-weight: bold; color: var(--primary-color, #2563eb); }
            .stat-main { margin-bottom: 1rem; }
            .prediction-card { /* Estilo para cards de profissional (links) */
                text-align: center;
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                 background-color: white; /* Garante fundo branco */
                 padding: 2rem 1.5rem; /* Mais padding */
                 border-radius: 0.5rem;
                 box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .prediction-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1); /* Sombra maior no hover */
            }
            .prediction-card h3 {
                 margin-top: 0.5rem;
                 color: var(--primary-color, #2563eb);
                 font-size: 1.2rem;
            }
            .card-description {
                font-size: 0.9rem;
                color: #6b7280;
                margin-top: 0.5rem;
                 line-height: 1.4;
            }
            .dashboard-grid a { /* Remove sublinhado dos cards clicáveis */
                 text-decoration: none;
                 color: inherit;
            }
        """)
    )

    # Renderiza o layout principal, passando o perfil para a navegação condicional
    return MainLayout(page_title, *content, active_page="dashboard", user_profile=user_profile)