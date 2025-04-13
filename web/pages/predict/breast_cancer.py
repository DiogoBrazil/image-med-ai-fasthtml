# web/pages/predict/breast_cancer.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Alert, Img
from services.prediction_service import PredictionService
from services.auth_service import AuthService
# --- Importa a função de HISTOGRAMA ---
from utils.plotting import generate_confidence_histogram
# -------------------------------------
import json, base64, io
from PIL import Image, UnidentifiedImageError

async def prediction_breast_cancer_page(request):
    session = request.scope.get("session", {})
    token = session.get('token')
    user_profile = session.get('user_profile')

    if not AuthService.is_professional(user_profile):
        session['message'], session['message_type'] = "Access denied.", "error"
        return RedirectResponse('/', status_code=303)

    page_title = "Breast Cancer Detection"
    error_message = None
    prediction_data = None
    original_filename = None
    chart_base64 = None # Agora guarda o HISTOGRAMA

    if request.method == "POST":
        form_data = await request.form()
        uploaded_file = form_data.get('image_file')
        if uploaded_file and uploaded_file.filename:
             if uploaded_file.content_type not in ["image/jpeg", "image/png", "image/gif", "image/bmp"]: error_message = "Invalid file type."
             else:
                 original_filename = uploaded_file.filename
                 file_content = await uploaded_file.read()
                 if not file_content: error_message = "Uploaded file is empty."
                 else:
                     result = await PredictionService.predict_breast_cancer(token, file_content, original_filename)
                     if result.get("success"):
                         prediction_data = result.get("data")
                         if prediction_data:
                             bounding_boxes = prediction_data.get('bounding_boxes', [])
                             # --- Gera HISTOGRAMA de Confiança ---
                             if bounding_boxes:
                                 try:
                                     # Chama a nova função de histograma
                                     chart_base64 = generate_confidence_histogram(bounding_boxes, title="Confidence Distribution")
                                     print("Histograma de confiança (Mama) gerado.")
                                 except Exception as plot_err:
                                     print(f"Erro ao gerar histograma de confiança (Mama): {plot_err}")
                             # ------------------------------------
                             session['last_prediction'] = {'model_used':'breast','model_result':json.dumps(bounding_boxes),'image_filename':original_filename,'image_base64':base64.b64encode(file_content).decode('utf-8')}
                         else: error_message = "Detection successful but results incomplete."
                     else: error_message = result.get("message", "Detection failed.")
        else: error_message = "No image file uploaded."


    # --- Renderização ---
    content = [ H1(page_title) ]
    if error_message: content.append(Alert(error_message, type="error"))

    # Formulário
    if not prediction_data:
        upload_form = Form(
            Div(Label("Upload Mammogram Image", For="image_file"), Input(id="image_file", name="image_file", type="file", accept="image/*", required=True), Small("Upload JPEG, PNG, GIF, or BMP images."), cls="form-group"),
            Button("Analyze Image", type="submit", cls="btn btn-primary"),
            method="post", action="/predict/breast-cancer", enctype="multipart/form-data" )
        content.append(Card(upload_form, title="Image Upload"))

    # Resultados
    if prediction_data:
        annotated_image_b64 = prediction_data.get('image_base64')
        bounding_boxes = prediction_data.get('bounding_boxes', [])

        detection_summary_text = "No suspicious masses detected."
        detection_summary_cls = "text-success"
        if bounding_boxes:
            count = len(bounding_boxes)
            mass_text = "mass" if count == 1 else "masses"
            detection_summary_text = f"{count} potential {mass_text} detected:"
            detection_summary_cls = "text-danger"

        # Cria a lista de detalhes SOMENTE se houver bounding boxes
        details_list_items = []
        if bounding_boxes:
             details_list_items = [
                 Li(f"Region {i+1}: Conf {box.get('confidence', 0)*100:.1f}% (Obs: {box.get('observations', 'N/A')})")
                 for i, box in enumerate(bounding_boxes)
             ]

        # Monta o conteúdo do painel direito dinamicamente
        right_panel_content = [
            H4("Detections Analysis"),
            P(detection_summary_text, cls=f"detection-summary {detection_summary_cls}")
        ]
        # Adiciona o histograma se foi gerado e existem boxes
        if bounding_boxes and chart_base64:
            right_panel_content.append(
                Div(Img(src=f"data:image/png;base64,{chart_base64}", alt="Detection Confidence Histogram", style="max-width:100%; height:auto; border: 1px solid #eee; margin-top:1rem; margin-bottom:1rem;"))
            )
        elif bounding_boxes: # Se boxes existem mas gráfico falhou
            right_panel_content.append(P("Confidence histogram unavailable.", style="font-size:0.9em; color:#6b7280;"))

        # Adiciona a lista Ul SOMENTE se ela tiver itens
        if details_list_items:
            right_panel_content.append(H5("Details:", style="margin-top:1.5rem; font-size:0.95em;"))
            right_panel_content.append(Ul(*details_list_items)) # Desempacota os LIs

        # Monta o Card de resultados
        result_card_content = [
            # Container Flex
            Div(
                # Painel Esquerdo (Imagem Anotada)
                Div(
                    H4("Annotated Image"),
                    Div(Img(src=f"data:image/jpeg;base64,{annotated_image_b64}", alt=f"Annotated: {original_filename}", cls="prediction-image-preview") if annotated_image_b64 else P("Annotated image unavailable."), cls="image-preview-container"),
                    cls="result-left-panel"
                ),
                # Painel Direito (Detalhes e Histograma)
                # Usa '*' para desempacotar os itens do painel direito
                Div(*right_panel_content, cls="result-detections-container"),
                cls="result-container"
            ),
            # Botões
            Div(
                A("Create Attendance Record", href="/attendances/add", cls="btn btn-success"),
                A("New Analysis", href="/predict/breast-cancer", cls="btn btn-secondary"),
                A("Back to Dashboard", href="/", cls="btn btn-outline"),
                cls="result-actions"
            )
        ]
        content.append(Card(*result_card_content)) # Sem título no Card

    # CSS Completo
    content.append(Style("""
        /* --- Estilos Gerais do Formulário e Botões --- */
        .form-group { margin-bottom: 1.25rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #374151; }
        .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 0.6rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05); box-sizing: border-box; font-size: 1rem; line-height: 1.5; }
        .form-group input[type=file] { padding: 0.4rem; box-shadow: none; border: 1px dashed #d1d5db; background-color: #f9fafb; }
        .form-group input[type=file]::file-selector-button { margin-right: 0.8rem; border: thin solid grey; background: #eee; padding: 0.4rem 0.8rem; border-radius: 0.2rem; cursor: pointer; transition: background-color 0.2s; }
        .form-group input[type=file]::file-selector-button:hover { background-color: #ddd; }
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus { border-color: var(--primary-color, #2563eb); outline: none; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2); }
        .form-group small { display: block; margin-top: 0.25rem; font-size: 0.85em; color: #6b7280; }
        .result-actions { margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color, #e5e7eb); display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center;}
        .btn { display: inline-block; background-color: var(--primary-color); color: white; padding: 0.6rem 1.2rem; border-radius: 0.375rem; text-decoration: none; font-weight: 500; border: none; cursor: pointer; transition: background-color 0.2s, transform 0.1s; text-align: center; line-height: 1.2; }
        .btn:hover { background-color: var(--secondary-color); transform: translateY(-1px); }
        .btn-success { background-color: var(--success-color, #10b981); border-color: var(--success-color, #10b981); color: white; }
        .btn-success:hover { background-color: #059669; border-color: #059669; }
        .btn-secondary { background-color: #6b7280; border-color: #6b7280; color: white; }
        .btn-secondary:hover { background-color: #4b5563; border-color: #4b5563; }
        .btn-outline { background-color: transparent; border: 1px solid #6b7280; color: #6b7280; }
        .btn-outline:hover { background-color: #f3f4f6; color: #4b5563; }
        /* --- Estilos para Layout Flex dos Resultados --- */
        .result-container { display: flex; flex-wrap: wrap; gap: 2rem; padding: 0 1.5rem 1.5rem 1.5rem; align-items: flex-start; }
        .result-left-panel { flex: 1 1 55%; min-width: 320px; text-align: center; }
        .result-detections-container { flex: 1 1 40%; min-width: 280px; padding-top: 0.5rem; }
        .result-left-panel h4, .result-detections-container h4 { margin-top: 0; margin-bottom: 1rem; font-weight: 600; color: #4b5563; font-size: 1.05em; }
        /* --- Estilos para Preview da Imagem Anotada --- */
        .image-preview-container { margin-bottom: 1rem; text-align: center; width: 100%; }
        .prediction-image-preview { display: block; margin-left: auto; margin-right: auto; width: 100%; max-width: 500px; height: auto; border: 1px solid #ccc; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border-radius: 4px; }
        /* --- Estilos para Lista/Sumário de Detecções --- */
        .result-detections-container ul { padding-left: 1.5rem; margin: 0.5rem 0 0 0; font-size: 0.9rem; list-style-type: square; }
        .result-detections-container li { margin-bottom: 0.4rem; color: #374151; }
        .detection-summary { font-weight: 600; margin-bottom: 1rem; font-size: 1.05em; }
        .text-danger { color: #b91c1c; }
        .text-success { color: #047857; }
    """)
    )

    # Renderiza o layout principal
    return MainLayout(page_title, *content, active_page="predict", user_profile=user_profile)