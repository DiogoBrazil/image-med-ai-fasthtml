from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Alert
from components.forms import UserForm
from services.users_service import UsersService
from services.auth_service import AuthService

async def edit_user_page(request):
    session = request.scope.get("session", {})
    token = session.get('token')
    current_user_id = session.get('user_id')
    current_user_profile = session.get('user_profile')

    path_params = request.path_params
    user_id_to_edit = path_params.get('user_id')

    # ... (código para buscar usuário e verificar permissão inicial - como antes) ...
    # --- Busca dados do usuário a ser editado ---
    user_result = await UsersService.get_user_by_id(token, user_id_to_edit)
    if not user_result["success"]:
        session['message'] = user_result.get("message", "User not found")
        session['message_type'] = "error"
        return RedirectResponse('/users', status_code=303)
    user = user_result["user"] # Dados do usuário sendo editado

    # --- Verifica Permissão Inicial ---
    can_edit = False
    if current_user_profile == "general_administrator":
        can_edit = True
    elif current_user_profile == "administrator":
        if str(user.get("id")) == str(current_user_id) or \
           (user.get("profile") == "professional" and str(user.get("admin_id")) == str(current_user_id)):
            can_edit = True
    elif str(user.get("id")) == str(current_user_id): # Outros perfis só podem editar a si mesmos
         can_edit = True

    if not can_edit:
        session['message'] = "You don't have permission to edit this user"
        session['message_type'] = "error"
        return RedirectResponse('/users', status_code=303)

    error_message = None
    administrators_list = None

    # --- Lógica GET (como antes) ---
    if request.method == "GET" and current_user_profile == "general_administrator":
        # ... (busca lista de administradores - como antes) ...
        try:
            admin_result = await UsersService.get_administrators(token)
            if admin_result.get("success"):
                administrators_list = admin_result.get("administrators", [])
                if not administrators_list:
                    error_message = "Warning: No administrators found to associate professionals with."
            else:
                error_message = f"Warning: Could not load administrators list: {admin_result.get('message', 'Unknown error')}"
        except Exception as e:
            error_message = f"Warning: Error loading administrators: {e}"


    # --- Lógica POST: Processa o formulário ---
    if request.method == "POST":
        form_data = await request.form()
        # Prepara os dados atualizados (pega apenas os que podem ser alterados)
        user_update_payload = {
            "full_name": form_data.get("full_name"),
            "email": form_data.get("email"),
            "status": form_data.get("status", "active")
        }

        # *** AJUSTE AQUI ***
        # Define o campo 'profile' no payload
        if current_user_profile == "general_administrator":
            # GA pode ter alterado o perfil no formulário
            selected_profile = form_data.get("profile")
            if selected_profile:
                 user_update_payload["profile"] = selected_profile

                 # Adiciona admin_id SOMENTE se o perfil for 'professional'
                 if selected_profile == "professional":
                     selected_admin_id = form_data.get("admin_id")
                     if not selected_admin_id:
                          error_message = "Please select an administrator when setting profile to Professional."
                     else:
                          user_update_payload["admin_id"] = selected_admin_id
                 # Se GA mudou perfil para admin/GA, garante que admin_id não seja enviado
                 # (a API deve tratar como None se 'admin_id' não estiver no payload)
                 elif "admin_id" in user_update_payload:
                      del user_update_payload["admin_id"] # Remove explicitamente

        elif current_user_profile == "administrator":
            # Admin comum está editando (só pode ser profissional associado ou ele mesmo)
            # Ele não pode mudar o perfil, então enviamos o perfil atual do usuário sendo editado.
            # Se for ele mesmo, usa o perfil dele. Se for profissional, envia 'professional'.
            if str(user.get("id")) == str(current_user_id):
                 user_update_payload["profile"] = "administrator" # Editando a si mesmo
            elif user.get("profile") == "professional":
                 user_update_payload["profile"] = "professional" # Editando profissional associado
            # Não precisa enviar admin_id aqui, pois ele não pode mudar a associação

        # Se o usuário editando for 'professional' (editando a si mesmo)
        elif current_user_profile == "professional":
             user_update_payload["profile"] = "professional" # Envia o próprio perfil


        # Valida dados gerais (nome, email, status)
        if not error_message and not all([user_update_payload.get("full_name"), user_update_payload.get("email"), user_update_payload.get("status")]):
             error_message = "Full Name, Email, and Status are required."
             # Remove profile se deu erro aqui, para evitar enviar perfil incorreto? Ou deixa? Melhor deixar.
        # Adicione outras validações se necessário


        # Se não houver erros, envia para a API
        if not error_message:
            # Remove chaves com valor None do payload antes de enviar?
            # A API já faz exclude_unset=True, então não é estritamente necessário.
            final_payload = user_update_payload # Usamos o payload como está
            print(f"--- DEBUG [User Edit POST] Payload to send: {final_payload}") # DEBUG

            result = await UsersService.update_user(token, user_id_to_edit, final_payload)

            if result.get("success", False):
                session['message'] = "User updated successfully"
                session['message_type'] = "success"
                redirect_url = '/users' if AuthService.is_admin(current_user_profile) else '/'
                return RedirectResponse(redirect_url, status_code=303)
            else:
                error_message = result.get("message", "Error updating user")
                print(f"--- DEBUG [User Edit POST] API Error: {error_message}") # DEBUG

        # Se deu erro no POST e editor for general_admin, busca admins de novo
        if error_message and current_user_profile == "general_administrator":
             # ... (código para rebuscar administradores - como antes) ...
             try:
                admin_result = await UsersService.get_administrators(token)
                if admin_result.get("success"):
                    administrators_list = admin_result.get("administrators", [])
             except Exception: pass


    # --- Renderização da Página (como antes) ---
    # ... (código para available_profiles, page_title, content, form, Style) ...
    # Prepara as opções de perfil com base no editor E no usuário sendo editado
    available_profiles = []
    if current_user_profile == "general_administrator":
         # GA pode mudar para qualquer perfil
        available_profiles = [
            {"id": "general_administrator", "name": "General Administrator"},
            {"id": "administrator", "name": "Administrator"},
            {"id": "professional", "name": "Professional"}
        ]
    # Admin comum não pode mudar perfil (select não será mostrado)

    page_title = f"Edit User: {user.get('full_name', user_id_to_edit)}"
    content = [ Div( H1(page_title), cls="page-header" ) ]

    # Adiciona alerta de erro (vindo do GET ou POST)
    if error_message:
        content.append(Alert(error_message, type="warning" if "Warning" in str(error_message) else "error"))

    # Cria o formulário, passando dados do usuário e condicionais
    form = UserForm(
        action=f"/users/edit/{user_id_to_edit}",
        user=user, # Dados atuais para preencher
        profiles=available_profiles, # Lista de perfis que podem ser selecionados (vazia se não for GA)
        is_edit=True,
        # Passa lista de admins SOMENTE se editor for GA
        administrators=administrators_list if current_user_profile == "general_administrator" else None,
        current_user_profile=current_user_profile # Passa perfil do editor para lógica do form
    )

    content.append( Card( form, title="User Information" ) )

    # *** RESTAURADO: Bloco <Style> para o formulário ***
    content.append(
        Style("""
            .page-header {
                margin-bottom: 1.5rem;
            }
            /* Estilos gerais do formulário (reutilizados) */
            .form-group {
                 margin-bottom: 1.25rem;
            }
            .form-group label {
                display: block;
                margin-bottom: 0.5rem;
                font-weight: 500;
                color: #374151;
            }
            .form-group input, .form-group select {
                width: 100%;
                padding: 0.6rem 0.75rem;
                border: 1px solid #d1d5db;
                border-radius: 0.375rem;
                box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
                box-sizing: border-box;
                font-size: 1rem;
                line-height: 1.5;
            }
            /* Desabilita visualmente campos que não podem ser editados */
            .form-group input[disabled], .form-group select[disabled] {
                 background-color: #f3f4f6; /* Fundo cinza claro */
                 cursor: not-allowed; /* Cursor de 'não permitido' */
                 opacity: 0.7; /* Levemente transparente */
            }
            .form-group input:focus, .form-group select:focus {
                 border-color: var(--primary-color, #2563eb);
                 outline: none;
                 box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
             }
            /* Estilos para botões de ação no formulário */
            .form-actions {
                margin-top: 1.5rem;
                padding-top: 1rem;
                border-top: 1px solid var(--border-color, #e5e7eb);
                display: flex;
                justify-content: flex-end; /* Alinha botões à direita */
                gap: 0.75rem; /* Espaço entre botões */
            }
            .form-actions .btn-secondary {
                 margin-left: 0; /* Remove margem extra se presente */
            }
        """)
    )
    # ----------------------------------------------

    return MainLayout(page_title, *content, active_page="users", user_profile=current_user_profile)
