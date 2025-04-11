# web/pages/users/list.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Table, Alert, Pagination
from services.users_service import UsersService
from services.auth_service import AuthService

async def users_list_page(request):
    """Renderiza a página de listagem de usuários"""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_profile = session.get('user_profile')
    
    # Verifica se o usuário atual pode gerenciar usuários
    can_manage = AuthService.is_admin(user_profile)
    
    # Obtém a lista de usuários
    result = await UsersService.get_users(token)
    
    content = []
    
    # Adiciona notificação caso haja uma mensagem na sessão
    if 'message' in session:
        message = session.pop('message')
        message_type = session.pop('message_type', 'success')
        content.append(Alert(message, type=message_type))
    
    # Cabeçalho da página
    content.append(
        Div(
            H1("Users Management"),
            Div(
                A("Add User", href="/users", cls="btn"),
                cls="actions"
            ) if can_manage else "",
            cls="page-header"
        )
    )
    
    # Conteúdo principal
    if result["success"]:
        users = result["users"]
        
        if users:
            # Prepara as linhas da tabela
            rows = []
            for user in users:
                # Adiciona células na linha para cada propriedade do usuário
                cells = [
                    Td(user.get("full_name", "")),
                    Td(user.get("email", "")),
                    Td(user.get("profile", "").replace("_", " ").title()),
                    Td(user.get("status", ""))
                ]
                
                # Adiciona botões de ação
                if can_manage:
                    actions = Td(
                        A("Edit", href=f"/users/{user['id']}", cls="btn-sm"),
                        " ",
                        A("Delete", href=f"/users/{user['id']}", 
                          cls="btn-sm btn-danger",
                          hx_confirm="Are you sure you want to delete this user?"),
                    )
                    cells.append(actions)
                
                rows.append(Tr(*cells))
            
            # Define as colunas da tabela
            headers = ["Name", "Email", "Profile", "Status"]
            if can_manage:
                headers.append("Actions")
            
            content.append(
                Card(
                    Table(headers, rows),
                    title="Users List"
                )
            )
        else:
            content.append(
                Card(
                    P("No users found.", cls="no-data"),
                    title="Users List"
                )
            )
    else:
        content.append(
            Card(
                Alert(result.get("message", "Error loading users"), type="error"),
                title="Users List"
            )
        )
    
    # Adiciona CSS específico da página
    content.append(
        Style("""
            .actions {
                display: flex;
                justify-content: flex-end;
            }
            .page-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }
            .btn-sm {
                padding: 0.25rem 0.5rem;
                font-size: 0.875rem;
            }
            .no-data {
                text-align: center;
                padding: 2rem;
                color: #6b7280;
            }
        """)
    )
    
    # Renderiza o layout principal com o conteúdo da lista de usuários
    return MainLayout("Users", *content, active_page="users")