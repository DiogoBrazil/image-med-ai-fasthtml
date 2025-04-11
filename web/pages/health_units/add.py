# web/pages/health_units/add.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Alert
from components.forms import HealthUnitForm
from services.health_units_service import HealthUnitsService
from services.auth_service import AuthService

async def add_health_unit_page(request):
    """Renderiza a página para adicionar uma nova unidade de saúde"""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_id = session.get('user_id')
    user_profile = session.get('user_profile')
    
    # Verifica se o usuário é um administrador, pois apenas administradores podem adicionar unidades
    if not AuthService.is_admin(user_profile):
        session['message'] = "Only administrators can add health units"
        session['message_type'] = "error"
        return RedirectResponse('/health-units', status_code=303)
    
    error_message = None
    
    # Processa o formulário no POST
    if request.method == "POST":
        form_data = await request.form()
        
        # Prepara os dados da unidade de saúde
        unit_data = {
            "name": form_data.get("name"),
            "cnpj": form_data.get("cnpj"),
            "status": form_data.get("status", "active"),
            "admin_id": user_id if user_profile == "administrator" else form_data.get("admin_id")
        }
        
        # Valida campos obrigatórios
        if not all([unit_data["name"], unit_data["cnpj"]]):
            error_message = "Name and CNPJ are required"
        else:
            # Envia para a API
            result = await HealthUnitsService.create_health_unit(token, unit_data)
            
            if result.get("success", False):
                session['message'] = "Health unit added successfully"
                session['message_type'] = "success"
                return RedirectResponse('/health-units', status_code=303)
            else:
                error_message = result.get("message", "Error adding health unit")
    
    # Conteúdo da página
    content = [
        Div(
            H1("Add New Health Unit"),
            cls="page-header"
        )
    ]
    
    if error_message:
        content.append(Alert(error_message, type="error"))
    
    # Formulário para adicionar unidade de saúde
    form = HealthUnitForm(
        action="/health-units/add",
        admin_id=user_id if user_profile == "administrator" else None
    )
    
    content.append(
        Card(
            form,
            title="Health Unit Information"
        )
    )
    
    # Orientações para adicionar uma unidade de saúde
    content.append(
        Card(
            Div(
                H3("Guidelines for Adding Health Units"),
                P("When adding a new health unit, please ensure that:"),
                Ul(
                    Li("The name is complete and matches the official registration"),
                    Li("The CNPJ number is valid and correctly formatted (XX.XXX.XXX/XXXX-XX)"),
                    Li("The unit has proper operating licenses and meets regulatory requirements")
                ),
                P("Once added, healthcare professionals can be assigned to this unit and begin registering medical attendances."),
                cls="guidelines"
            ),
            cls="info-card"
        )
    )
    
    # CSS específico para esta página
    content.append(
        Style("""
            .page-header {
                margin-bottom: 1.5rem;
            }
            .info-card {
                margin-top: 1.5rem;
                background-color: #f8fafc;
            }
            .guidelines {
                padding: 0.5rem 0;
            }
            .guidelines ul {
                margin-left: 1.5rem;
                margin-top: 0.5rem;
                margin-bottom: 0.5rem;
            }
            .guidelines li {
                margin-bottom: 0.5rem;
            }
        """)
    )
    
    # Renderiza o layout principal com o formulário
    return MainLayout("Add Health Unit", *content, active_page="health-units")