# web/pages/attendances/view.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Alert, Img # Adicionado Img
from services.attendance_service import AttendanceService
from services.users_service import UsersService
from services.health_units_service import HealthUnitsService
from services.auth_service import AuthService
from datetime import datetime
import json # Para formatar o resultado

async def view_attendance_page(request):
    """Renderiza a página de visualização detalhada de um atendimento médico"""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_id = session.get('user_id')
    # *** ADICIONADO: Obter user_profile da sessão ***
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

    # --- Verifica permissão de visualização ---
    # Assume que admins podem ver tudo e profissionais podem ver os seus.
    can_view = False
    if AuthService.is_admin(user_profile):
        can_view = True
    elif AuthService.is_professional(user_profile) and attendance.get("professional_id") == user_id:
        can_view = True

    if not can_view:
         session['message'] = "You don't have permission to view this attendance record"
         session['message_type'] = "error"
         return RedirectResponse('/attendances', status_code=303)
    # ---------------------------------------


    # Obtém informações adicionais: profissional e unidade de saúde
    professional_result = await UsersService.get_user_by_id(token, attendance.get("professional_id", ""))
    professional = professional_result.get("user", {}) if professional_result.get("success", False) else {}

    health_unit_result = await HealthUnitsService.get_health_unit_by_id(token, attendance.get("health_unit_id", ""))
    health_unit = health_unit_result.get("health_unit", {}) if health_unit_result.get("success", False) else {}

    # Verifica permissões para editar e excluir (pode ser diferente da visualização)
    can_edit_delete = AuthService.is_admin(user_profile) or attendance.get("professional_id") == user_id

    # Formata a data do atendimento
    attendance_date = attendance.get("attendance_date", "")
    formatted_date = attendance_date
    if attendance_date and isinstance(attendance_date, str):
        try:
            date_obj = datetime.fromisoformat(attendance_date.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime("%d/%m/%Y %H:%M:%S")
        except:
            pass # Mantém original se der erro

    # Formata o resultado do modelo para exibição
    model_result_display = attendance.get("model_result", "N/A")
    try:
         # Tenta formatar se for JSON
         result_dict = json.loads(model_result_display) if isinstance(model_result_display, str) and model_result_display.startswith('{') else None
         if result_dict:
             # Exemplo: Formata dicionário de probabilidades (TB ou Osteo)
             if 'probabilities' in result_dict:
                 probs_str = ", ".join([f"{k}: {v:.1f}%" for k,v in result_dict['probabilities'].items()])
                 model_result_display = f"Class: {result_dict.get('class_pred', 'N/A')} ({probs_str})"
             # Exemplo: Formata resultado de detecção (Breast)
             elif 'detections' in result_dict:
                 count = len(result_dict['detections'])
                 mass_text = "mass" if count == 1 else "masses"
                 model_result_display = f"{count} potential {mass_text} detected" if count > 0 else "No suspicious masses detected"
             # Adicione outros formatos conforme necessário
         # Se não for JSON ou não tiver formato esperado, usa a string original
    except:
         pass # Usa a string original se não for JSON válido


    # Conteúdo da página
    page_title = "Attendance Details" # Título
    content = [
        Div(
            H1(page_title),
            Div(
                A("Back to List", href="/attendances", cls="btn btn-secondary"),
                # Mostra botão Editar apenas se tiver permissão
                A("Edit", href=f"/attendances/edit/{attendance_id}", cls="btn") if can_edit_delete else "",
                # Mostra botão Delete apenas se tiver permissão (usando HTMX)
                A("Delete",
                  hx_post=f"/attendances/delete/{attendance_id}", # POST para a rota de delete
                  hx_target="body", # Alvo pode ser body para receber redirect com msg
                  hx_swap="outerHTML", # Ou ajuste conforme necessário
                  hx_confirm="Are you sure you want to delete this attendance record?",
                  cls="btn btn-danger") if can_edit_delete else "",
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
                    P(Strong("Diagnosis Result: "), model_result_display), # Usa resultado formatado
                    P(Strong("Expected Result (Provided): "), attendance.get("expected_result", "N/A")),
                    P(
                        Strong("Diagnosis Correctness: "),
                        Span(
                            "Correct" if attendance.get("correct_diagnosis") else "Incorrect",
                            cls=f"badge {'badge-success' if attendance.get('correct_diagnosis') else 'badge-error'}"
                        ) if attendance.get("correct_diagnosis") is not None else Span("Not Confirmed", cls="badge badge-secondary")
                    ),
                    cls="diagnosis-info"
                ),

                cls="info-container"
            ),
            title="Attendance Information"
        )
    )

    # Cartão com a imagem médica
    image_b64 = attendance.get('image_base64', '')
    content.append(
        Card(
            Div(
                Img( src=f"data:image/png;base64,{image_b64}", alt="Medical image", cls="medical-image") if image_b64 else P("Image not available."),
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
                        P(Strong(f"Region {i+1}:")),
                        P(f"Position: X={box.get('x')}, Y={box.get('y')}"),
                        P(f"Size: Width={box.get('width')}, Height={box.get('height')}"),
                        P(f"Confidence: {box.get('confidence', 0) * 100:.1f}%"),
                        P(f"Observations: {box.get('observations', 'None')}"),
                    )
                    for i, box in enumerate(bounding_boxes)
                ], cls="boxes-list"), # Adiciona classe para estilizar lista
            ]

            content.append(
                Card(
                    Div(*boxes_content, cls="bounding-boxes-info"),
                    title="Anomaly Detection Details" # Título mais descritivo
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

    # CSS específico para esta página (mantido como antes, com ajustes para lista de boxes)
    content.append(
        Style("""
            .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
            .page-actions { display: flex; gap: 0.5rem; }
            .info-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
            .basic-info p, .diagnosis-info p { margin-bottom: 0.5rem; } /* Espaçamento entre parágrafos */
            .image-container { display: flex; justify-content: center; padding: 1rem; background-color: #f8f9fa; border-radius: 0.25rem; }
            .medical-image { max-width: 100%; max-height: 500px; object-fit: contain; }
            .badge { display: inline-block; padding: 0.25rem 0.6rem; border-radius: 0.25rem; font-weight: 500; font-size: 0.875rem; line-height: 1.2; vertical-align: middle;}
            .badge-success { background-color: #d1fae5; color: #065f46; }
            .badge-error { background-color: #fee2e2; color: #b91c1c; }
            .badge-secondary { background-color: #e5e7eb; color: #4b5563; }
            .bounding-boxes-info ul.boxes-list { list-style: none; padding-left: 0; margin-top: 1rem; }
            .bounding-boxes-info li { margin-bottom: 1rem; padding: 1rem; background-color: #f9fafb; border-radius: 4px; border: 1px solid #eee; }
            .bounding-boxes-info li p { margin-bottom: 0.3rem; font-size: 0.9rem;}
            .observations-text { white-space: pre-wrap; line-height: 1.6; background-color: #fdfdff; padding: 1rem; border-radius: 4px; border: 1px solid #f0f0f5; }
        """)
    )

    # *** ALTERADO: Passar user_profile para MainLayout ***
    return MainLayout(page_title, *content, active_page="attendances", user_profile=user_profile)