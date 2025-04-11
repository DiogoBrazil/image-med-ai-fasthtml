# web/pages/attendances/edit.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Alert
from components.forms import AttendanceForm
from services.attendance_service import AttendanceService
from services.health_units_service import HealthUnitsService
from services.auth_service import AuthService
import base64

async def edit_attendance_page(request):
    """Renderiza a página para editar um atendimento médico existente"""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_id = session.get('user_id')
    user_profile = session.get('user_profile')
    
    # Obtém o ID do atendimento a ser editado da URL
    path_params = request.path_params
    attendance_id = path_params.get('attendance_id')
    
    if not attendance_id:
        session['message'] = "Attendance ID is missing"
        session['message_type'] = "error"
        return RedirectResponse('/attendances', status_code=303)
    
    # Obtém os dados do atendimento a ser editado
    # Incluindo a imagem base64 completa
    attendance_result = await AttendanceService.get_attendance_by_id(token, attendance_id, include_image=True)
    
    if not attendance_result["success"]:
        session['message'] = attendance_result.get("message", "Attendance not found")
        session['message_type'] = "error"
        return RedirectResponse('/attendances', status_code=303)
    
    attendance = attendance_result["attendance"]
    
    # Verifica se o usuário tem permissão para editar este atendimento
    if not AuthService.is_admin(user_profile) and attendance.get("professional_id") != user_id:
        session['message'] = "You don't have permission to edit this attendance record"
        session['message_type'] = "error"
        return RedirectResponse('/attendances', status_code=303)
    
    error_message = None
    
    # Lista de modelos de IA disponíveis
    models = [
        {"id": "respiratory", "name": "Respiratory Diseases"},
        {"id": "tuberculosis", "name": "Tuberculosis"},
        {"id": "osteoporosis", "name": "Osteoporosis"},
        {"id": "breast", "name": "Breast Cancer"}
    ]
    
    # Obtém unidades de saúde disponíveis
    health_units_result = await HealthUnitsService.get_health_units(token)
    health_units = health_units_result.get("health_units", []) if health_units_result.get("success", False) else []
    
    # Processa o formulário no POST
    if request.method == "POST":
        form = await request.form()
        
        # Valida campos obrigatórios
        if not all([form.get("health_unit_id"), form.get("model_used")]):
            error_message = "Health unit and AI model are required"
        else:
            try:
                # Processa o arquivo de imagem (apenas se um novo for enviado)
                image = form.get("image_base64")
                image_base64 = None
                
                if image and hasattr(image, "file") and await image.read():
                    # Volta o ponteiro do arquivo para o início para ler novamente
                    await image.seek(0)
                    # Lê o arquivo e converte para base64
                    contents = await image.read()
                    if contents:
                        image_base64 = base64.b64encode(contents).decode("utf-8")
                
                # Prepara os dados atualizados do atendimento
                attendance_data = {
                    "professional_id": attendance["professional_id"],
                    "health_unit_id": form.get("health_unit_id"),
                    "admin_id": attendance["admin_id"],
                    "model_used": form.get("model_used"),
                    "model_result": attendance["model_result"],
                    "expected_result": form.get("expected_result", ""),
                    "correct_diagnosis": form.get("correct_diagnosis") == "true", # Checkbox para confirmar diagnóstico correto
                    "observation": form.get("observation", "")
                }
                
                # Inclui a imagem apenas se uma nova foi enviada
                if image_base64:
                    attendance_data["image_base64"] = image_base64
                
                # Se o modelo for "breast", adiciona os bounding boxes
                if attendance["model_used"] == "breast" and "bounding_boxes" in attendance:
                    attendance_data["bounding_boxes"] = attendance["bounding_boxes"]
                
                # Envia para a API
                result = await AttendanceService.update_attendance(token, attendance_id, attendance_data)
                
                if result.get("success", False):
                    session['message'] = "Attendance record updated successfully"
                    session['message_type'] = "success"
                    return RedirectResponse('/attendances', status_code=303)
                else:
                    error_message = result.get("message", "Error updating attendance record")
            
            except Exception as e:
                error_message = f"Error processing form: {str(e)}"
    
    # Conteúdo da página
    content = [
        Div(
            H1("Edit Attendance Record"),
            Div(
                A("View Details", href=f"/attendances/view/{attendance_id}", cls="btn btn-secondary"),
                A("Back to List", href="/attendances", cls="btn btn-secondary", style="margin-left: 0.5rem;"),
                cls="page-actions"
            ),
            cls="page-header"
        )
    ]
    
    if error_message:
        content.append(Alert(error_message, type="error"))
    
    # Adiciona a imagem atual para visualização
    content.append(
        Card(
            Div(
                H3("Current Medical Image"),
                Div(
                    Img(
                        src=f"data:image/png;base64,{attendance['image_base64']}",
                        style="max-width: 100%; max-height: 300px;"
                    ),
                    cls="image-preview"
                ),
                cls="current-image"
            ),
            title="Image Preview"
        )
    )
    
    # Se houver resultado do modelo, exibe-o
    if attendance.get("model_result"):
        content.append(
            Card(
                Div(
                    H3("AI Diagnosis Result"),
                    P(Strong("Model: "), attendance.get("model_used", "").capitalize()),
                    P(Strong("Result: "), attendance.get("model_result", "")),
                    P(Strong("Expected Result: "), attendance.get("expected_result", "Not provided")),
                    P(
                        Strong("Diagnosis Correctness: "), 
                        Span(
                            "Correct" if attendance.get("correct_diagnosis") else "Incorrect",
                            cls=f"badge {'badge-success' if attendance.get('correct_diagnosis') else 'badge-error'}"
                        )
                    ),
                    cls="diagnosis-result"
                ),
                title="Diagnosis Information"
            )
        )
    
    # Formulário para editar atendimento
    form = AttendanceForm(
        action=f"/attendances/edit/{attendance_id}",
        models=models,
        health_units=health_units,
        attendance=attendance,
        professional_id=attendance.get("professional_id"),
        admin_id=attendance.get("admin_id")
    )
    
    content.append(
        Card(
            form,
            title="Edit Attendance Information"
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
            .current-image {
                text-align: center;
                margin-bottom: 1rem;
            }
            .image-preview {
                margin-top: 1rem;
                padding: 1rem;
                background-color: #f8f9fa;
                border-radius: 0.25rem;
                display: flex;
                justify-content: center;
            }
            .diagnosis-result {
                padding: 0.5rem 0;
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
        """)
    )
    
    # Renderiza o layout principal com o formulário
    return MainLayout("Edit Attendance", *content, active_page="attendances")