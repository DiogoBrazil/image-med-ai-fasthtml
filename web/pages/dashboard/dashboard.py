# web/pages/dashboard/dashboard.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card
from services.api_client import ApiClient
from datetime import datetime, timedelta

async def dashboard_page(request):
    """Renderiza o dashboard principal"""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_profile = session.get('user_profile')
    user_name = session.get('user_name')
    
    client = ApiClient(token)
    
    try:
        # Obtem estatísticas de atendimentos
        today = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        stats_response = await client.get(
            f"/attendances/statistics/summary?start_date={start_date}&end_date={today}"
        )
        
        stats = stats_response.get("detail", {}).get("statistics", {})
        model_usage = stats.get("model_usage", {})
        model_accuracy = stats.get("model_accuracy", {})
        
        # Prepara os cartões de estatísticas
        
        # Cartão de total de atendimentos
        total_attendances = sum(model_usage.values())
        usage_by_model = []
        for model, count in model_usage.items():
            usage_by_model.append(P(f"{model.capitalize()}: {count}"))
        
        # Cartão de precisão
        accuracy_items = []
        for model, data in model_accuracy.items():
            accuracy = data.get("accuracy_percentage", 0)
            accuracy_items.append(P(
                f"{model.capitalize()}: {accuracy}% "
                f"({data.get('correct', 0)}/{data.get('total', 0)})"
            ))
        
    except Exception as e:
        # Em caso de erro, mostra informações básicas
        total_attendances = 0
        usage_by_model = [P("Error loading usage data")]
        accuracy_items = [P("Error loading accuracy data")]
    
    # Conteúdo principal
    content = [
        Header(
            H1(f"Welcome, {user_name}"),
            P(f"Dashboard overview for the last 30 days"),
            cls="dashboard-header"
        ),
        Div(
            Card(
                H3("Total Attendances"),
                P(Span(str(total_attendances), cls="stat-number"), cls="stat-main"),
                *usage_by_model,
                cls="dashboard-card"
            ),
            Card(
                H3("Model Accuracy"),
                *accuracy_items,
                cls="dashboard-card"
            ),
            cls="dashboard-cards"
        ),
        Style("""
            .dashboard-header {
                margin-bottom: 2rem;
            }
            .dashboard-cards {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 1.5rem;
            }
            .dashboard-card {
                min-height: 180px;
            }
            .stat-number {
                font-size: 2rem;
                font-weight: bold;
                color: #2563eb;
            }
            .stat-main {
                margin-bottom: 1rem;
            }
        """)
    ]
    
    # Renderiza o layout principal com o conteúdo do dashboard
    return MainLayout("Dashboard", *content, active_page="dashboard")