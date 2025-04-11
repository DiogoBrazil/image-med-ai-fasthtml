# web/pages/attendances/view.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Alert
from services.attendance_service import AttendanceService
from services.users_service import UsersService
from services.health_units_service import HealthUnitsService
from services.auth_service import AuthService
from datetime import datetime

async def view_attendance_page(request):
    """Renderiza a página de visualização detalhada de um atendimento médico"""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_id = session.get('user_id')
    user_profile = session.get('user_profile')
    
    # Obtém o ID do atendimento da URL
    path_params = request.path_params
    attendance_id = path_params.get('attendance_id')
    
    if not attendance_id:
        session['message'] = "Attendance ID is missing"
        session['message_type'] = "error"
        return RedirectResponse('/attendances', status_code=303)
    
    # Obtém os dados completos do atendimento, incluindo a imagem
    attendance_result = await AttendanceService.get_attendance_by_id(token, attendance_id, include_image=True)
    
    if not attendance_result["success"]:
        session['message'] = attendance_result.get("message", "Attendance not found")
        session['message_type'] = "error"
        return RedirectResponse('/attendances', status_code=303)
    
    attendance = attendance_result["attendance"]
    
    # Obtém informações adicionais: profissional e unidade de saúde
    professional_result = await UsersService.get_user_by_id(token, attendance.get("professional_id", ""))
    professional = professional_result.get("user", {}) if professional_result.get("success", False) else {}
    
    health_unit_result = await HealthUnitsService.get_health_unit_by_id(token, attendance.get("health_unit_id", ""))
    health_unit = health_unit_result.get("health_unit", {}) if health_unit_result.get("success", False) else {}
    
    # Verifica permissões para editar e excluir
    can_edit = AuthService.is_admin(user_profile) or attendance.get("professional_id") == user_id
    can_delete = can_edit
    
    # Formata a data do atendimento
    attendance_date = attendance.get("attendance_date", "")
    formatted_date = attendance_date
    if attendance_date and isinstance(attendance_date, str):
        try:
            date_obj = datetime.fromisoformat(attendance_date.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime("%d/%m/%Y %H:%M:%S")
        except:
            pass
    
    # Conteúdo da página
    content = [
        Div(
            H1("Attendance Details"),
            Div(
                A("Back to List", href="/attendances", cls="btn btn-secondary"),
                A("Edit", href=f"/attendances/edit/{attendance_id}", cls="btn") if can_edit else "",
                A("Delete", 
                  href=f"/attendances/delete/{attendance_id}", 
                  cls="btn btn-danger",
                  hx_confirm="Are you sure you want to delete this attendance record?") if can_delete else "",
                cls="page-actions"
            ),
            cls="page-header"
        )
    ]
    
    # Cartão com informações básicas
    content.append(
        Card(
            Div(
                Div(
                    P(Strong("Date: "), formatted_date),
                    P(Strong("Professional: "), professional.get("full_name", attendance.get("professional_id", ""))),
                    P(Strong("Health Unit: "), health_unit.get("name", attendance.get("health_unit_id", ""))),
                    cls="basic-info"
                ),
                
                Div(
                    P(Strong("AI Model: "), attendance.get("model_used", "").capitalize()),
                    P(Strong("Diagnosis Result: "), attendance.get("model_result", "Pending")),
                    P(Strong("Expected Result: "), attendance.get("expected_result", "Not provided")),
                    P(
                        Strong("Diagnosis Correctness: "), 
                        Span(
                            "Correct" if attendance.get("correct_diagnosis") else "Incorrect",
                            cls=f"badge {'badge-success' if attendance.get('correct_diagnosis') else 'badge-error'}"
                        )
                    ),
                    cls="diagnosis-info"
                ),
                
                cls="info-container"
            ),
            title="Attendance Information"
        )
    )
    
    # Cartão com a imagem médica
    content.append(
        Card(
            Div(
                Img(
                    src=f"data:image/png;base64,{attendance.get('image_base64', '')}",
                    alt="Medical image",
                    cls="medical-image"
                ),
                cls="image-container"
            ),
            title="Medical Image"
        )
    )
    
    # Se houver bounding boxes (para modelo de mama), exibe-os
    if attendance.get("model_used") == "breast" and "bounding_boxes" in attendance:
        bounding_boxes = attendance.get("bounding_boxes", [])
        
        if bounding_boxes:
            boxes_content = [
                H3("Detected Anomalies"),
                P("The AI model detected the following regions of interest:"),
                Ul(*[
                    Li(
                        P(f"Region {i+1}:"),
                        P(f"Position: X={box.get('x')}, Y={box.get('y')}"),
                        P(f"Size: Width={box.get('width')}, Height={box.get('height')}"),
                        P(f"Confidence: {box.get('confidence', 0) * 100:.1f}%"),
                        P(f"Observations: {box.get('observations', 'None')}"),
                    )
                    for i, box in enumerate(bounding_boxes)
                ]),
            ]
            
            content.append(
                Card(
                    Div(*boxes_content, cls="bounding-boxes-info"),
                    title="Anomaly Detection"
                )
            )
    
    # Cartão com observações
    if attendance.get("observations"):
        content.append(
            Card(
                Div(
                    P(attendance.get("observations", "")),
                    cls="observations-text"
                ),
                title="Professional Observations"
            )
        )
    
    # CSS específico para esta página
    content.append(
        Style("""
            .page-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }
            .page-actions {
                display: flex;
                gap: 0.5rem;
            }
            .info-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
            }
            .basic-info, .diagnosis-info {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            .image-container {
                display: flex;
                justify-content: center;
                padding: 1rem;
                background-color: #f8f9fa;
                border-radius: 0.25rem;
            }
            .medical-image {
                max-width: 100%;
                max-height: 500px;
                object-fit: contain;
            }
            .badge {
                display: inline-block;
                padding: 0.25rem 0.5rem;
                border-radius: 0.25rem;
                font-weight: 500;
                font-size: 0.875rem;
            }
            .badge-success {
                background-color: #d1fae5;
                color: #065f46;
            }
            .badge-error {
                background-color: #fee2e2;
                color: #b91c1c;
            }
            .bounding-boxes-info ul {
                margin-left: 1.5rem;
                margin-top: 1rem;
            }
            .bounding-boxes-info li {
                margin-bottom: 1.5rem;
                padding: 1rem;
                background-color: #f8f9fa;
                border-radius: 0.25rem;
            }
            .observations-text {
                white-space: pre-line;
                line-height: 1.6;
            }
        """)
    )
    
    # Renderiza o layout principal com o conteúdo detalhado do atendimento
    return MainLayout("View Attendance", *content, active_page="attendances")