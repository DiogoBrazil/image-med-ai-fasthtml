# web/pages/users/list.py
from fasthtml.common import *
# Importa datetime para formatar a data
from datetime import datetime
from components.layout import MainLayout
from components.ui import Card, Table, Alert
from services.users_service import UsersService
from services.auth_service import AuthService
# Importa NotStr para renderizar SVG diretamente
from fasthtml.components import NotStr

# --- Definições dos Ícones SVG (mantidos como antes) ---
# Ícone de Lápis (Editar)
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

async def users_list_page(request):
    """Renderiza a página de listagem de usuários com lógica baseada no perfil."""
    session = request.scope.get("session", {})
    token = session.get('token')
    # *** ADICIONADO: Obter user_profile da sessão ***
    user_profile = session.get('user_profile')
    current_user_id = session.get('user_id')

    # Verifica permissão geral de gerenciamento (ambos admins podem)
    can_manage = AuthService.is_admin(user_profile)
    is_general_admin = (user_profile == "general_administrator")

    users_list = []
    result_message = None
    result_success = False
    page_title = "Users" # Título padrão

    # --- Busca de Dados Baseada no Perfil ---
    try:
        if is_general_admin:
            page_title = "All Users Management"
            result = await UsersService.get_users(token)
            if result.get("success"):
                users_list = result.get("users", [])
                result_success = True
            else:
                result_message = result.get("message", "Error loading all users")
        elif user_profile == "administrator":
            page_title = "My Professionals Management"
            # A API /professionals/list/ deve retornar apenas os profissionais do admin logado (via token)
            result = await UsersService.get_professionals_by_admin(token)
            if result.get("success"):
                users_list = result.get("professionals", []) # Espera a chave 'professionals'
                result_success = True
            else:
                result_message = result.get("message", "Error loading professionals")
        else:
            # Segurança: outros perfis não deveriam acessar, mas definimos uma mensagem
            result_message = "Access Denied"
            page_title = "Access Denied"

    except Exception as e:
        # Captura erros inesperados na chamada de serviço
        result_message = f"An unexpected error occurred: {e}"
        result_success = False
        print(f"Erro na view users_list_page: {e}") # Log do erro

    # --- Renderização do Conteúdo ---
    content = []

    # Adiciona Alerta de erro ou mensagem da sessão
    if 'message' in session:
        message = session.pop('message')
        message_type = session.pop('message_type', 'success')
        content.append(Alert(message, type=message_type))
    elif result_message and not result_success:
        content.append(Alert(result_message, type="error"))

    # Cabeçalho da página
    content.append(
        Div(
            H1(page_title),
            Div(
                A("Add User", href="/users/add", cls="btn btn-primary"),
                cls="page-actions"
            ) if can_manage else "", # Botão Add só para admins
            cls="page-header"
        )
    )

    # Tabela de Usuários (somente se a busca foi bem sucedida)
    if result_success:
        if users_list:
            rows = []
            for user in users_list:
                user_id_list = user.get("id") # ID do usuário na linha atual

                # Formata data
                created_at_str = user.get("created_at", "")
                created_at_formatted = created_at_str
                if isinstance(created_at_str, str) and created_at_str:
                    try:
                        created_at_dt = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                        created_at_formatted = created_at_dt.strftime("%d/%m/%Y")
                    except ValueError: pass # Ignora erro de formatação, mantém original

                # Células de dados
                cells = [
                    Td(user.get("full_name", "")),
                    Td(user.get("email", "")),
                    Td(user.get("profile", "").replace("_", " ").title()),
                    Td(Span(user.get("status", "").capitalize(), cls=f"status-{user.get('status', 'inactive')}")),
                    Td(created_at_formatted)
                ]

                # Lógica para permitir ações (Editar/Deletar)
                allow_action = False
                if can_manage and user_id_list != current_user_id: # Admins não agem sobre si mesmos
                    if is_general_admin:
                        # General admin pode agir sobre qualquer um (admin ou prof) listado
                        allow_action = True
                    elif user_profile == "administrator":
                        # Admin comum só vê profissionais na lista, então pode agir sobre eles
                        if user.get("profile") == "professional":
                             allow_action = True

                # Adiciona célula de ações com ícones se permitido
                if allow_action:
                    actions = Td(
                        A(NotStr(edit_icon_svg), href=f"/users/edit/{user_id_list}", cls="btn-icon btn-edit", title=f"Edit {user.get('full_name', 'User')}"),
                        A(NotStr(delete_icon_svg), hx_post=f"/users/delete/{user_id_list}", hx_target=f"#user-row-{user_id_list}", hx_swap="outerHTML", hx_confirm=f"Tem certeza que deseja excluir o usuário {user.get('full_name', '')}?", cls="btn-icon btn-delete", title=f"Delete {user.get('full_name', 'User')}"),
                        cls="actions-cell"
                    )
                    cells.append(actions)
                else:
                    cells.append(Td("")) # Célula de ações vazia

                # Adiciona ID à linha da tabela
                rows.append(Tr(*cells, id=f"user-row-{user_id_list}"))

            # Cabeçalhos da tabela
            headers = ["Name", "Email", "Profile", "Status", "Created At", "Actions"]

            # Cria Card com a Tabela
            card_title = f"{'All Users' if is_general_admin else 'My Professionals'} ({len(users_list)})"
            content.append(
                Card(
                    Table(headers, rows, id="users-table"),
                    title=card_title
                )
            )
        else:
            # Mensagem se não houver usuários/profissionais
            no_data_message = "No users found." if is_general_admin else "No professionals associated with your account."
            card_title = f"{'All Users' if is_general_admin else 'My Professionals'}"
            content.append( Card( P(no_data_message, cls="no-data"), title=card_title) )
    # else: O erro da API já foi tratado pelo Alert no início

    # Adiciona CSS (mantido como antes)
    content.append(
        Style("""
            /* --- CSS Completo (mantido da resposta anterior) --- */
            .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border-color, #e5e7eb); padding-bottom: 1rem; }
            .page-header h1 { margin-bottom: 0; }
            .page-actions .btn { padding: 0.6rem 1.2rem; font-weight: 500; }
            .no-data { text-align: center; padding: 2rem; color: #6b7280; }
            .table-container { overflow-x: auto; }
            .actions-cell { display: flex; gap: 0.75rem; align-items: center; justify-content: center; white-space: nowrap; }
            .btn-icon { display: inline-flex; align-items: center; justify-content: center; padding: 0.3rem; border-radius: 50%; border: 1px solid transparent; cursor: pointer; transition: all 0.2s; }
            .btn-icon svg { width: 1em; height: 1em; vertical-align: middle; }
            .btn-edit { color: #2563eb; border-color: #bfdbfe; }
            .btn-edit:hover { background-color: #eff6ff; border-color: #93c5fd; transform: scale(1.1); }
            .btn-delete { color: #dc2626; border-color: #fecaca; }
            .btn-delete:hover { background-color: #fee2e2; border-color: #fca5a5; transform: scale(1.1); }
            .status-active { color: #059669; font-weight: 500; background-color: #d1fae5; padding: 0.2em 0.6em; border-radius: 0.25rem; display: inline-block; }
            .status-inactive { color: #71717a; font-weight: 500; background-color: #f4f4f5; padding: 0.2em 0.6em; border-radius: 0.25rem; display: inline-block; }
            table td { vertical-align: middle; }
        """)
    )

    # *** ALTERADO: Passar user_profile para MainLayout ***
    return MainLayout(page_title, *content, active_page="users", user_profile=user_profile)