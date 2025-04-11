# web/pages/users/edit.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Alert
from components.forms import UserForm
from services.users_service import UsersService
from services.auth_service import AuthService

async def edit_user_page(request):
    """Renderiza a página para editar usuário"""
    session = request.scope.get("session", {})
    token = session.get('token')
    current_user_id = session.get('user_id')
    current_user_profile = session.get('user_profile')
    
    # Obtém o ID do usuário a ser editado da URL
    path_params = request.path_params
    user_id = path_params.get('user_id')
    
    if not user_id:
        session['message'] = "User ID is missing"
        session['message_type'] = "error"
        return RedirectResponse('/users', status_code=303)
    
    # Verifica se o usuário atual pode editar o usuário especificado
    if not AuthService.is_admin(current_user_profile) and user_id != current_user_id:
        session['message'] = "You don't have permission to edit this user"
        session['message_type'] = "error"
        return RedirectResponse('/users', status_code=303)
    
    # Obtém os dados do usuário a ser editado
    user_result = await UsersService.get_user_by_id(token, user_id)
    
    if not user_result["success"]:
        session['message'] = user_result.get("message", "User not found")
        session['message_type'] = "error"
        return RedirectResponse('/users', status_code=303)
    
    user = user_result["user"]
    error_message = None
    
    # Processa o formulário no POST
    if request.method == "POST":
        form_data = await request.form()
        
        # Prepara os dados atualizados do usuário
        user_data = {
            "full_name": form_data.get("full_name"),
            "email": form_data.get("email"),
            "profile": form_data.get("profile"),
            "status": form_data.get("status", "active")
        }
        
        # Adiciona admin_id se estiver presente no formulário
        if form_data.get("admin_id"):
            user_data["admin_id"] = form_data.get("admin_id")
        
        # Valida dados obrigatórios
        if not all([user_data["full_name"], user_data["email"], user_data["profile"]]):
            error_message = "All fields are required"
        else:
            # Verifica se o usuário está tentando alterar seu próprio perfil (não é permitido)
            if user_id == current_user_id and user_data["profile"] != user["profile"]:
                error_message = "You cannot change your own profile type"
            else:
                # Envia para a API
                result = await UsersService.update_user(token, user_id, user_data)
                
                if result["success"]:
                    session['message'] = "User updated successfully"
                    session['message_type'] = "success"
                    return RedirectResponse('/users', status_code=303)
                else:
                    error_message = result.get("message", "Error updating user")
    
    # Prepara as opções de perfil com base no perfil do usuário atual
    available_profiles = []
    
    if current_user_profile == "general_administrator":
        available_profiles = [
            {"id": "general_administrator", "name": "General Administrator"},
            {"id": "administrator", "name": "Administrator"},
            {"id": "professional", "name": "Professional"}
        ]
    elif current_user_profile == "administrator":
        available_profiles = [
            {"id": "administrator", "name": "Administrator"},
            {"id": "professional", "name": "Professional"}
        ]
    else:  # professional
        available_profiles = [
            {"id": "professional", "name": "Professional"}
        ]
    
    # Conteúdo da página
    content = [
        Div(
            H1(f"Edit User: {user['full_name']}"),
            cls="page-header"
        )
    ]
    
    if error_message:
        content.append(Alert(error_message, type="error"))
    
    # Formulário de edição de usuário
    form = UserForm(
        action=f"/users/edit/{user_id}",
        user=user,
        profiles=available_profiles,
        admin_id=user.get("admin_id"),
        is_edit=True
    )
    
    content.append(
        Card(
            form,
            title="User Information"
        )
    )
    
    # CSS específico da página
    content.append(
        Style("""
            .page-header {
                margin-bottom: 1.5rem;
            }
        """)
    )
    
    # Renderiza o layout principal com o formulário
    return MainLayout("Edit User", *content, active_page="users")