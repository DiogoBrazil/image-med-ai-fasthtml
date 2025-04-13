# web/components/forms.py
from fasthtml.common import *
from fasthtml.components import fill_form
from datetime import datetime

def LoginForm(action="/login", error=None):
    """Formulário de login"""
    form_content = []
    
    if error:
        form_content.append(Div(error, cls="alert alert-error"))
    
    form_content.extend([
        Div(
            Label("Email", For="email"),
            Input(id="email", name="email", type="email", required=True),
            cls="form-group"
        ),
        Div(
            Label("Password", For="password"),
            Input(id="password", name="password", type="password", required=True),
            cls="form-group"
        ),
        Div(
            Button("Login", type="submit", cls="btn"),
            cls="form-group"
        )
    ])
    
    return Form(*form_content, method="post", action=action)

def UserForm(action, user=None, profiles=None, admin_id=None, is_edit=False):
    """Formulário para criar/editar usuário"""
    if profiles is None:
        profiles = [
            {"id": "professional", "name": "Professional"},
            {"id": "administrator", "name": "Administrator"},
            {"id": "general_administrator", "name": "General Administrator"}
        ]
    
    form_items = [
        Div(
            Label("Full Name", For="full_name"),
            Input(id="full_name", name="full_name", required=True),
            cls="form-group"
        ),
        Div(
            Label("Email", For="email"),
            Input(id="email", name="email", type="email", required=True),
            cls="form-group"
        )
    ]
    
    # Campo de senha (oculto na edição)
    if not is_edit:
        form_items.append(
            Div(
                Label("Password", For="password"),
                Input(id="password", name="password", type="password", required=True),
                cls="form-group"
            )
        )
    
    # Perfil
    form_items.append(
        Div(
            Label("Profile", For="profile"),
            Select(
                *[Option(p["name"], value=p["id"], selected=user and user.get("profile") == p["id"]) 
                  for p in profiles],
                id="profile", name="profile", required=True
            ),
            cls="form-group"
        )
    )
    
    # Status
    form_items.append(
        Div(
            Label("Status", For="status"),
            Select(
                Option("Active", value="active", selected=not user or user.get("status") == "active"),
                Option("Inactive", value="inactive", selected=user and user.get("status") == "inactive"),
                id="status", name="status", required=True
            ),
            cls="form-group"
        )
    )
    
    # Admin ID para profissionais
    if admin_id:
        form_items.append(Hidden(id="admin_id", name="admin_id", value=admin_id))
    
    # Botões
    form_items.append(
        Div(
            Button("Save", type="submit", cls="btn"),
            A("Cancel", href="/users", cls="btn btn-secondary", style="margin-left: 1rem;"),
            cls="form-group"
        )
    )
    
    form = Form(*form_items, method="post", action=action)
    
    # Preenche o formulário com dados existentes
    if user:
        form = fill_form(form, user)
    
    return form

def HealthUnitForm(action, unit=None, admin_id=None, administrators=None):
    """Formulário para criar/editar unidade de saúde"""
    form_items = [] # Inicializa a lista de itens do form

    # Campo Select para Administrador (APENAS SE FORNECIDO E NÃO VAZIO)
    # Verifica se a lista 'administrators' foi passada e não é None
    if administrators is not None: # Renderiza o select se a lista existir (mesmo vazia, mostra o label e select vazio)
        form_items.append(
            Div(
                Label("Associate to Administrator", For="admin_id"),
                Select(
                    Option("Select an Administrator", value="", disabled=True, selected=True),
                    # Assume que cada admin tem 'id' e 'full_name'
                    *[Option(admin.get("full_name", admin.get("id")), value=admin.get("id"))
                      for admin in administrators], # Itera sobre a lista passada
                    id="admin_id", name="admin_id", required=True # É requerido se o select for mostrado
                ),
                cls="form-group"
            )
        )
    # Se não houver lista de administradores (admin comum criando),
    # e um admin_id foi passado (o ID do próprio admin comum), adiciona como hidden.
    elif admin_id:
         form_items.append(Hidden(id="admin_id", name="admin_id", value=admin_id))
    # else: Se for general admin e a lista de admins for None (erro ao buscar),
    #       não adiciona nem select nem hidden, o erro será tratado na página.

    # Campos existentes
    form_items.extend([
        Div(
            Label("Name", For="name"),
            Input(id="name", name="name", required=True),
            cls="form-group"
        ),
        Div(
            Label("CNPJ", For="cnpj"),
            Input(id="cnpj", name="cnpj", required=True),
            cls="form-group"
        ),
        Div(
            Label("Status", For="status"),
            Select(
                Option("Active", value="active", selected=not unit or unit.get("status") == "active"),
                Option("Inactive", value="inactive", selected=unit and unit.get("status") == "inactive"),
                id="status", name="status", required=True
            ),
            cls="form-group"
        )
    ])

    # Botões (no final)
    form_items.append(
        Div(
            Button("Save", type="submit", cls="btn"),
            A("Cancel", href="/health-units", cls="btn btn-secondary", style="margin-left: 1rem;"),
            cls="form-group"
        )
    )

    form = Form(*form_items, method="post", action=action)

    # Preenche o formulário com dados existentes (para edição)
    if unit:
        unit_data_for_fill = unit.copy()
        form = fill_form(form, unit_data_for_fill)

    return form


def AttendanceForm(action, models, health_units, attendance=None, professional_id=None, admin_id=None):
    """Formulário para criar/editar atendimento"""
    form_items = [
        Div(
            Label("Health Unit", For="health_unit_id"),
            Select(
                *[Option(unit["name"], value=unit["id"], 
                        selected=attendance and attendance.get("health_unit_id") == unit["id"]) 
                 for unit in health_units],
                id="health_unit_id", name="health_unit_id", required=True
            ),
            cls="form-group"
        ),
        Div(
            Label("AI Model", For="model_used"),
            Select(
                *[Option(model["name"], value=model["id"], 
                        selected=attendance and attendance.get("model_used") == model["id"]) 
                 for model in models],
                id="model_used", name="model_used", required=True
            ),
            cls="form-group"
        ),
        Div(
            Label("Medical Image", For="image_base64"),
            Input(id="image_base64", name="image_base64", type="file", accept="image/*", required=not attendance),
            cls="form-group"
        ),
        Div(
            Label("Expected Result (optional)", For="expected_result"),
            Input(id="expected_result", name="expected_result"),
            cls="form-group"
        ),
        Div(
            Label("Observations", For="observation"),
            Textarea(id="observation", name="observation", rows=5),
            cls="form-group"
        )
    ]
    
    # Campos adicionais
    if professional_id:
        form_items.append(Hidden(id="professional_id", name="professional_id", value=professional_id))
    
    if admin_id:
        form_items.append(Hidden(id="admin_id", name="admin_id", value=admin_id))
    
    # Botões
    form_items.append(
        Div(
            Button("Save", type="submit", cls="btn"),
            A("Cancel", href="/attendances", cls="btn btn-secondary", style="margin-left: 1rem;"),
            cls="form-group"
        )
    )
    
    form = Form(*form_items, method="post", action=action, enctype="multipart/form-data")
    
    # Preenche o formulário com dados existentes
    if attendance:
        attendance_data = {k: v for k, v in attendance.items() if k != "image_base64"}
        form = fill_form(form, attendance_data)
    
    return form