# web/pages/health_units/list.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Table, Alert
from services.health_units_service import HealthUnitsService
from services.auth_service import AuthService

async def health_units_list_page(request):
    """Renderiza a página de listagem de unidades de saúde"""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_id = session.get('user_id')
    user_profile = session.get('user_profile')
    
    # Verifica se o usuário pode gerenciar unidades de saúde
    can_manage = AuthService.is_admin(user_profile)
    
    # Obtém a lista de unidades de saúde
    result = await HealthUnitsService.get_health_units(token)
    
    content = []
    
    # Adiciona notificação caso haja uma mensagem na sessão
    if 'message' in session:
        message = session.pop('message')
        message_type = session.pop('message_type', 'success')
        content.append(Alert(message, type=message_type))
    
    # Cabeçalho da página
    content.append(
        Div(
            H1("Health Units Management"),
            Div(
                A("Add Health Unit", href="/health-units/add", cls="btn"),
                cls="actions"
            ) if can_manage else "",
            cls="page-header"
        )
    )
    
    # Conteúdo principal
    if result["success"]:
        health_units = result["health_units"]
        
        if health_units:
            # Prepara as linhas da tabela
            rows = []
            for unit in health_units:
                # Adiciona células na linha para cada propriedade da unidade
                cells = [
                    Td(unit.get("name", "")),
                    Td(unit.get("cnpj", "")),
                    Td(unit.get("status", "").capitalize()),
                    Td(unit.get("created_at", "").split("T")[0] if isinstance(unit.get("created_at", ""), str) else "")
                ]
                
                # Adiciona botões de ação
                if can_manage:
                    # Para administradores comuns, verifica se é o dono da unidade
                    can_edit = user_profile == "general_administrator" or unit.get("admin_id") == user_id
                    
                    actions = Td(
                        A("Edit", href=f"/health-units/edit/{unit['id']}", cls="btn-sm") if can_edit else "",
                        " " if can_edit else "",
                        A("Delete", href=f"/health-units/delete/{unit['id']}", 
                          cls="btn-sm btn-danger",
                          hx_confirm="Are you sure you want to delete this health unit?") if can_edit else "",
                    )
                    cells.append(actions)
                
                rows.append(Tr(*cells))
            
            # Define as colunas da tabela
            headers = ["Name", "CNPJ", "Status", "Created At"]
            if can_manage:
                headers.append("Actions")
            
            content.append(
                Card(
                    Table(headers, rows),
                    title="Health Units List"
                )
            )
        else:
            content.append(
                Card(
                    P("No health units found.", cls="no-data"),
                    title="Health Units List"
                )
            )
    else:
        content.append(
            Card(
                Alert(result.get("message", "Error loading health units"), type="error"),
                title="Health Units List"
            )
        )
    
    # Adiciona CSS específico da página
    content.append(
        Style("""
            .actions {
                display: flex;
                justify-content: flex-end;
            }
            .page-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }
            .btn-sm {
                padding: 0.25rem 0.5rem;
                font-size: 0.875rem;
            }
            .no-data {
                text-align: center;
                padding: 2rem;
                color: #6b7280;
            }
        """)
    )
    
    # Renderiza o layout principal com o conteúdo da lista de unidades
    return MainLayout("Health Units", *content, active_page="health-units")