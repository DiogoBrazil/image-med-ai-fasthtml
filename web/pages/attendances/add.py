# web/pages/attendances/add.py
from fasthtml.common import *
# Importações necessárias
from components.layout import MainLayout
from components.ui import Card, Alert, Img # Importa Img para preview
from components.forms import AttendanceForm # O formulário de atendimento
from services.attendance_service import AttendanceService
from services.health_units_service import HealthUnitsService
from services.auth_service import AuthService
import base64 # Para lidar com a imagem
import json # Para ler/escrever resultados na sessão

async def add_attendance_page(request):
    """Renderiza a página para adicionar atendimento, com possível pré-preenchimento a partir da sessão."""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_id = session.get('user_id')
    user_profile = session.get('user_profile')
    admin_id = session.get("admin_id") # admin_id associado ao profissional

    # Segurança: Apenas profissionais podem adicionar atendimentos
    if not AuthService.is_professional(user_profile):
        session['message'] = "Only healthcare professionals can register attendances"
        session['message_type'] = "error"
        return RedirectResponse('/', status_code=303)

    error_message = None
    prefilled_data = {} # Guarda dados pré-preenchidos da predição ou de erro POST
    image_preview_b64 = None # Guarda base64 da imagem para preview (se houver)
    image_preview_filename = None # Guarda nome do arquivo para preview

    # --- Lógica GET: Verifica predição anterior na sessão ---
    if request.method == "GET":
        if 'last_prediction' in session:
            try:
                prediction_session_data = session.pop('last_prediction') # Pega e remove
                print(f"Dados de predição encontrados na sessão: {prediction_session_data}") # Log
                prefilled_data['model_used'] = prediction_session_data.get('model_used')
                # Guarda o resultado como string (o form pode ter campo hidden para isso)
                prefilled_data['model_result'] = str(prediction_session_data.get('model_result', ''))
                # Guarda info da imagem para preview e possível reuso no POST
                image_preview_b64 = prediction_session_data.get('image_base64')
                image_preview_filename = prediction_session_data.get('image_filename')
                # Armazena temporariamente na sessão caso precise re-renderizar após erro no POST
                if image_preview_b64: session['_temp_image_b64'] = image_preview_b64
                if image_preview_filename: session['_temp_image_filename'] = image_preview_filename

            except Exception as e:
                print(f"Erro ao processar dados da sessão 'last_prediction': {e}")
                if 'last_prediction' in session: del session['last_prediction'] # Limpa sessão em caso de erro


    # --- Busca Unidades de Saúde (Sempre necessário para o select) ---
    health_units = []
    try:
        # Idealmente, buscar apenas unidades do admin do profissional
        health_units_result = await HealthUnitsService.get_health_units(token)
        if health_units_result.get("success"):
            health_units = health_units_result.get("health_units", [])
            if not health_units and not error_message: # Não sobrescreve erro anterior
                 error_message = "No available health units found for your profile."
        elif not error_message: # Não sobrescreve erro anterior
             error_message = health_units_result.get("message", "Could not load health units.")
    except Exception as e:
         if not error_message: error_message = f"Error loading health units: {e}"


    # --- Lógica POST: Processa o formulário ---
    if request.method == "POST":
        form_data = await request.form()
        health_unit_id = form_data.get("health_unit_id")
        model_used = form_data.get("model_used")
        image_file = form_data.get("image_base64_input") # Nome diferente do campo da sessão
        expected_result = form_data.get("expected_result", "")
        observation = form_data.get("observation", "")
        # Resultado do modelo pode vir de um campo hidden se pré-preenchido
        model_result_str = form_data.get("model_result") or "" # Garante que seja string

        # Imagem: Prioriza novo upload, senão usa a da sessão temporária (se existir)
        image_base64_to_send = None
        filename_to_send = None

        # Verifica novo upload
        if image_file and image_file.filename:
            if image_file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
                error_message = "Invalid image type (only JPEG, PNG, GIF)."
            else:
                contents = await image_file.read()
                if contents:
                    image_base64_to_send = base64.b64encode(contents).decode("utf-8")
                    filename_to_send = image_file.filename
                    # Guarda na sessão temporária para re-renderizar se der erro
                    session['_temp_image_b64'] = image_base64_to_send
                    session['_temp_image_filename'] = filename_to_send
                    # Atualiza preview para a nova imagem
                    image_preview_b64 = image_base64_to_send
                    image_preview_filename = filename_to_send
                else:
                    error_message = "Uploaded file is empty."
        else:
            # Se não houve upload, tenta usar a imagem da sessão temporária (vindo do GET ou de erro POST anterior)
            image_base64_to_send = session.get('_temp_image_b64')
            filename_to_send = session.get('_temp_image_filename')
            # Mantém preview com a imagem vinda da sessão
            image_preview_b64 = image_base64_to_send
            image_preview_filename = filename_to_send


        # Limpa a sessão temporária após tentar usar/guardar
        if '_temp_image_b64' in session: del session['_temp_image_b64']
        if '_temp_image_filename' in session: del session['_temp_image_filename']

        # Validações
        if not error_message and not all([health_unit_id, model_used]):
             error_message = "Health unit and AI model are required."
        if not error_message and not image_base64_to_send:
             # Pode acontecer se veio da predição mas falhou em guardar na sessão, ou se não fez upload
             error_message = "Medical image is required (upload or from previous prediction)."

        # Se passou nas validações, monta o payload e envia para API
        if not error_message:
            attendance_data = {
                "professional_id": user_id,
                "health_unit_id": health_unit_id,
                "admin_id": admin_id or "", # Garante que é string
                "model_used": model_used,
                "model_result": model_result_str, # Envia a string JSON ou o que tiver
                "expected_result": expected_result,
                "correct_diagnosis": False, # Valor inicial padrão
                "image_base64": image_base64_to_send,
                "observation": observation
            }

            create_result = await AttendanceService.create_attendance(token, attendance_data)
            if create_result.get("success"):
                session['message'] = "Attendance record created successfully"
                session['message_type'] = "success"
                # Redireciona para o dashboard do profissional após sucesso
                return RedirectResponse('/', status_code=303)
            else:
                error_message = create_result.get("message", "Error creating attendance record")

        # Se deu erro no POST, recria prefilled_data com os dados submetidos para repopular o form
        if error_message:
             prefilled_data = {
                 'health_unit_id': health_unit_id,
                 'model_used': model_used,
                 'model_result': model_result_str,
                 'expected_result': expected_result,
                 'observation': observation,
                 # Guarda novamente a imagem/nome para preview no re-render
                 'image_base64': image_preview_b64,
                 'image_filename': image_preview_filename,
             }


    # --- Renderização da Página ---
    page_title = "Register New Attendance"
    content = [ H1(page_title) ]

    if error_message:
        content.append(Alert(error_message, type="error"))

    # Mostra preview da imagem se veio da predição ou de um POST com erro
    if image_preview_b64:
         content.append(
             Card(
                 H3("Image Preview" + (f" ({image_preview_filename})" if image_preview_filename else "")),
                 Div(Img(src=f"data:image/jpeg;base64,{image_preview_b64}", # Assume JPEG/PNG
                         alt="Medical Image Preview",
                         style="max-width: 100%; max-height: 300px; display: block; margin: auto; border: 1px solid #eee;"),
                     cls="image-preview-container"),
                 P("Uploading a new image below will replace this one.", cls="preview-note") if not request.method == "POST" else "", # Nota só no GET
                 title="Image to be Associated"
             )
         )

    # Cria o formulário, passando os dados pré-preenchidos
    # Nota: O form não lida diretamente com prefill de 'file' input nem model_result complexo,
    # mas preenche os selects e outros campos de texto/textarea.
    # O model_result pode ser um campo hidden ou textarea readonly no form.
    form = AttendanceForm(
        action="/attendances/add",
        models=[ # Mova para config se preferir
            {"id": "respiratory", "name": "Respiratory Diseases"},
            {"id": "tuberculosis", "name": "Tuberculosis"},
            {"id": "osteoporosis", "name": "Osteoporosis"},
            {"id": "breast", "name": "Breast Cancer"}
        ],
        health_units=health_units,
        attendance=prefilled_data, # Passa dados preenchidos (model_used, etc)
        professional_id=user_id,
        admin_id=admin_id # Passa admin_id para possível uso interno no form
    )

    # Adiciona Card com o formulário
    content.append( Card(form, title="Attendance Details") )

    # Adiciona CSS
    content.append(
        Style("""
            .page-header { margin-bottom: 1.5rem; }
            .form-group { margin-bottom: 1.25rem; }
            .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #374151; }
            .form-group input, .form-group select, .form-group textarea {
                 width: 100%; padding: 0.6rem 0.75rem; border: 1px solid #d1d5db;
                 border-radius: 0.375rem; box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
                 box-sizing: border-box; font-size: 1rem; line-height: 1.5;
             }
             /* Estilo específico para o input de arquivo */
             .form-group input[type=file] {
                  padding: 0.4rem; /* Padding menor para input file */
                  box-shadow: none;
                  border: 1px dashed #d1d5db; /* Borda tracejada */
                  background-color: #f9fafb;
             }
             .form-group input[type=file]::file-selector-button {
                  margin-right: 0.8rem;
                  border: thin solid grey;
                  background: #eee;
                  padding: 0.4rem 0.8rem;
                  border-radius: 0.2rem;
                  cursor: pointer;
                  transition: background-color 0.2s;
             }
            .form-group input[type=file]::file-selector-button:hover {
                 background-color: #ddd;
             }
            .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
                  border-color: var(--primary-color, #2563eb); outline: none;
                  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
             }
            .form-group .btn-secondary { margin-left: 1rem; }
            .image-preview-container { margin-top: 0.5rem; text-align: center; }
            .preview-note { font-size: 0.85em; color: #6b7280; text-align: center; margin-top: 0.5rem; }
        """)
    )

    # Renderiza o layout principal
    # Passa 'attendances' como active_page se quiser que esse item fique ativo no menu (se visível)
    return MainLayout(page_title, *content, active_page="attendances", user_profile=user_profile)