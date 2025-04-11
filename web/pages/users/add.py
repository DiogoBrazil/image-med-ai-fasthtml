# web/pages/users/add.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Alert
from components.forms import UserForm
from services.users_service import UsersService
from services.auth_service import AuthService

async def add_user_page(request):
    """Renderiza a página para adicionar usuário"""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_id = session.get('user_id')
    user_profile = session.get('user_profile')
    
    # Verifica se o usuário atual pode adicionar usuários
    if not AuthService.is_admin(user_profile):
        session['message'] = "You don't have permission to add users"
        session['message_type'] = "error"
        return RedirectResponse('/users', status_code=303)
    
    error_message = None
    
    # Processa o formulário no POST
    if request.method == "POST":
        form_data = await request.form()
        
        # Prepara os dados do usuário
        user_data = {
            "full_name": form_data.get("full_name"),
            "email": form_data.get("email"),
            "password": form_data.get("password"),
            "profile": form_data.get("profile"),
            "status": form_data.get("status", "active")
        }
        
        # Adiciona admin_id se necessário
        if form_data.get("admin_id"):
            user_data["admin_id"] = form_data.get("admin_id")
        elif user_profile == "administrator" and user_data["profile"] == "professional":
            # Para administradores criando profissionais, adiciona o ID do admin automaticamente
            user_data["admin_id"] = user_id
        
        # Valida dados obrigatórios
        if not all([user_data["full_name"], user_data["email"], user_data["password"], user_data["profile"]]):
            error_message = "All fields are required"
        else:
            # Envia para a API
            result = await UsersService.create_user(token, user_data)
            
            if result["success"]:
                session['message'] = "User added successfully"
                session['message_type'] = "success"
                return RedirectResponse('/users', status_code=303)
            else:
                error_message = result.get("message", "Error adding user")
    
    # Prepara as opções de perfil com base no perfil do usuário atual
    available_profiles = []
    
    if user_profile == "general_administrator":
        available_profiles = [
            {"id": "administrator", "name": "Administrator"},
            {"id": "professional", "name": "Professional"}
        ]
    elif user_profile == "administrator":
        available_profiles = [
            {"id": "professional", "name": "Professional"}
        ]
    
    # Conteúdo da página
    content = [
        Div(
            H1("Add New User"),
            cls="page-header"
        )
    ]
    
    if error_message:
        content.append(Alert(error_message, type="error"))
    
    # Formulário de adição de usuário
    form = UserForm(
        action="/users/add",
        profiles=available_profiles,
        admin_id=user_id if user_profile == "administrator" else None
    )
    
    content.append(
        Card(
            form,
            title="User Information"
        )
    )
    
    # Renderiza o layout principal com o formulário
    return MainLayout("Add User", *content, active_page="users")