from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Alert
from components.forms import UserForm
from services.users_service import UsersService # Importa UsersService
from services.auth_service import AuthService

async def add_user_page(request):
    """Renderiza a página para adicionar usuário"""
    session = request.scope.get("session", {})
    token = session.get('token')
    current_user_id = session.get('user_id') # ID do usuário logado
    current_user_profile = session.get('user_profile') # Perfil do usuário logado

    # Verifica permissão
    if not AuthService.is_admin(current_user_profile):
        session['message'] = "You don't have permission to add users"
        session['message_type'] = "error"
        return RedirectResponse('/users', status_code=303)

    error_message = None
    administrators_list = None # Lista para o select

    # --- Lógica GET: Busca administradores se for general_administrator ---
    if request.method == "GET" and current_user_profile == "general_administrator":
        try:
            admin_result = await UsersService.get_administrators(token)
            if admin_result.get("success"):
                administrators_list = admin_result.get("administrators", [])
                if not administrators_list:
                    error_message = "Warning: No administrators found to associate new professionals with."
            else:
                error_message = f"Could not load administrators list: {admin_result.get('message', 'Unknown error')}"
        except Exception as e:
            error_message = f"Error loading administrators: {e}"

    # --- Lógica POST: Processa o formulário ---
    if request.method == "POST":
        form_data = await request.form()
        # *** DEBUG: Imprimir dados recebidos do formulário ***
        print(f"--- DEBUG [User Add POST] ---")
        print(f"Current User Profile: {current_user_profile}")
        print(f"Form Data Keys Received: {list(form_data.keys())}")
        print(f"Value for 'profile' field: {form_data.get('profile')}")
        print(f"Value for 'admin_id' field: {form_data.get('admin_id')}")
        # ****************************************************

        profile_to_create = form_data.get("profile") # Perfil sendo criado
        # *** Corrigido: Ler admin_id ANTES da lógica condicional ***
        admin_id_selected = form_data.get("admin_id") # ID do admin selecionado (pode ser None)

        # Prepara os dados do usuário (sem admin_id inicialmente)
        user_data = {
            "full_name": form_data.get("full_name"),
            "email": form_data.get("email"),
            "password": form_data.get("password"),
            "profile": profile_to_create,
            "status": form_data.get("status", "active")
        }

        # Determina o admin_id final a ser enviado para a API
        final_admin_id = None
        print(f"--- DEBUG: Determining final_admin_id...")
        if current_user_profile == "administrator" and profile_to_create == "professional":
            final_admin_id = current_user_id # Admin comum vincula a si mesmo
            print(f"--- DEBUG: Case -> Admin creating Professional. final_admin_id = {final_admin_id}")
        elif current_user_profile == "general_administrator":
            print(f"--- DEBUG: Case -> General Admin creating...")
            if profile_to_create == "professional":
                # Se criando profissional, o admin_id vem do select que lemos acima
                final_admin_id = admin_id_selected
                print(f"--- DEBUG: SubCase -> GA creating Professional. final_admin_id = {final_admin_id} (from selected: {admin_id_selected})")
                if not final_admin_id: # Valida se um admin foi selecionado (não pode ser vazio)
                    error_message = "Please select an administrator to associate the professional with."
                    print(f"--- DEBUG: Validation Error! No administrator selected.")
            elif profile_to_create == "administrator":
                # Admin geral criando admin não precisa de admin_id
                final_admin_id = None
                print(f"--- DEBUG: SubCase -> GA creating Administrator. final_admin_id = None")
            else: # Segurança extra
                 error_message = "Invalid profile selected for creation."
                 print(f"--- DEBUG: SubCase -> Invalid profile selected: {profile_to_create}")
        else:
             print(f"--- DEBUG: Unexpected user profile: {current_user_profile}")


        # Adiciona admin_id aos dados SOMENTE se um valor válido foi determinado
        if final_admin_id:
            user_data["admin_id"] = final_admin_id
            print(f"--- DEBUG: Added admin_id={final_admin_id} to user_data.")
        else:
             print(f"--- DEBUG: No final_admin_id to add to user_data.")


        # Validação de campos obrigatórios gerais
        if not error_message and not all([user_data["full_name"], user_data["email"], user_data["password"], user_data["profile"]]):
            error_message = "Full Name, Email, Password, and Profile are required."
            print(f"--- DEBUG: Validation Error! Missing required fields.")

        # Se não houver erros até agora, tenta criar
        if not error_message:
            print(f"--- DEBUG: Calling UsersService.create_user with data: {user_data}") # Imprime o payload final
            result = await UsersService.create_user(token, user_data)
            if result["success"]:
                session['message'] = "User added successfully"
                session['message_type'] = "success"
                return RedirectResponse('/users', status_code=303)
            else:
                error_message = result.get("message", "Error adding user")
                print(f"--- DEBUG: API Error on create_user: {error_message}")
        else:
             print(f"--- DEBUG: Skipping API call due to validation error: {error_message}")


        # Se deu erro no POST e for general_admin, busca admins de novo para repopular o form
        if error_message and current_user_profile == "general_administrator":
            try:
                print(f"--- DEBUG: Re-fetching administrators list due to error...")
                admin_result = await UsersService.get_administrators(token)
                if admin_result.get("success"):
                    administrators_list = admin_result.get("administrators", [])
                # Não sobrescreve o erro principal se falhar aqui
            except Exception as e:
                print(f"--- DEBUG: Error re-fetching administrators: {e}")
                pass # Ignora erro na re-busca, o erro principal já está setado

    # --- Renderização da Página ---
    # (O código de renderização continua o mesmo da resposta anterior)
    # ... (código para available_profiles, page_title, content, form, Style) ...

    # Prepara as opções de perfil com base no perfil do usuário atual
    available_profiles = []
    if current_user_profile == "general_administrator":
        available_profiles = [
            {"id": "administrator", "name": "Administrator"},
            {"id": "professional", "name": "Professional"}
        ]
    elif current_user_profile == "administrator":
        available_profiles = [
            {"id": "professional", "name": "Professional"}
        ]

    page_title = "Add New User"
    content = [ Div( H1(page_title), cls="page-header" ) ]

    if error_message:
        content.append(Alert(error_message, type="error"))

    # Cria o formulário, passando a lista de administradores e o perfil atual
    form = UserForm(
        action="/users/add",
        profiles=available_profiles,
        # Só passa a lista de administradores se for general_admin
        administrators=administrators_list if current_user_profile == "general_administrator" else None,
        # Passa o perfil do usuário logado para a lógica JS/condicional no form
        current_user_profile=current_user_profile,
        # Não passa 'user' pois é adição
        # admin_id só é relevante para general_admin via select agora
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
