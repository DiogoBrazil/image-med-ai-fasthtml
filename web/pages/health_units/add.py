# web/pages/health_units/add.py
from fasthtml.common import *
from components.layout import MainLayout
from components.ui import Card, Alert
from components.forms import HealthUnitForm
from services.health_units_service import HealthUnitsService
from services.auth_service import AuthService
from services.users_service import UsersService # Importa o serviço de usuários

async def add_health_unit_page(request):
    """Renderiza a página para adicionar uma nova unidade de saúde"""
    session = request.scope.get("session", {})
    token = session.get('token')
    current_user_id = session.get('user_id')
    current_user_profile = session.get('user_profile')

    # Verifica se o usuário é um administrador (comum ou geral)
    if not AuthService.is_admin(current_user_profile):
        session['message'] = "Only administrators can add health units"
        session['message_type'] = "error"
        return RedirectResponse('/health-units', status_code=303)

    error_message = None
    administrators_list = None # Inicializa como None

    # --- Lógica para GET (exibição do formulário) ---
    # Busca administradores apenas se for general_administrator e a requisição for GET
    # (ou se for POST com erro, para re-renderizar o formulário)
    if request.method == "GET" and current_user_profile == "general_administrator":
        admin_result = await UsersService.get_administrators(token)
        if admin_result.get("success"):
            administrators_list = admin_result.get("administrators", [])
            if not administrators_list:
                 # Informa se não houver admins comuns para associar
                 error_message = "No administrators found to associate the health unit with."
        else:
            # Exibe um erro se não conseguir buscar os admins, mas permite continuar
            error_message = f"Could not load administrators list: {admin_result.get('message', 'Unknown error')}"
            # Considere se é melhor redirecionar ou mostrar o form sem o select neste caso

    # --- Lógica para POST (processamento do formulário) ---
    if request.method == "POST":
        form_data = await request.form()
        unit_name = form_data.get("name")
        unit_cnpj = form_data.get("cnpj")
        unit_status = form_data.get("status", "active")
        final_admin_id = None # ID do admin a ser enviado para a API

        # Determina o admin_id a ser enviado para a API
        if current_user_profile == "general_administrator":
            final_admin_id = form_data.get("admin_id") # Pega do select
            if not final_admin_id: # Validação se o select foi mostrado e um admin selecionado
                 error_message = "Please select an administrator to associate the unit with."
        elif current_user_profile == "administrator":
            final_admin_id = current_user_id # Admin comum associa a si mesmo
        else:
             # Esta verificação já foi feita no início, mas é uma segurança extra
             error_message = "Invalid user profile for this action."

        # Valida campos obrigatórios gerais
        if not error_message and not all([unit_name, unit_cnpj]):
            error_message = "Name and CNPJ are required."

        # Se não houver erros até agora, tenta criar a unidade
        if not error_message:
            unit_data = {
                "name": unit_name,
                "cnpj": unit_cnpj,
                "status": unit_status,
                "admin_id": final_admin_id # Usa o ID determinado
            }

            # Envia para a API
            result = await HealthUnitsService.create_health_unit(token, unit_data)

            if result.get("success", False):
                session['message'] = "Health unit added successfully"
                session['message_type'] = "success"
                return RedirectResponse('/health-units', status_code=303)
            else:
                error_message = result.get("message", "Error adding health unit")

        # Se chegou aqui via POST e deu erro, precisa buscar a lista de admins de novo (se for general_admin)
        # para re-renderizar o formulário corretamente com o select
        if error_message and current_user_profile == "general_administrator":
             admin_result = await UsersService.get_administrators(token)
             # Se falhar em buscar admins aqui, o select não será populado, mas o erro principal será mostrado
             if admin_result.get("success"):
                 administrators_list = admin_result.get("administrators", [])


    # --- Renderização do Conteúdo da Página (para GET e para re-renderização no POST com erro) ---
    page_title = "Add New Health Unit"
    content = [
        Div(
            H1(page_title),
            cls="page-header"
        )
    ]

    # Adiciona o alerta de erro, se houver
    if error_message:
        content.append(Alert(error_message, type="error"))

    # Cria o formulário
    # Passa a lista de administradores SOMENTE se for general_admin
    # Passa o ID do admin comum SOMENTE se for admin comum para o campo hidden
    form = HealthUnitForm(
        action="/health-units/add", # Ação do formulário
        administrators=(administrators_list if current_user_profile == "general_administrator" else None),
        admin_id=(current_user_id if current_user_profile == "administrator" else None)
        # Não passa 'unit' pois é um formulário de adição
    )

    # Adiciona o Card com o formulário ao conteúdo
    content.append(
        Card(
            form,
            title="Health Unit Information"
        )
    )

    # Adiciona o Card com as diretrizes
    content.append(
        Card(
            Div(
                H3("Guidelines for Adding Health Units"),
                P("When adding a new health unit, please ensure that:"),
                Ul(
                    Li("The name is complete and matches the official registration."),
                    Li("The CNPJ number is valid and correctly formatted (XX.XXX.XXX/XXXX-XX)."),
                    Li("The unit has proper operating licenses and meets regulatory requirements.")
                ),
                P("Once added, healthcare professionals can be assigned to this unit."),
                # Mostra instrução específica para general_administrator
                P("If you are a General Administrator, select the Administrator responsible for this unit.") if current_user_profile == "general_administrator" else "",
                cls="guidelines"
            ),
            cls="info-card"
        )
    )

    # Adiciona o CSS específico para esta página (mantido da versão anterior)
    content.append(
        Style("""
            .page-header {
                margin-bottom: 1.5rem;
            }
            .info-card {
                margin-top: 1.5rem;
                background-color: #f8fafc; /* Um cinza bem claro */
            }
            .guidelines {
                padding: 0.5rem 0;
                font-size: 0.9rem;
                color: #4b5563; /* Cinza um pouco mais escuro para texto */
            }
            .guidelines ul {
                margin-left: 1.5rem;
                margin-top: 0.5rem;
                margin-bottom: 0.5rem;
                list-style-type: disc; /* Estilo de marcador padrão */
            }
            .guidelines li {
                margin-bottom: 0.5rem;
            }
            /* Estilos adicionais para melhorar a aparência do form-group, se necessário */
            .form-group {
                 margin-bottom: 1rem; /* Espaçamento entre grupos de formulário */
            }
            .form-group label {
                display: block;
                margin-bottom: 0.5rem; /* Espaço abaixo do label */
                font-weight: 500; /* Peso da fonte para labels */
            }
            /* Ajusta inputs e selects para ocupar a largura e ter uma aparência consistente */
            .form-group input, .form-group select {
                width: 100%; /* Ocupa toda a largura disponível */
                padding: 0.6rem; /* Preenchimento interno */
                border: 1px solid #d1d5db; /* Cor da borda */
                border-radius: 0.375rem; /* Bordas arredondadas */
                box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05); /* Sombra interna sutil */
                box-sizing: border-box; /* Garante que padding não aumente a largura total */
            }
            /* Estilo para o botão Cancelar */
            .btn-secondary {
                 margin-left: 1rem; /* Espaço à esquerda do botão Cancelar */
            }
        """)
    )

    # Renderiza o layout principal com o conteúdo construído
    return MainLayout(page_title, *content, active_page="health-units")