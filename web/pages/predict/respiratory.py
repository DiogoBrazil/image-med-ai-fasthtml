# web/pages/predict/respiratory.py
from fasthtml.common import *
# Importações padrão
from components.layout import MainLayout
from components.ui import Card, Alert, Img # Importa Img para preview
from services.prediction_service import PredictionService
from services.auth_service import AuthService # Para verificar perfil
from utils.plotting import generate_probability_chart # Função do gráfico
import json # Para guardar resultado na sessão
import base64 # Para lidar com imagem
# Importações para redimensionamento
import io
from PIL import Image, UnidentifiedImageError

async def prediction_respiratory_page(request):
    """Página para upload de imagem e visualização da predição respiratória com gráfico."""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_profile = session.get('user_profile')

    # --- Verificação de Perfil ---
    if not AuthService.is_professional(user_profile):
        session['message'] = "Access denied. Only professionals can perform predictions."
        session['message_type'] = "error"
        return RedirectResponse('/', status_code=303)
    # ---------------------------

    page_title = "Respiratory Disease Prediction"
    error_message = None
    prediction_result = None # Guarda dict de probabilidades
    original_filename = None
    # image_to_preview_b64 guarda a imagem REDIMENSIONADA para preview e sessão
    image_to_preview_b64 = None
    chart_base64 = None # Guarda o gráfico gerado

    # --- Lógica POST (Processa Upload, Predição e Redimensionamento) ---
    if request.method == "POST":
        form_data = await request.form()
        uploaded_file = form_data.get('image_file')
        if uploaded_file and uploaded_file.filename:
             # Validação básica de tipo
             if uploaded_file.content_type not in ["image/jpeg", "image/png", "image/gif", "image/bmp"]:
                 error_message = "Invalid file type. Please upload an image (JPEG, PNG, GIF, BMP)."
             else:
                 original_filename = uploaded_file.filename
                 file_content = await uploaded_file.read() # CONTEÚDO ORIGINAL
                 if not file_content: error_message = "Uploaded file is empty."
                 else:
                     # Chama Predição com Imagem ORIGINAL
                     result = await PredictionService.predict_respiratory(token, file_content, original_filename)

                     if result.get("success"):
                         prediction_result = result.get("data", {}).get("prediction")
                         if prediction_result and isinstance(prediction_result, dict):
                             # Tenta Redimensionar IMAGEM ORIGINAL para Sessão/Preview
                             try:
                                 img = Image.open(io.BytesIO(file_content))
                                 img = img.convert("RGB") # Garante formato RGB
                                 max_dim = 640 # Dimensão máxima alvo
                                 img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS) # Redimensiona inplace

                                 # Salva imagem redimensionada em buffer como JPEG
                                 buffer = io.BytesIO()
                                 img.save(buffer, format="JPEG", quality=85) # Qualidade 85
                                 buffer.seek(0)
                                 image_to_preview_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                                 print(f"Imagem redimensionada para sessão (Resp): {len(image_to_preview_b64)} bytes base64")
                             except UnidentifiedImageError:
                                 error_message = "Could not process the uploaded image format for preview."
                                 image_to_preview_b64 = None
                             except Exception as resize_err:
                                 print(f"Erro ao redimensionar imagem (Resp): {resize_err}")
                                 error_message = "Error processing image for preview."
                                 image_to_preview_b64 = None

                             # Tenta Gerar gráfico
                             try:
                                 chart_base64 = generate_probability_chart(prediction_result, title="Respiratory Condition Probabilities")
                                 print("Gráfico respiratório gerado.")
                             except Exception as plot_err:
                                 print(f"Erro ao gerar gráfico respiratório: {plot_err}")
                                 # Continua sem gráfico se der erro

                             # Guarda na sessão (imagem REDIMENSIONADA) somente se foi gerada
                             if image_to_preview_b64:
                                 session['last_prediction'] = {
                                     'model_used': 'respiratory',
                                     'model_result': json.dumps(prediction_result),
                                     'image_filename': original_filename,
                                     'image_base64': image_to_preview_b64 # Salva a versão REDIMENSIONADA
                                 }
                             elif not error_message: # Se redimensionamento falhou mas predição não
                                 error_message = "Prediction successful, but image preview could not be prepared for attendance form."

                         else: error_message = "Prediction successful but no results returned or format is invalid."
                     else: error_message = result.get("message", "Prediction failed.")
        else: error_message = "No image file uploaded."

    # --- Renderização da Página ---
    content = [ H1(page_title) ]
    if error_message: content.append(Alert(error_message, type="error"))

    # Formulário de Upload (só aparece se não houver resultado)
    if not prediction_result:
        upload_form = Form(
            Div(
                Label("Upload Chest X-ray Image", For="image_file"),
                Input(id="image_file", name="image_file", type="file", accept="image/*", required=True),
                 Small("Upload JPEG, PNG, GIF, or BMP images."),
                cls="form-group"
            ),
            Button("Analyze Image", type="submit", cls="btn btn-primary"),
            method="post",
            action="/predict/respiratory",
            enctype="multipart/form-data"
        )
        content.append(Card(upload_form, title="Image Upload"))

    # Card de Resultados (só aparece se houver resultado da API)
    if prediction_result:
        result_card_content = [
            # --- Container Flex para Gráfico e Imagem ---
            Div(
                # --- Painel Esquerdo (Gráfico) ---
                Div(
                    H4("Probabilities Chart"), # Título do gráfico
                    Img(src=f"data:image/png;base64,{chart_base64}", alt="Prediction Probabilities Chart", style="max-width:100%; height:auto; border: 1px solid #eee;") if chart_base64 else P("Chart could not be generated.", style="color: #ef4444;"),
                    cls="result-left-panel" # Classe para layout (metade esquerda)
                ),
                # --- Painel Direito (Imagem) ---
                Div(
                     H4("Uploaded Image Preview"), # Título da imagem
                     Div( # Container da imagem
                         Img(src=f"data:image/jpeg;base64,{image_to_preview_b64}", # Mostra JPEG redimensionado
                             alt=f"Uploaded X-ray: {original_filename}",
                             # Aplica a classe CSS para estilo e tamanho
                             cls="prediction-image-preview") if image_to_preview_b64 else P("Image preview unavailable."),
                         cls="image-preview-container" # Container para centralizar
                     ),
                    cls="result-right-panel" # Classe para layout (metade direita)
                ),
                cls="result-container" # Aplica display: flex
            ),
            # -----------------------------------------
            # Botões de Ação (fora do container flex)
            Div(
                A("Create Attendance Record", href="/attendances/add", cls="btn btn-success"),
                A("New Prediction", href="/predict/respiratory", cls="btn btn-secondary"),
                A("Back to Dashboard", href="/", cls="btn btn-outline"),
                cls="result-actions" # Classe para centralizar e adicionar borda superior
            )
        ]
        # Card principal SEM título "Analysis Complete"
        content.append(Card(*result_card_content))

    # --- CSS Completo ---
    # Inclui estilos para form, botões, preview, gráfico, status e layout flex
    content.append(
        Style("""
            /* --- Estilos Gerais do Formulário e Botões (Reutilizados) --- */
            .form-group { margin-bottom: 1.25rem; }
            .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #374151; }
            .form-group input, .form-group select, .form-group textarea {
                 width: 100%; padding: 0.6rem 0.75rem; border: 1px solid #d1d5db;
                 border-radius: 0.375rem; box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
                 box-sizing: border-box; font-size: 1rem; line-height: 1.5;
             }
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
            .result-container {
                display: flex;
                flex-wrap: wrap; /* Quebra linha em telas menores */
                gap: 2rem; /* Espaço entre colunas */
                padding: 0 1.5rem 1.5rem 1.5rem; /* Padding (sem padding superior, pois está dentro do card) */
                align-items: flex-start; /* Alinha itens no topo */
            }
            .result-left-panel { /* Para o gráfico */
                flex: 1 1 50%; /* Tenta 50%, flexível */
                min-width: 300px;
                text-align: center;
            }
            .result-right-panel { /* Para a imagem */
                flex: 1 1 45%; /* Tenta 45%, flexível */
                min-width: 280px;
                 display: flex; /* Usa flex para centralizar conteúdo verticalmente */
                 flex-direction: column;
                 align-items: center;
            }
             .result-left-panel h4, .result-right-panel h4 { /* Títulos dos painéis */
                 margin-top: 0;
                 margin-bottom: 1rem;
                 text-align: center;
                 font-weight: 600;
                 color: #4b5563;
                 font-size: 1.05em;
             }

            /* --- Estilos para Preview da Imagem --- */
            .image-preview-container {
                margin-bottom: 1rem; /* Espaço abaixo do preview, antes do resultado principal (se houver) */
                text-align: center;
                width: 100%; /* Ocupa largura do painel direito */
            }
            .prediction-image-preview {
                display: block; margin-left: auto; margin-right: auto;
                width: 100%; /* Ajustado para preencher o container */
                max-width: 400px; /* Limita um pouco mais que o painel direito */
                height: auto;
                border: 1px solid #ccc; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                border-radius: 4px;
            }

            /* --- Estilos para Status/Classe Predita (Respiratório) --- */
            .status-normal { color: #059669; font-weight: 500; background-color: #d1fae5; padding: 0.2em 0.6em; border-radius: 0.25rem; display: inline-block; }
            .status-covid_19 { color: #b91c1c; font-weight: 500; background-color: #fee2e2; padding: 0.2em 0.6em; border-radius: 0.25rem; display: inline-block; }
            .status-pneumonia_bacteriana, .status-pneumonia_viral { color: #92400e; font-weight: 500; background-color: #fffbeb; padding: 0.2em 0.6em; border-radius: 0.25rem; display: inline-block; }
            /* Adicione outras classes se seu modelo retornar mais opções */
        """)
    )

    # Renderiza o layout principal
    return MainLayout(page_title, *content, active_page="predict", user_profile=user_profile)