# web/pages/attendances/add.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Alert
from components.forms import AttendanceForm
from services.attendance_service import AttendanceService
from services.health_units_service import HealthUnitsService
from services.auth_service import AuthService
import base64

async def add_attendance_page(request):
    """Renderiza a página para adicionar um novo atendimento médico com diagnóstico"""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_id = session.get('user_id')
    user_profile = session.get('user_profile')
    
    # Verifica se o usuário é um profissional, pois apenas profissionais podem registrar atendimentos
    if not AuthService.is_professional(user_profile):
        session['message'] = "Only healthcare professionals can register attendances"
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
    
    if not health_units:
        error_message = "No health units available. Please contact your administrator."
    
    # Processa o formulário no POST
    if request.method == "POST":
        form = await request.form()
        
        # Valida campos obrigatórios
        if not all([form.get("health_unit_id"), form.get("model_used")]):
            error_message = "Health unit and AI model are required"
        else:
            try:
                # Processa o arquivo de imagem (se enviado)
                image = form.get("image_base64")
                image_base64 = None
                
                if image and hasattr(image, "file"):
                    # Lê o arquivo e converte para base64
                    contents = await image.read()
                    if contents:
                        image_base64 = base64.b64encode(contents).decode("utf-8")
                    else:
                        error_message = "Empty image file"
                
                if not error_message and not image_base64:
                    error_message = "Medical image is required"
                
                if not error_message:
                    # Prepara os dados do atendimento
                    attendance_data = {
                        "professional_id": user_id,
                        "health_unit_id": form.get("health_unit_id"),
                        "admin_id": session.get("admin_id", ""),  # Pode ser obtido do token
                        "model_used": form.get("model_used"),
                        "model_result": "",  # Será preenchido pela API após processar a imagem
                        "expected_result": form.get("expected_result", ""),
                        "correct_diagnosis": False,  # Será atualizado após o diagnóstico
                        "image_base64": image_base64,
                        "observation": form.get("observation", "")
                    }
                    
                    # Envia para a API
                    result = await AttendanceService.create_attendance(token, attendance_data)
                    
                    if result.get("success", False):
                        session['message'] = "Attendance record created successfully"
                        session['message_type'] = "success"
                        return RedirectResponse('/attendances', status_code=303)
                    else:
                        error_message = result.get("message", "Error creating attendance record")
            
            except Exception as e:
                error_message = f"Error processing form: {str(e)}"
    
    # Conteúdo da página
    content = [
        Div(
            H1("New Medical Attendance"),
            cls="page-header"
        )
    ]
    
    if error_message:
        content.append(Alert(error_message, type="error"))
    
    # Formulário para adicionar atendimento
    form = AttendanceForm(
        action="/attendances/add",
        models=models,
        health_units=health_units,
        professional_id=user_id,
        admin_id=session.get("admin_id")
    )
    
    content.append(
        Card(
            form,
            title="Attendance Information"
        )
    )
    
    # Informações adicionais para o usuário
    content.append(
        Card(
            Div(
                H3("Instructions"),
                P("Upload a medical image for AI diagnosis. The system supports the following types of images:"),
                Ul(
                    Li("Respiratory: X-rays of lungs and chest"),
                    Li("Tuberculosis: Chest X-rays"),
                    Li("Osteoporosis: Bone density scans"),
                    Li("Breast Cancer: Mammograms")
                ),
                P("For accurate results, please ensure the image is clear and properly oriented."),
                cls="instructions"
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
            .instructions {
                padding: 0.5rem 0;
            }
            .instructions ul {
                margin-left: 1.5rem;
            }
        """)
    )
    
    # Renderiza o layout principal com o formulário
    return MainLayout("Add Attendance", *content, active_page="attendances")