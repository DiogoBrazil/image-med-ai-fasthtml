# web/pages/attendances/list.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Table, Alert, Pagination
from services.attendance_service import AttendanceService
from services.health_units_service import HealthUnitsService
from services.auth_service import AuthService

async def attendances_list_page(request):
    """Renderiza a página de listagem de atendimentos médicos"""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_id = session.get('user_id')
    user_profile = session.get('user_profile')
    
    # Obtém parâmetros da query string
    query_params = request.query_params
    page = int(query_params.get('page', '1'))
    per_page = int(query_params.get('per_page', '10'))
    health_unit_id = query_params.get('health_unit_id')
    model_used = query_params.get('model_used')
    
    # Verifica se o usuário tem permissão para ver atendimentos
    can_add = AuthService.is_professional(user_profile)
    
    # Obtém unidades de saúde para o filtro (se for administrador)
    health_units = []
    if AuthService.is_admin(user_profile):
        health_units_result = await HealthUnitsService.get_health_units(token)
        if health_units_result.get("success", False):
            health_units = health_units_result.get("health_units", [])
    
    # Obtém a lista de atendimentos
    attendance_result = await AttendanceService.get_attendances(
        token, health_unit_id, model_used, page, per_page
    )
    
    content = []
    
    # Adiciona notificação caso haja uma mensagem na sessão
    if 'message' in session:
        message = session.pop('message')
        message_type = session.pop('message_type', 'success')
        content.append(Alert(message, type=message_type))
    
    # Cabeçalho da página com filtros
    content.append(
        Div(
            H1("Medical Attendances"),
            Div(
                A("New Attendance", href="/attendances/add", cls="btn") if can_add else "",
                cls="actions"
            ),
            cls="page-header"
        )
    )
    
    # Seção de filtros
    filter_form = None
    if health_units:
        filter_form = Form(
            Div(
                Div(
                    Label("Health Unit", For="health_unit_id"),
                    Select(
                        Option("All Health Units", value=""),
                        *[Option(unit["name"], value=unit["id"], 
                                selected=health_unit_id == unit["id"]) 
                          for unit in health_units],
                        id="health_unit_id", name="health_unit_id"
                    ),
                    cls="form-group"
                ),
                Div(
                    Label("AI Model", For="model_used"),
                    Select(
                        Option("All Models", value=""),
                        Option("Respiratory", value="respiratory", selected=model_used == "respiratory"),
                        Option("Tuberculosis", value="tuberculosis", selected=model_used == "tuberculosis"),
                        Option("Osteoporosis", value="osteoporosis", selected=model_used == "osteoporosis"),
                        Option("Breast", value="breast", selected=model_used == "breast"),
                        id="model_used", name="model_used"
                    ),
                    cls="form-group"
                ),
                Button("Filter", type="submit", cls="btn"),
                cls="filter-inputs"
            ),
            method="get",
            action="/attendances",
            cls="filter-form"
        )
    
    if filter_form:
        content.append(
            Card(
                filter_form,
                title="Filter Attendances",
                cls="filter-card"
            )
        )
    
    # Conteúdo principal
    if attendance_result.get("success", False):
        attendances = attendance_result.get("attendances", [])
        pagination = attendance_result.get("pagination", {})
        
        if attendances:
            # Prepara as linhas da tabela
            rows = []
            for attendance in attendances:
                # Formata a data de atendimento para exibição
                attendance_date = attendance.get("attendance_date", "")
                if attendance_date and isinstance(attendance_date, str):
                    # Considera que o formato da data é ISO: YYYY-MM-DDTHH:MM:SS
                    try:
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(attendance_date.replace('Z', '+00:00'))
                        attendance_date = date_obj.strftime("%d/%m/%Y %H:%M")
                    except:
                        pass
                
                # Prepara a exibição do resultado do diagnóstico
                model_result = attendance.get("model_result", "Pending")
                correct_diagnosis = attendance.get("correct_diagnosis")
                
                diagnosis_display = model_result
                if correct_diagnosis is not None:
                    diagnosis_class = "diagnosis-correct" if correct_diagnosis else "diagnosis-incorrect"
                    diagnosis_display = Span(model_result, cls=diagnosis_class)
                
                # Prepara a exibição da unidade de saúde
                health_unit_id = attendance.get("health_unit_id", "")
                health_unit_name = next((unit["name"] for unit in health_units if unit["id"] == health_unit_id), health_unit_id)
                
                # Adiciona células na linha para cada propriedade do atendimento
                cells = [
                    Td(attendance_date),
                    Td(health_unit_name),
                    Td(attendance.get("model_used", "").capitalize()),
                    Td(diagnosis_display),
                ]
                
                # Adiciona botões de ação
                actions = Td(
                    A("View", href=f"/attendances/view/{attendance['id']}", cls="btn-sm"),
                    " ",
                    A("Edit", href=f"/attendances/edit/{attendance['id']}", cls="btn-sm"),
                    " ",
                    A("Delete", href=f"/attendances/delete/{attendance['id']}", 
                      cls="btn-sm btn-danger",
                      hx_confirm="Are you sure you want to delete this attendance record?"),
                )
                cells.append(actions)
                
                rows.append(Tr(*cells))
            
            # Define as colunas da tabela
            headers = ["Date", "Health Unit", "AI Model", "Diagnosis", "Actions"]
            
            content.append(
                Card(
                    Div(
                        Table(headers, rows),
                        Pagination(
                            page=pagination.get("current_page", 1),
                            total_pages=pagination.get("total_pages", 1),
                            base_url="/attendances"
                        ) if pagination else "",
                        cls="table-container"
                    ),
                    title=f"Attendance Records ({pagination.get('total_count', 0)})"
                )
            )
        else:
            content.append(
                Card(
                    P("No attendance records found. Please adjust your filters or add a new record.", cls="no-data"),
                    title="Attendance Records"
                )
            )
    else:
        content.append(
            Card(
                Alert(attendance_result.get("message", "Error loading attendance records"), type="error"),
                title="Attendance Records"
            )
        )
    
    # Adiciona CSS específico da página
    content.append(
        Style("""
            .page-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }
            .filter-card {
                margin-bottom: 1.5rem;
            }
            .filter-inputs {
                display: flex;
                flex-wrap: wrap;
                gap: 1rem;
                align-items: flex-end;
            }
            .filter-inputs .form-group {
                flex: 1;
                min-width: 200px;
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
            .diagnosis-correct {
                color: #047857;
                font-weight: 500;
            }
            .diagnosis-incorrect {
                color: #b91c1c;
                font-weight: 500;
            }
            .table-container {
                overflow-x: auto;
            }
        """)
    )
    
    # Renderiza o layout principal com o conteúdo da lista de atendimentos
    return MainLayout("Attendances", *content, active_page="attendances")