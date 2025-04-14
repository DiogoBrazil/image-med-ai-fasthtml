# web/pages/attendances/edit.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Alert, Img # Adicionado Img
from components.forms import AttendanceForm
from services.attendance_service import AttendanceService
from services.health_units_service import HealthUnitsService
from services.auth_service import AuthService
import base64
import json # Para ler o model_result

async def edit_attendance_page(request):
    """Renderiza a página para editar um atendimento médico existente"""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_id = session.get('user_id')
    # *** ADICIONADO: Obter user_profile da sessão ***
    user_profile = session.get('user_profile')

    # Obtém o ID do atendimento a ser editado da URL
    path_params = request.path_params
    attendance_id = path_params.get('attendance_id')

    if not attendance_id:
        session['message'] = "Attendance ID is missing"
        session['message_type'] = "error"
        return RedirectResponse('/attendances', status_code=303)

    # Obtém os dados do atendimento a ser editado
    # Incluindo a imagem base64 completa para mostrar no preview
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
    image_preview_b64 = attendance.get("image_base64") # Pega imagem atual para preview

    # Lista de modelos de IA disponíveis
    models = [
        {"id": "respiratory", "name": "Respiratory Diseases"},
        {"id": "tuberculosis", "name": "Tuberculosis"},
        {"id": "osteoporosis", "name": "Osteoporosis"},
        {"id": "breast", "name": "Breast Cancer"}
    ]

    # Obtém unidades de saúde disponíveis
    health_units = []
    try:
        health_units_result = await HealthUnitsService.get_health_units(token)
        if health_units_result.get("success"):
            health_units = health_units_result.get("health_units", [])
        else:
            error_message = health_units_result.get("message", "Could not load health units.")
    except Exception as e:
         error_message = f"Error loading health units: {e}"


    # Processa o formulário no POST
    if request.method == "POST":
        form_data = await request.form()

        # Valida campos obrigatórios (apenas unidade e modelo, outros são opcionais na edição)
        health_unit_id = form_data.get("health_unit_id")
        model_used = form_data.get("model_used") # Modelo não deve mudar, mas pegamos do form se presente

        if not health_unit_id: # Modelo não precisa ser obrigatório aqui, pois não deveria mudar
             error_message = "Health unit is required"
        else:
            try:
                # Processa o arquivo de imagem (apenas se um novo for enviado)
                image_file = form_data.get("image_base64_input") # Nome diferente
                new_image_base64 = None

                if image_file and image_file.filename:
                     allowed_types = ["image/jpeg", "image/png", "image/gif", "image/bmp", "image/webp"]
                     if image_file.content_type not in allowed_types:
                          error_message = f"Invalid image type ({image_file.content_type}). Allowed: JPEG, PNG, GIF, BMP, WEBP."
                     else:
                          contents = await image_file.read()
                          if contents:
                              new_image_base64 = base64.b64encode(contents).decode("utf-8")
                              image_preview_b64 = new_image_base64 # Atualiza preview para nova imagem
                          else:
                              error_message = "Uploaded file is empty, keeping the original image."
                # Se não houve erro de tipo/vazio, prossegue

                if not error_message:
                    # Prepara os dados atualizados do atendimento
                    # Exclui campos que não devem ser enviados vazios ou não devem ser alterados facilmente
                    update_data = {
                        "professional_id": attendance["professional_id"], # Mantém o profissional original
                        "health_unit_id": health_unit_id,
                        "admin_id": attendance["admin_id"], # Mantém o admin original
                        "model_used": model_used or attendance["model_used"], # Usa o do form ou mantém original
                        "model_result": form_data.get("model_result") or attendance["model_result"], # Permite editar resultado? Ou mantém original? Decidi manter o original
                        "expected_result": form_data.get("expected_result", attendance.get("expected_result","")), # Permite editar expected
                        # Atualiza correct_diagnosis (se fornecido)
                        "correct_diagnosis": form_data.get("correct_diagnosis") == "true" if form_data.get("correct_diagnosis") is not None else attendance.get("correct_diagnosis"),
                        "observation": form_data.get("observation", attendance.get("observation","")) # Permite editar observação
                    }

                    # Inclui a NOVA imagem apenas se foi enviada
                    # A API deve ignorar 'image_base64' se for None ou vazio
                    # if new_image_base64:
                    #     update_data["image_base64"] = new_image_base64
                    # -> A API não espera image_base64 no PUT, então removemos

                    # Se o modelo for "breast", adiciona os bounding boxes originais (ou editados, se implementado)
                    if attendance.get("model_used") == "breast":
                         # A API de PUT não parece aceitar bounding_boxes, então não enviamos
                         pass
                         # update_data["bounding_boxes"] = attendance.get("bounding_boxes", [])

                    # Envia para a API
                    result = await AttendanceService.update_attendance(token, attendance_id, update_data)

                    if result.get("success", False):
                        session['message'] = "Attendance record updated successfully"
                        session['message_type'] = "success"
                        # Redireciona para a lista após sucesso
                        return RedirectResponse('/attendances', status_code=303)
                    else:
                        error_message = result.get("message", "Error updating attendance record")

            except Exception as e:
                error_message = f"Error processing form: {str(e)}"

    # --- Renderização da Página ---
    page_title = "Edit Attendance Record"
    content = [
        Div(
            H1(page_title),
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

    # Mostra preview da imagem atual (ou da nova, se POST falhou)
    if image_preview_b64:
        content.append(
            Card(
                Div(
                    H3("Medical Image"),
                    Div( Img( src=f"data:image/png;base64,{image_preview_b64}", style="max-width: 100%; max-height: 300px; display: block; margin: auto; border: 1px solid #eee;"), cls="image-preview-container" ),
                    P("Upload a new image below to replace this one.", cls="preview-note"),
                    cls="current-image"
                ),
                title="Image Preview"
            )
        )
    else:
         content.append(P("No image available for this record.", cls="preview-note"))


    # Se houver resultado do modelo, exibe-o (não editável aqui)
    model_result_display = attendance.get("model_result", "")
    try:
         # Tenta formatar se for JSON
         result_dict = json.loads(model_result_display) if isinstance(model_result_display, str) and model_result_display.startswith('{') else None
         if result_dict:
             # Exemplo: Formata dicionário de probabilidades
             if 'probabilities' in result_dict:
                 probs_str = ", ".join([f"{k}: {v:.1f}%" for k,v in result_dict['probabilities'].items()])
                 model_result_display = f"Class: {result_dict.get('class_pred', 'N/A')} ({probs_str})"
             elif 'detections' in result_dict:
                 count = len(result_dict['detections'])
                 model_result_display = f"{count} detection(s) found."
             # Adicione outros formatos conforme necessário
         # Se não for JSON ou não tiver formato esperado, usa a string original
    except:
         pass # Usa a string original se não for JSON válido

    if model_result_display:
        content.append(
            Card(
                Div(
                    H3("Original AI Diagnosis Result"),
                    P(Strong("Model: "), attendance.get("model_used", "").capitalize()),
                    P(Strong("Result: "), model_result_display), # Mostra resultado formatado ou original
                    # Campo hidden para enviar o resultado original (se necessário pela API)
                    Hidden(name="model_result", value=attendance.get("model_result", "")),
                    cls="diagnosis-result"
                ),
                title="AI Information (Not Editable)"
            )
        )

    # Formulário para editar outros campos do atendimento
    form = AttendanceForm(
        action=f"/attendances/edit/{attendance_id}",
        models=models,
        health_units=health_units,
        attendance=attendance, # Passa dados atuais para preencher
        professional_id=attendance.get("professional_id"), # Passa IDs existentes
        admin_id=attendance.get("admin_id")
    )

    content.append(
        Card(
            form,
            title="Edit Attendance Information"
        )
    )

    # CSS específico para esta página (mantido como antes)
    content.append(
        Style("""
            .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
            .page-actions { display: flex; gap: 0.5rem; }
            .current-image { text-align: center; margin-bottom: 1rem; }
            .image-preview-container { margin-top: 1rem; padding: 1rem; background-color: #f8f9fa; border-radius: 0.25rem; display: flex; justify-content: center; }
            .preview-note { font-size: 0.85em; color: #6b7280; text-align: center; margin-top: 0.5rem; }
            .diagnosis-result { padding: 0.5rem 0; }
            .form-group input[type=file] { /* Ajuste para input de arquivo na edição */
                 padding: 0.4rem; box-shadow: none; border: 1px dashed #d1d5db; background-color: #f9fafb;
            }
            .form-group input[type=file]::file-selector-button {
                 margin-right: 0.8rem; border: thin solid grey; background: #eee; padding: 0.4rem 0.8rem;
                 border-radius: 0.2rem; cursor: pointer; transition: background-color 0.2s;
            }
            .form-group input[type=file]::file-selector-button:hover { background-color: #ddd; }
        """)
    )

    # *** ALTERADO: Passar user_profile para MainLayout ***
    return MainLayout(page_title, *content, active_page="attendances", user_profile=user_profile)