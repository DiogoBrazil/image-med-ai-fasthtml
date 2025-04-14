# web/pages/attendances/list.py
from fasthtml.common import *
# Importar datetime e NotStr
from datetime import datetime
from fasthtml.components import NotStr
# Importar componentes e serviços
from components.layout import MainLayout
from components.ui import Card, Table, Alert, Pagination # Pagination está aqui, usaremos
from services.attendance_service import AttendanceService
from services.health_units_service import HealthUnitsService
from services.auth_service import AuthService

# --- Definições dos Ícones SVG (mantidos como antes) ---
# Ícone de Olho (View) - Exemplo Bootstrap Icons
view_icon_svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-fill" viewBox="0 0 16 16">
  <path d="M10.5 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0"/>
  <path d="M0 8s3-5.5 8-5.5S16 8 16 8s-3 5.5-8 5.5S0 8 0 8m8 3.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7"/>
</svg>
"""
# Ícone de Lápis (Edit)
edit_icon_svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-square" viewBox="0 0 16 16">
  <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
  <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5z"/>
</svg>
"""
# Ícone de Lixeira (Deletar)
delete_icon_svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash3-fill" viewBox="0 0 16 16">
  <path d="M11 1.5v1h3.5a.5.5 0 0 1 0 1h-.538l-.853 10.66A2 2 0 0 1 11.115 16h-6.23a2 2 0 0 1-1.994-1.84L2.038 3.5H1.5a.5.5 0 0 1 0-1h3.5v-1A1.5 1.5 0 0 1 6.5 0h3A1.5 1.5 0 0 1 11 1.5m-5 0v1h4v-1a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5M4.5 5.029l.5 8.5a.5.5 0 1 0 .998-.06l-.5-8.5a.5.5 0 1 0-.998.06m6.53-.528a.5.5 0 0 0-.528.47l-.5 8.5a.5.5 0 0 0 .998.058l.5-8.5a.5.5 0 0 0-.47-.528M8 4.5a.5.5 0 0 0-.5.5v8.5a.5.5 0 0 0 1 0V5a.5.5 0 0 0-.5-.5"/>
</svg>
"""
# --------------------------------

async def attendances_list_page(request):
    """Renderiza a página de listagem de atendimentos médicos"""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_id = session.get('user_id')
    # *** ADICIONADO: Obter user_profile da sessão ***
    user_profile = session.get('user_profile')

    # Obtém parâmetros da query string
    query_params = request.query_params
    page = int(query_params.get('page', '1'))
    per_page = int(query_params.get('per_page', '10')) # Mantém per_page
    health_unit_id_filter = query_params.get('health_unit_id') # Renomeia para evitar conflito
    model_used_filter = query_params.get('model_used') # Renomeia para evitar conflito

    # Verifica permissões
    # Somente profissional pode adicionar, admin pode ver/filtrar
    can_add = AuthService.is_professional(user_profile)
    can_view_list = AuthService.is_admin(user_profile) # Admins podem ver a lista

    # Se não for admin, nega acesso à lista (ajuste conforme sua regra)
    if not can_view_list:
         session['message'] = "Only administrators can view the attendance list."
         session['message_type'] = "error"
         # Redireciona para o dashboard ou outra página apropriada
         return RedirectResponse('/', status_code=303)

    # --- Busca de Dados ---
    health_units = []
    attendances = []
    pagination = {}
    api_error = None

    # Obtém unidades de saúde para o filtro (sempre busca se for admin)
    if can_view_list:
        try:
            health_units_result = await HealthUnitsService.get_health_units(token)
            if health_units_result.get("success", False):
                health_units = health_units_result.get("health_units", [])
            else:
                 # Guarda erro, mas continua para tentar buscar atendimentos
                 api_error = health_units_result.get("message", "Error loading health units")
        except Exception as e:
            api_error = f"Error loading health units: {e}"

    # Obtém a lista de atendimentos (somente se for admin)
    if can_view_list:
        try:
            attendance_result = await AttendanceService.get_attendances(
                token, health_unit_id_filter, model_used_filter, page, per_page
            )
            if attendance_result.get("success", False):
                attendances = attendance_result.get("attendances", [])
                pagination = attendance_result.get("pagination", {})
            else:
                 # Guarda erro da busca de atendimentos
                 api_error = attendance_result.get("message", "Error loading attendance records")
        except Exception as e:
            api_error = f"Error loading attendances: {e}"
    # ---------------------

    page_title = "Medical Attendances"
    content = []

    # Adiciona notificação de erro da API ou mensagem da sessão
    if 'message' in session:
        message = session.pop('message')
        message_type = session.pop('message_type', 'success')
        content.append(Alert(message, type=message_type))
    elif api_error:
        content.append(Alert(api_error, type="error"))

    # Cabeçalho da página
    content.append(
        Div(
            H1(page_title),
            Div(
                # Botão só aparece para profissional
                A("New Attendance", href="/attendances/add", cls="btn btn-primary") if can_add else "",
                cls="page-actions"
            ),
            cls="page-header"
        )
    )

    # Seção de filtros (só para admins)
    if can_view_list and health_units: # Mostra filtro se for admin e tiver unidades
        filter_form = Form(
            Div(
                Div(
                    Label("Health Unit", For="health_unit_id"),
                    Select(
                        Option("All Health Units", value=""),
                        *[Option(unit["name"], value=unit["id"],
                                selected=health_unit_id_filter == unit["id"]) # Usa a variável renomeada
                          for unit in health_units],
                        id="health_unit_id", name="health_unit_id" # Nome do parâmetro da query
                    ),
                    cls="form-group"
                ),
                Div(
                    Label("AI Model", For="model_used"),
                    Select(
                        Option("All Models", value=""),
                        Option("Respiratory", value="respiratory", selected=model_used_filter == "respiratory"),
                        Option("Tuberculosis", value="tuberculosis", selected=model_used_filter == "tuberculosis"),
                        Option("Osteoporosis", value="osteoporosis", selected=model_used_filter == "osteoporosis"),
                        Option("Breast", value="breast", selected=model_used_filter == "breast"),
                        id="model_used", name="model_used" # Nome do parâmetro da query
                    ),
                    cls="form-group"
                ),
                Button("Filter", type="submit", cls="btn btn-secondary"), # Botão secundário para filtro
                cls="filter-inputs"
            ),
            method="get", # Filtro usa GET
            action="/attendances", # Submete para a própria página de lista
            cls="filter-form"
        )
        content.append(
            Card(
                filter_form,
                title="Filter Attendances",
                cls="filter-card"
            )
        )

    # Tabela de Atendimentos (se busca foi sucesso e for admin)
    if can_view_list and not api_error: # Só mostra tabela se for admin e não deu erro na busca
        if attendances:
            rows = []
            for attendance in attendances:
                attendance_id = attendance.get("id")
                attendance_date_str = attendance.get("attendance_date", "")
                attendance_date_formatted = attendance_date_str
                if isinstance(attendance_date_str, str) and attendance_date_str:
                    try:
                        date_obj = datetime.fromisoformat(attendance_date_str.replace('Z', '+00:00'))
                        attendance_date_formatted = date_obj.strftime("%d/%m/%Y %H:%M")
                    except ValueError: pass

                model_result = attendance.get("model_result", "N/A")
                correct_diagnosis = attendance.get("correct_diagnosis")
                # Tenta carregar model_result como JSON para pegar a classe principal (se for TB ou Osteo)
                try:
                     result_dict = json.loads(model_result) if isinstance(model_result, str) and model_result.startswith('{') else {}
                     display_result = result_dict.get("class_pred", model_result) # Mostra 'class_pred' ou o texto original
                except:
                     display_result = model_result # Mantém original se não for JSON válido

                diagnosis_display = Span(display_result) # Começa com o resultado
                if correct_diagnosis is not None:
                     # Ajusta o display se tivermos informação de correção
                     diag_text = "Correct" if correct_diagnosis else "Incorrect"
                     diag_class = "diagnosis-correct" if correct_diagnosis else "diagnosis-incorrect"
                     diagnosis_display = Span(f"{display_result} ", Span(f"({diag_text})", cls=diag_class))


                health_unit_id = attendance.get("health_unit_id", "")
                # Cria um dicionário para lookup rápido de nomes de unidade
                health_unit_names = {unit["id"]: unit["name"] for unit in health_units}
                health_unit_name = health_unit_names.get(health_unit_id, health_unit_id) # Mostra nome ou ID

                cells = [
                    Td(attendance_date_formatted),
                    Td(health_unit_name),
                    Td(attendance.get("model_used", "").capitalize()),
                    Td(diagnosis_display),
                ]

                # Ações: View para todos (admin/prof), Edit/Delete conforme permissão da API
                # A lógica exata de quem pode editar/deletar está na API/Serviço, aqui apenas mostramos os botões.
                # Adicionamos uma verificação básica se o usuário logado é o profissional do atendimento OU admin
                allow_edit_delete = (user_profile == "professional" and user_id == attendance.get("professional_id")) or AuthService.is_admin(user_profile)

                actions = Td(
                    A(NotStr(view_icon_svg), href=f"/attendances/view/{attendance_id}", cls="btn-icon btn-view", title="View Details"),
                    A(NotStr(edit_icon_svg), href=f"/attendances/edit/{attendance_id}", cls="btn-icon btn-edit", title="Edit Attendance") if allow_edit_delete else "",
                    A(NotStr(delete_icon_svg), hx_post=f"/attendances/delete/{attendance_id}", hx_target=f"#attendance-row-{attendance_id}", hx_swap="outerHTML", hx_confirm="Are you sure you want to delete this attendance record?", cls="btn-icon btn-delete", title="Delete Attendance") if allow_edit_delete else "",
                    cls="actions-cell"
                )
                cells.append(actions)

                rows.append(Tr(*cells, id=f"attendance-row-{attendance_id}"))

            headers = ["Date", "Health Unit", "AI Model", "Diagnosis Result", "Actions"]
            content.append(
                Card(
                    Div( # Div para container da tabela responsiva
                         Table(headers, rows, id="attendances-table"),
                         cls="table-container"
                    ),
                    # Adiciona Paginação
                    Pagination(
                        page=pagination.get("current_page", 1),
                        total_pages=pagination.get("total_pages", 1),
                        base_url="/attendances" # Ajuste se usar filtros na URL base da paginação
                    ) if pagination.get("total_pages", 1) > 1 else "", # Só mostra paginação se tiver mais de 1 página
                    title=f"Attendance Records ({pagination.get('total_count', 0)})"
                )
            )
        elif can_view_list: # Se for admin e não houver atendimentos
             content.append(
                Card(
                    P("No attendance records found. Please adjust filters or wait for new records.", cls="no-data"),
                    title="Attendance Records"
                )
            )
    # Nota: Se não for admin, a tabela nem é renderizada.

    # CSS (Combinado e ajustado)
    content.append(
        Style("""
            /* --- Estilos Gerais da Página --- */
            .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border-color, #e5e7eb); padding-bottom: 1rem; }
            .page-header h1 { margin-bottom: 0; }
            .page-actions .btn { padding: 0.6rem 1.2rem; font-weight: 500; }
            .no-data { text-align: center; padding: 2rem; color: #6b7280; }

            /* --- Estilos Filtros --- */
            .filter-card { margin-bottom: 1.5rem; background-color: #f9fafb; }
            .filter-form .filter-inputs { display: flex; flex-wrap: wrap; gap: 1.5rem; align-items: flex-end; }
            .filter-form .form-group { flex: 1; min-width: 200px; margin-bottom: 0; /* Remove margem inferior dentro do flex */ }
            .filter-form label { font-size: 0.9em; margin-bottom: 0.3rem; color: #4b5563; }
            .filter-form select { padding: 0.5rem; font-size: 0.95rem; }
            .filter-form .btn-secondary { padding: 0.55rem 1rem; font-size: 0.95rem; margin-left: 1rem; /* Espaço antes do botão */}

            /* --- Estilos Tabela e Ações --- */
            .table-container { overflow-x: auto; }
            table td { vertical-align: middle; }
            .actions-cell { display: flex; gap: 0.75rem; align-items: center; justify-content: flex-start; /* Alinha à esquerda */ white-space: nowrap; padding-left: 0.5rem; /* Pequeno espaço à esquerda */}

            /* --- Estilos Botões Ícone --- */
            .btn-icon { display: inline-flex; align-items: center; justify-content: center; padding: 0.3rem; border-radius: 50%; border: 1px solid transparent; cursor: pointer; transition: all 0.2s; }
            .btn-icon svg { width: 1em; height: 1em; vertical-align: middle; }
            .btn-view { color: #0e7490; border-color: #a5f3fc; } /* Ciano */
            .btn-view:hover { background-color: #ecfeff; border-color: #67e8f9; transform: scale(1.1); }
            .btn-edit { color: #2563eb; border-color: #bfdbfe; } /* Azul */
            .btn-edit:hover { background-color: #eff6ff; border-color: #93c5fd; transform: scale(1.1); }
            .btn-delete { color: #dc2626; border-color: #fecaca; } /* Vermelho */
            .btn-delete:hover { background-color: #fee2e2; border-color: #fca5a5; transform: scale(1.1); }

            /* --- Estilos Status/Diagnóstico --- */
            .diagnosis-correct { color: #059669; font-weight: 500; background-color: #d1fae5; padding: 0.2em 0.4em; border-radius: 0.25rem; font-size: 0.85em; margin-left: 0.3rem; vertical-align: middle; }
            .diagnosis-incorrect { color: #b91c1c; font-weight: 500; background-color: #fee2e2; padding: 0.2em 0.4em; border-radius: 0.25rem; font-size: 0.85em; margin-left: 0.3rem; vertical-align: middle;}

             /* --- Estilos Paginação --- */
            .pagination { display: flex; list-style: none; padding: 0; margin: 1.5rem 0 0.5rem 0; justify-content: center; }
            .pagination li { margin: 0 0.25rem; }
            .pagination li a { display: block; padding: 0.5rem 0.75rem; border: 1px solid #e5e7eb; border-radius: 0.25rem; text-decoration: none; color: #374151; background-color: white; }
            .pagination li a:hover { background-color: #f9fafb; }
            .pagination li.active a { background-color: var(--primary-color, #2563eb); color: white; border-color: var(--primary-color, #2563eb); font-weight: 500; }
            .pagination li a.disabled { color: #9ca3af; pointer-events: none; background-color: #f9fafb; }
        """)
    )

    # *** ALTERADO: Passar user_profile para MainLayout ***
    return MainLayout(page_title, *content, active_page="attendances", user_profile=user_profile)