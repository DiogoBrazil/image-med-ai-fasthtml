from fasthtml.common import *
from config import SERVER_HOST, SERVER_PORT, SESSION_SECRET_KEY
from middlewares.auth_middleware import auth_middleware

# Importa páginas
from pages.auth.login import login_page
from pages.auth.logout import logout_page
from pages.dashboard.dashboard import dashboard_page
from pages.users.list import users_list_page
from pages.users.add import add_user_page
from pages.users.edit import edit_user_page
from pages.attendances.add import add_attendance_page
from pages.attendances.edit import edit_attendance_page
from pages.attendances.list import attendances_list_page
from pages.attendances.view import view_attendance_page
from pages.health_units.add import add_health_unit_page
from pages.health_units.edit import edit_health_unit_page
from pages.health_units.list import health_units_list_page

# Define os caminhos que devem ignorar a autenticação
skip_paths = ['/login', '/logout', '/static', '/favicon.ico']

# Cria o objeto beforeware com a função auth_middleware
beforeware = Beforeware(auth_middleware, skip=skip_paths)

# Cria a aplicação FastHTML com o beforeware
app = FastHTML(
    debug=True,
    secret_key=SESSION_SECRET_KEY,
    before=beforeware
)

# Define as rotas
rt = app.route

# Rotas públicas
@rt('/login')
async def get(request):
    return await login_page(request)

@rt('/login')
async def post(request):
    return await login_page(request)

@rt('/logout')
async def get(request):
    return await logout_page(request)

# Rotas protegidas
@rt('/')
async def get(request):
    return await dashboard_page(request)


@rt('/users')
async def get(request):
    return await users_list_page(request)

@rt('/users/add')
async def get(request):
    return await add_user_page(request)

@rt('/users/add')
async def post(request):
    return await add_user_page(request)

@rt('/users/edit/{user_id}')
async def get(request):
    return await edit_user_page(request)

@rt('/users/{user_id}')
async def post(request):
    return await edit_user_page(request)

@rt('/attendances/add')
async def get(request):
    return await add_attendance_page(request)

@rt('/attendances')
async def post(request):
    return await add_attendance_page(request)

@rt('/attendances/{attendance_id}')
async def get(request):
    return await edit_attendance_page(request)

@rt('/attendances/{attendance_id}')
async def post(request):
    return await edit_attendance_page(request)

@rt('/attendances')
async def get(request):
    return await attendances_list_page(request)

@rt('/attendances/view/{attendance_id}')
async def get(request):
    return await view_attendance_page(request)

@rt('/health-units')
async def get(request):
    return await add_health_unit_page(request)

@rt('/health-units')
async def post(request):
    return await add_health_unit_page(request)

@rt('/health-units')
async def get(request):
    return await health_units_list_page(request)

@rt('/health-units{unit_id}')
async def get(request):
    return await edit_health_unit_page(request)

@rt('/health-units/{unit_id}')
async def post(request):
    return await edit_health_unit_page(request)

# Inicia o servidor
if __name__ == "__main__":
    from fasthtml.server import serve
    serve(app=app, host=SERVER_HOST, port=SERVER_PORT)