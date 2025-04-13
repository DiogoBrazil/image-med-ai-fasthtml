# web/pages/health_units/edit.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Alert
from components.forms import HealthUnitForm # Usaremos o mesmo form de 'add'
from services.health_units_service import HealthUnitsService
from services.auth_service import AuthService
from services.users_service import UsersService # Para buscar admins

async def edit_health_unit_page(request):
    """Renderiza a página para editar uma unidade de saúde existente"""
    session = request.scope.get("session", {})
    token = session.get('token')
    current_user_id = session.get('user_id')
    current_user_profile = session.get('user_profile')

    is_general_admin = (current_user_profile == "general_administrator")

    # Obtém o ID da unidade de saúde a ser editada da URL
    path_params = request.path_params
    unit_id = path_params.get('unit_id')

    if not unit_id:
        session['message'] = "Health unit ID is missing"
        session['message_type'] = "error"
        return RedirectResponse('/health-units', status_code=303)

    # --- Busca dados da Unidade ---
    unit_result = await HealthUnitsService.get_health_unit_by_id(token, unit_id)
    if not unit_result.get("success"):
        session['message'] = unit_result.get("message", "Health unit not found")
        session['message_type'] = "error"
        return RedirectResponse('/health-units', status_code=303)
    health_unit = unit_result.get("health_unit")

    # --- Verifica Permissão (frontend inicial) ---
    # Admin comum só pode editar unidades associadas a ele
    if not is_general_admin and health_unit.get("admin_id") != current_user_id:
        session['message'] = "You do not have permission to edit this health unit."
        session['message_type'] = "error"
        return RedirectResponse('/health-units', status_code=303)

    error_message = None
    administrators_list = None # Lista de admins para o select

    # --- Lógica para GET ---
    if request.method == "GET":
        if is_general_admin:
            # Busca a lista de admins para o select
            admin_result = await UsersService.get_administrators(token)
            if admin_result.get("success"):
                administrators_list = admin_result.get("administrators", [])
                if not administrators_list:
                    error_message = "Warning: No administrators found to assign."
            else:
                error_message = f"Could not load administrators list: {admin_result.get('message', 'Unknown error')}"
                # Decide se quer mostrar o form mesmo assim ou redirecionar

    # --- Lógica para POST ---
    if request.method == "POST":
        form_data = await request.form()
        unit_name = form_data.get("name")
        unit_cnpj = form_data.get("cnpj")
        unit_status = form_data.get("status", "active")
        final_admin_id = None

        # Determina o admin_id a ser enviado
        if is_general_admin:
            final_admin_id = form_data.get("admin_id") # Pega do select
            if not final_admin_id:
                error_message = "Please select an administrator."
        else: # Admin comum
            final_admin_id = current_user_id # Mantém o admin atual (ele mesmo)

        # Validação
        if not error_message and not all([unit_name, unit_cnpj]):
            error_message = "Name and CNPJ are required."

        # Se não houver erros, tenta atualizar
        if not error_message:
            unit_data = {
                "name": unit_name,
                "cnpj": unit_cnpj,
                "status": unit_status,
                "admin_id": final_admin_id # Envia o admin_id correto
            }

            # Chama o serviço de atualização
            update_result = await HealthUnitsService.update_health_unit(token, unit_id, unit_data)

            if update_result.get("success"):
                session['message'] = "Health unit updated successfully"
                session['message_type'] = "success"
                return RedirectResponse('/health-units', status_code=303)
            else:
                error_message = update_result.get("message", "Error updating health unit")

        # Se POST falhou e for general admin, precisa buscar admins de novo para re-renderizar
        if error_message and is_general_admin:
            admin_result = await UsersService.get_administrators(token)
            if admin_result.get("success"):
                administrators_list = admin_result.get("administrators", [])


    # --- Renderização da Página ---
    page_title = f"Edit Health Unit: {health_unit.get('name', 'N/A')}"
    content = [
        Div(
            H1(page_title),
            # Botão Voltar opcional
            Div(A("Back to List", href="/health-units", cls="btn btn-secondary"), cls="page-actions-header"),
            cls="page-header"
        )
    ]

    if error_message:
        content.append(Alert(error_message, type="error"))

    # Cria o formulário de edição
    # Passa a unidade para preencher os campos
    # Passa a lista de administradores APENAS se for general_administrator
    form = HealthUnitForm(
        action=f"/health-units/edit/{unit_id}", # Action aponta para a própria URL de edição
        unit=health_unit, # Dados atuais para preencher o form
        administrators=administrators_list if is_general_admin else None,
        # Não passa admin_id aqui, o form decide mostrar select ou nada
    )

    content.append(
        Card(
            form,
            title="Update Health Unit Information"
        )
    )

    # Adiciona o CSS (reutilizando o CSS da página de adicionar)
    content.append(
        Style("""
            .page-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
                border-bottom: 1px solid var(--border-color, #e5e7eb);
                padding-bottom: 1rem;
            }
             .page-header h1 { margin-bottom: 0; }
            .page-actions-header .btn { /* Estilo para o botão Voltar */
                 padding: 0.5rem 1rem;
                 font-size: 0.9rem;
            }
            /* Estilos gerais do formulário (reutilizados) */
            .form-group {
                 margin-bottom: 1.25rem; /* Aumenta um pouco o espaço */
            }
            .form-group label {
                display: block;
                margin-bottom: 0.5rem;
                font-weight: 500;
                color: #374151; /* Cinza um pouco mais escuro */
            }
            .form-group input, .form-group select, .form-group textarea {
                width: 100%;
                padding: 0.6rem 0.75rem; /* Ajusta padding */
                border: 1px solid #d1d5db;
                border-radius: 0.375rem;
                box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
                box-sizing: border-box;
                font-size: 1rem;
                line-height: 1.5; /* Melhora leitura em textarea */
            }
             .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
                 border-color: var(--primary-color, #2563eb); /* Destaca borda no foco */
                 outline: none; /* Remove outline padrão */
                 box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2); /* Adiciona sombra de foco */
            }
            /* Estilo para o botão Cancelar no final do form */
            .form-group .btn-secondary {
                 margin-left: 1rem;
            }
        """)
    )

    # Renderiza o layout principal
    return MainLayout(page_title, *content, active_page="health-units")