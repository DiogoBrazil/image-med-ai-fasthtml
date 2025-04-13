# web/app.py (Estrutura Corrigida Sugerida)

from fasthtml.common import *
from config import SERVER_HOST, SERVER_PORT, SESSION_SECRET_KEY
from middlewares.auth_middleware import auth_middleware
from starlette.responses import Response as HTTPResponse, RedirectResponse

# Importa páginas
from pages.auth.login import login_page
from pages.auth.logout import logout_page
from pages.dashboard.dashboard import dashboard_page
from pages.users.list import users_list_page
from pages.users.add import add_user_page
from pages.users.edit import edit_user_page
from pages.attendances.list import attendances_list_page
from pages.attendances.add import add_attendance_page
from pages.attendances.edit import edit_attendance_page
from pages.attendances.view import view_attendance_page
from pages.health_units.list import health_units_list_page
from pages.health_units.add import add_health_unit_page
from pages.health_units.edit import edit_health_unit_page
from services.health_units_service import HealthUnitsService
from services.users_service import UsersService
from services.attendance_service import AttendanceService
from pages.predict.respiratory import prediction_respiratory_page
from pages.predict.breast_cancer import prediction_breast_cancer_page
from pages.predict.tuberculosis import prediction_tuberculosis_page
from pages.predict.osteoporosis import prediction_osteoporosis_page


# Removi a importação duplicada de delete, se houver uma página de deleção, importe-a corretamente

# Define os caminhos que devem ignorar a autenticação
# Adicionei '/live-reload' que estava no seu middleware original
skip_paths = ['/login', '/logout', '/static', '/favicon.ico', '/live-reload']

# Cria o objeto beforeware com a função auth_middleware
beforeware = Beforeware(auth_middleware, skip=skip_paths)

# Cria a aplicação FastHTML com o beforeware
app = FastHTML(
    debug=True,
    secret_key=SESSION_SECRET_KEY,
    before=beforeware,
    # Adicione outros hdrs globais se necessário, como CSS do layout
    # hdrs=(...)
)

# Define as rotas
rt = app.route

# --- Rotas Públicas ---
@rt('/login')
async def get_login(request):
    return await login_page(request)

@rt('/login')
async def post_login(request):
    return await login_page(request) # A mesma função lida com GET (mostrar form) e POST (processar login)

@rt('/logout')
async def get_logout(request):
    return await logout_page(request)

# --- Rotas Protegidas ---

# Dashboard
@rt('/')
async def get_dashboard(request):
    return await dashboard_page(request)

# Usuários (Users)
@rt('/users')
async def get_users(request):
    return await users_list_page(request)

@rt('/users/add')
async def post_add_user(request):
    return await add_user_page(request) # Processa o formulário de adição

@rt('/users/edit/{user_id}')
async def get_edit_user(request):
    return await edit_user_page(request) # Página do formulário de edição

@rt('/users/edit/{user_id}') # CORREÇÃO: A rota POST deve ser para /edit/{user_id}
async def post_edit_user(request):
    return await edit_user_page(request) # Processa o formulário de edição

@rt('/users/delete/{user_id}')
async def post_delete_user(request, user_id: str):
    """Processa a requisição de deleção de usuário vinda do HTMX."""
    session = request.scope.get("session", {})
    token = session.get('token')

    if not token:
        return HTTPResponse(status_code=401, content="Not Authorized")

    # Chama o serviço para deletar o usuário
    result = await UsersService.delete_user(token, user_id)

    if result.get("success"):
        # Sucesso: Retorna resposta vazia para remover a linha via HTMX
        print(f"Usuário {user_id} deletado com sucesso via frontend.") # Log opcional
        return HTTPResponse(status_code=200, content="")
    else:
        # Falha: Redireciona com mensagem de erro
        error_message = result.get("message", "Erro ao deletar usuário.")
        print(f"Falha ao deletar usuário {user_id}: {error_message}") # Log opcional
        session['message'] = error_message
        session['message_type'] = "error"
        return HTTPResponse(status_code=200, headers={'HX-Redirect': '/users'})


# Atendimentos (Attendances)
@rt('/attendances') # Rota raiz para listar
async def get_attendances_list(request): # Nome da função mais específico
    return await attendances_list_page(request)

@rt('/attendances/add') # Rota para mostrar form de adicionar
async def get_add_attendance_form(request):
    return await add_attendance_page(request)

@rt('/attendances/add') # Rota para processar form de adicionar
async def post_add_attendance_submit(request):
    return await add_attendance_page(request) # A página lida com GET e POST

@rt('/attendances/view/{attendance_id}') # Rota para visualizar detalhes
async def get_view_attendance(request, attendance_id: str): # Adiciona tipo ao parâmetro
    # Passa o attendance_id para a função da página
    return await view_attendance_page(request) # A página pega o ID dos path_params

@rt('/attendances/edit/{attendance_id}') # Rota para mostrar form de editar
async def get_edit_attendance_form(request, attendance_id: str): # Adiciona tipo
    # Passa o attendance_id para a função da página
    return await edit_attendance_page(request) # A página pega o ID

@rt('/attendances/edit/{attendance_id}') # Rota para processar form de editar
async def post_edit_attendance_submit(request, attendance_id: str): # Adiciona tipo
     # Passa o attendance_id para a função da página
    return await edit_attendance_page(request) # A página lida com GET e POST

# ROTA PARA DELETAR ATENDIMENTO
@rt('/attendances/delete/{attendance_id}')
async def post_delete_attendance(request, attendance_id: str):
    """Processa a requisição de deleção de atendimento vinda do HTMX."""
    session = request.scope.get("session", {})
    token = session.get('token')

    if not token:
        return HTTPResponse(status_code=401, content="Not Authorized")

    # Chama o serviço para deletar
    result = await AttendanceService.delete_attendance(token, attendance_id)

    if result.get("success"):
        # Sucesso: Retorna resposta vazia para remover a linha via HTMX
        print(f"Atendimento {attendance_id} deletado com sucesso via frontend.")
        return HTTPResponse(status_code=200, content="")
    else:
        # Falha: Redireciona com mensagem de erro
        error_message = result.get("message", "Erro ao deletar atendimento.")
        print(f"Falha ao deletar atendimento {attendance_id}: {error_message}")
        session['message'] = error_message
        session['message_type'] = "error"
        return HTTPResponse(status_code=200, headers={'HX-Redirect': '/attendances'})


# Unidades de Saúde (Health Units)
@rt('/health-units')
async def get_health_units(request):
    return await health_units_list_page(request) # Listagem

@rt('/health-units/add')
async def get_add_health_unit(request):
    return await add_health_unit_page(request) # Página do formulário de adição

@rt('/health-units/add') # CORREÇÃO: POST para /add
async def post_add_health_unit(request):
    return await add_health_unit_page(request) # Processa o formulário de adição

@rt('/health-units/edit/{unit_id}') # CORREÇÃO: Path correto e método GET
async def get_edit_health_unit(request):
    return await edit_health_unit_page(request) # Página do formulário de edição

@rt('/health-units/edit/{unit_id}') # CORREÇÃO: Método POST para a rota de edição
async def post_edit_health_unit(request):
    return await edit_health_unit_page(request) # Processa o formulário de edição

@rt('/health-units/delete/{unit_id}')
async def post_delete_health_unit(request, unit_id: str):
    """Processa a requisição de deleção vinda do HTMX."""
    session = request.scope.get("session", {})
    token = session.get('token')

    # Verifica se tem token (segurança extra, middleware já deve ter barrado)
    if not token:
        # Retorna 'Não autorizado' - HTMX pode tratar ou exibir erro no console
        return HTTPResponse(status_code=401, content="Not Authorized")

    # --- Chama o serviço para deletar ---
    result = await HealthUnitsService.delete_health_unit(token, unit_id)

    if result.get("success"):
        # --- Sucesso ---
        # Retorna uma resposta vazia com status 200 OK.
        # O HTMX (com hx_target na linha e hx_swap='outerHTML')
        # interpretará isso como "substituir o alvo por nada",
        # removendo a linha da tabela dinamicamente.
        print(f"Unidade {unit_id} deletada com sucesso via frontend.") # Log opcional
        return HTTPResponse(status_code=200, content="")
    else:
        # --- Falha ---
        # Opção 1: Redirecionar com mensagem de erro (causa reload)
        error_message = result.get("message", "Erro ao deletar unidade.")
        print(f"Falha ao deletar unidade {unit_id}: {error_message}") # Log opcional
        session['message'] = error_message
        session['message_type'] = "error"
        # O cabeçalho HX-Redirect instrui o HTMX a fazer um redirect no lado do cliente
        return HTTPResponse(status_code=200, headers={'HX-Redirect': '/health-units'})


# --- ROTAS DE PREDIÇÃO ---
@rt('/predict/respiratory')
async def get_predict_respiratory(request):
    return await prediction_respiratory_page(request)
@rt('/predict/respiratory')
async def post_predict_respiratory(request):
    return await prediction_respiratory_page(request)

@rt('/predict/breast-cancer')
async def get_predict_breast_cancer(request):
    return await prediction_breast_cancer_page(request)
@rt('/predict/breast-cancer')
async def post_predict_breast_cancer(request):
    return await prediction_breast_cancer_page(request)

@rt('/predict/tuberculosis')
async def get_predict_tuberculosis(request):
    return await prediction_tuberculosis_page(request)
@rt('/predict/tuberculosis')
async def post_predict_tuberculosis(request):
    return await prediction_tuberculosis_page(request)

@rt('/predict/osteoporosis')
async def get_predict_osteoporosis(request):
    return await prediction_osteoporosis_page(request)
@rt('/predict/osteoporosis')
async def post_predict_osteoporosis(request):
    return await prediction_osteoporosis_page(request)


# Inicia o servidor
if __name__ == "__main__":
    # CORREÇÃO: importar 'serve' diretamente do módulo correto
    from fasthtml.serve import serve
    serve(host=SERVER_HOST, port=SERVER_PORT) # 'app' é detectado automaticamente no módulo atual