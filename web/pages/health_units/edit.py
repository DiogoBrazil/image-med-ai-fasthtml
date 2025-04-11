# web/pages/health_units/edit.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Alert
from components.forms import HealthUnitForm
from services.health_units_service import HealthUnitsService
from services.auth_service import AuthService

async def edit_health_unit_page(request):
    """Renderiza a página para editar uma unidade de saúde existente"""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_id = session.get('user_id')
    user_profile = session.get('user_profile')
    
    # Obtém o ID da unidade de saúde a ser editada da URL
    path_params = request.path_params
    unit_id = path_params.get('unit_id')
    
    if not unit_id:
        session['message'] = "Health unit ID is missing"
        session['message_type'] = "error"
        return RedirectResponse('/health-units', status_code=303)
    
    # Verifica se o usuário é um administrador, pois apenas administradores podem editar unidades
    if not AuthService.is_admin(user_profile):
        session['message'] = "Only administrators can edit health units"
        session['message_type'] = "error"
        return RedirectResponse('/health-units', status_code=303)
    
    # Obtém os dados da unidade de saúde a ser editada
    unit_result = await HealthUnitsService.get_health_unit_by_id(token, unit_id)
    
    if not unit_result["success"]:
        session['message'] = unit_result.get("message", "Health unit not found")
        session['message_type'] = "error"
        return RedirectResponse('/health-units', status_code=303)
    
    health_unit = unit_result["health_unit"]
    
    # Verifica se o administrador comum (não super) pode editar esta unidade
    if user_profile == "administrator" and health_unit.get("admin_id") != user_id:
        session['message'] = "You can only edit your own health units"
        session['message_type'] = "error"
        return RedirectResponse('/health-units', status_code=303)
    
    error_message = None
    
    # Processa o formulário no POST
    if request.method == "POST":
        form_data = await request.form()
        
        # Prepara os dados atualizados da unidade de saúde
        unit_data = {
            "name": form_data.get("name"),
            "cnpj": form_data.get("cnpj"),
            "status": form_data.get("status", "active"),
            "admin_id": health_unit.get("admin_id")  # Mantém o mesmo admin_id
        }
        
        # Valida campos obrigatórios
        if not all([unit_data["name"], unit_data["cnpj"]]):
            error_message = "Name and CNPJ are required"
        else:
            # Envia para a API
            result = await HealthUnitsService.update_health_unit(token, unit_id, unit_data)
            
            if result.get("success", False):
                session['message'] = "Health unit updated successfully"
                session['message_type'] = "success"
                return RedirectResponse('/health-units', status_code=303)
            else:
                error_message = result.get("message", "Error updating health unit")
    
    # Conteúdo da página
    content = [
        Div(
            H1(f"Edit Health Unit: {health_unit.get('name')}"),
            cls="page-header"
        )
    ]
    
    if error_message:
        content.append(Alert(error_message, type="error"))
    
    # Formulário para editar unidade de saúde
    form = HealthUnitForm(
        action=f"/health-units/edit/{unit_id}",
        unit=health_unit,
        admin_id=health_unit.get("admin_id")
    )
    
    content.append(
        Card(
            form,
            title="Health Unit Information"
        )
    )
    
    # CSS específico para esta página
    content.append(
        Style("""
            .page-header {
                margin-bottom: 1.5rem;
            }
        """)
    )
    
    # Renderiza o layout principal com o formulário
    return MainLayout("Edit Health Unit", *content, active_page="health-units")