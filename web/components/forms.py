# web/components/forms.py
from fasthtml.common import *

# --- UserForm Atualizado ---
def UserForm(action, user=None, profiles=None, admin_id=None, is_edit=False, administrators=None, current_user_profile=None):
    """
    Formulário para criar ou editar usuários.
    - administrators: Lista de admins para seleção (usado por general_admin).
    - current_user_profile: Perfil do usuário logado para lógica condicional.
    """
    user = user or {} # Garante que user seja um dict
    is_edit = bool(user.get("id")) # Define is_edit baseado na presença de ID
    profiles = profiles or [] # Garante que profiles seja uma lista
    administrators = administrators or [] # Garante que administrators seja uma lista

    # Define se o campo profile deve ser mostrado/editável
    show_profile_field = (current_user_profile == "general_administrator") or not is_edit
    # Profile é editável apenas por GA ou na criação
    profile_is_editable = (current_user_profile == "general_administrator") or not is_edit

    # Define se o select de admin deve ser potencialmente visível
    # (A visibilidade real ainda depende do perfil selecionado ser 'professional')
    admin_select_potentially_visible = (current_user_profile == "general_administrator")

    # Esconde a senha na edição
    password_field = Input(
        id="password", name="password", type="password",
        placeholder="Leave blank to keep current password" if is_edit else "Enter password",
        # Senha não é obrigatória na edição (só se quiser mudar)
        required=not is_edit
    )

    # --- Campos do Formulário ---
    form_fields = [
        # Nome Completo
        Div(
            Label("Full Name", For="full_name"),
            Input(id="full_name", name="full_name", value=user.get("full_name", ""), required=True),
            cls="form-group"
        ),
        # Email
        Div(
            Label("Email", For="email"),
            Input(id="email", name="email", type="email", value=user.get("email", ""), required=True),
            cls="form-group"
        ),
        # Senha (só mostra na criação ou se editando o próprio perfil?) - Por ora, sempre mostra campo (opcional na edicao)
        Div(
            Label("Password", For="password"),
            password_field,
            cls="form-group"
        ) if not is_edit else Div( # Na edição, informa que não muda aqui
              Label("Password"),
              P("Password cannot be changed from this form.", cls='form-text'),
              # Poderia adicionar link para "change password" se existir
              cls="form-group"
         ),

        # --- Campo Perfil (Condicional) ---
        # Mostra o Select se for GA ou Adição. Mostra Texto se for Admin editando.
        Div(
            Label("Profile", For="profile"),
            # Select editável (para GA ou Adição)
            Select(
                Option("-- Select Profile --", value="", disabled=True, selected=not user.get("profile")),
                *[Option(p["name"], value=p["id"], selected=user.get("profile") == p["id"]) for p in profiles],
                id="profile", name="profile", required=True,
                disabled=not profile_is_editable, # Desabilita se não for editável
                onchange="toggleAdminSelect(this.value)" if admin_select_potentially_visible else None # JS só se relevante
            ) if profile_is_editable else
            # Texto não editável (para Admin editando Profissional)
            Span(user.get("profile", "N/A").replace("_", " ").title(), cls="form-text"),
            # Campo Hidden para garantir que o perfil seja enviado se não for editável? Não necessário se a API não esperar.
            # Hidden(name="profile", value=user.get("profile")) if not profile_is_editable else "",
            # Aplica classe para esconder se necessário (embora a lógica acima já controle)
            cls=f"form-group {'profile-visible' if show_profile_field else 'profile-hidden'}"
        ),

        # --- Campo Associar Administrador (Condicional) ---
        # Aparece APENAS se:
        # 1. O usuário logado for general_administrator
        # 2. A lista de administradores for passada
        # A visibilidade inicial é 'none' ou 'block' (na edição) dependendo do perfil atual do usuário, controlada pelo JS.
        Div(
            Label("Associate Administrator", For="admin_id"),
            Select(
                Option("-- Select Administrator --", value="", disabled=True, selected=not user.get("admin_id")),
                *[Option(admin["full_name"], value=admin["id"], selected=str(user.get("admin_id")) == str(admin["id"])) for admin in administrators],
                id="admin_id", name="admin_id",
                # Required será validado no backend/JS se profile for 'professional'
            ),
            id="admin-select-container",
            cls="form-group",
             # Estilo inicial será definido pelo JS no carregamento
            style="display: none;" # Começa escondido, JS ajusta
        ) if admin_select_potentially_visible and administrators else "", # Condição para INCLUIR no HTML

        # --- Campo Status ---
        Div(
            Label("Status", For="status"),
            Select(
                Option("Active", value="active", selected=user.get("status", "active") == "active"),
                Option("Inactive", value="inactive", selected=user.get("status") == "inactive"),
                id="status", name="status", required=True
            ),
            cls="form-group"
        ),
        # --- Botões de Ação ---
        Div(
            Button("Save User" if not is_edit else "Update User", type="submit", cls="btn btn-primary"),
            A("Cancel", href="/users", cls="btn btn-secondary"),
            cls="form-actions"
        )
    ]

    # Script JS para controlar a visibilidade do select de admin
    # Agora também lida com o estado inicial na edição
    # Só adiciona script se for potencialmente relevante (editor é GA)
    script_content = f"""
        function toggleAdminSelect(selectedProfile) {{
            const adminSelectContainer = document.getElementById('admin-select-container');
            // Verifica se o container existe (só existe se editor for GA e lista de admins foi passada)
            if (adminSelectContainer) {{
                if (selectedProfile === 'professional') {{
                    adminSelectContainer.style.display = 'block';
                    // Opcional: tornar obrigatório
                    // adminSelectContainer.querySelector('select').required = true;
                }} else {{
                    adminSelectContainer.style.display = 'none';
                    // Opcional: remover obrigatório
                    // adminSelectContainer.querySelector('select').required = false;
                }}
            }}
        }}

        // Chama a função uma vez no carregamento inicial para definir o estado correto na edição
        document.addEventListener('DOMContentLoaded', () => {{
            const profileSelect = document.getElementById('profile');
            if (profileSelect) {{
                 // Chama imediatamente ou com pequeno delay
                 setTimeout(() => toggleAdminSelect(profileSelect.value), 0);
            }} else {{
                 // Se o select de perfil não existe (admin editando profissional),
                 // garante que o select de admin (se existir por algum motivo) esteja escondido.
                 const adminContainer = document.getElementById('admin-select-container');
                 if(adminContainer) {{ adminContainer.style.display = 'none'; }}
            }}
        }});
    """
    script = Script(script_content) if admin_select_potentially_visible else ""

    return Form(*form_fields, script, method="post", action=action)

# --- HealthUnitForm (Mantido como antes) ---
def HealthUnitForm(action, unit=None, administrators=None, admin_id=None):
    unit = unit or {}
    is_edit = bool(unit)
    administrators = administrators or []

    form_fields = [
        Div(
            Label("Name", For="name"),
            Input(id="name", name="name", value=unit.get("name", ""), required=True),
            cls="form-group"
        ),
        Div(
            Label("CNPJ", For="cnpj"),
            Input(id="cnpj", name="cnpj", value=unit.get("cnpj", ""), required=True),
            cls="form-group"
        ),
        # Campo para selecionar administrador (mostrado apenas se a lista administrators for passada)
        # Usado por general_administrator ao criar ou editar
        Div(
            Label("Responsible Administrator", For="admin_id"),
            Select(
                Option("-- Select Administrator --", value="", disabled=True, selected=not unit.get("admin_id")),
                *[Option(admin["full_name"], value=admin["id"], selected=unit.get("admin_id") == admin["id"]) for admin in administrators],
                id="admin_id", name="admin_id", required=True # Obrigatório se mostrado
            ),
            cls="form-group"
        ) if administrators else "", # Só mostra se a lista for passada

        # Campo hidden para admin comum (quando administrators não é passado)
        # Usado por admin comum ao criar ou editar (vincula a si mesmo)
        Hidden(name="admin_id", value=admin_id) if not administrators and admin_id else "",

        Div(
            Label("Status", For="status"),
            Select(
                Option("Active", value="active", selected=unit.get("status", "active") == "active"),
                Option("Inactive", value="inactive", selected=unit.get("status") == "inactive"),
                id="status", name="status", required=True
            ),
            cls="form-group"
        ),
        Div(
            Button("Save Health Unit" if not is_edit else "Update Health Unit", type="submit", cls="btn btn-primary"),
            A("Cancel", href="/health-units", cls="btn btn-secondary"),
            cls="form-actions"
        )
    ]
    return Form(*form_fields, method="post", action=action)


# --- AttendanceForm (Mantido como antes, mas garantindo enctype) ---
def AttendanceForm(action, models=None, health_units=None, attendance=None, professional_id=None, admin_id=None):
    attendance = attendance or {}
    is_edit = bool(attendance.get("id")) # Verifica se tem ID para saber se é edição
    models = models or []
    health_units = health_units or []

    # Valor do campo correct_diagnosis para o select
    correct_diagnosis_value = attendance.get("correct_diagnosis")
    correct_diagnosis_str = ""
    if correct_diagnosis_value is True:
        correct_diagnosis_str = "true"
    elif correct_diagnosis_value is False:
        correct_diagnosis_str = "false"
    # Se for None, será string vazia ""

    form_fields = [
        # Campo hidden para ID do profissional (sempre necessário)
        Hidden(name="professional_id", value=professional_id or attendance.get("professional_id")),
        # Campo hidden para ID do admin (se disponível)
        Hidden(name="admin_id", value=admin_id or attendance.get("admin_id")),

        Div(
            Label("Health Unit", For="health_unit_id"),
            Select(
                Option("-- Select Health Unit --", value="", disabled=True, selected=not attendance.get("health_unit_id")),
                *[Option(unit["name"], value=unit["id"], selected=attendance.get("health_unit_id") == unit["id"]) for unit in health_units],
                id="health_unit_id", name="health_unit_id", required=True
            ),
            cls="form-group"
        ),
        Div(
            Label("AI Model Used", For="model_used"),
            Select(
                Option("-- Select Model --", value="", disabled=True, selected=not attendance.get("model_used")),
                *[Option(model["name"], value=model["id"], selected=attendance.get("model_used") == model["id"]) for model in models],
                id="model_used", name="model_used", required=True,
                # Desabilita na edição? Ou permite trocar o modelo?
                # disabled=is_edit # Descomente para desabilitar na edição
            ),
            cls="form-group"
        ),

        # Campo para UPLOAD de nova imagem (ou substituição)
        Div(
            Label(f"Medical Image {'(Optional: Upload to replace)' if is_edit else ''}", For="image_base64_input"),
            Input(id="image_base64_input", name="image_base64_input", type="file", accept="image/png, image/jpeg, image/gif, image/bmp, image/webp"), # Aceita tipos comuns
            cls="form-group"
        ),

        # Campo para Expected Result (Diagnóstico Esperado pelo Profissional)
        Div(
            Label("Expected Result (Your Diagnosis)", For="expected_result"),
            Input(id="expected_result", name="expected_result", value=attendance.get("expected_result", ""), placeholder="e.g., Pneumonia, Normal, Malignant"),
            cls="form-group"
        ),

        # Campo para confirmar se o diagnóstico da IA foi correto (aparece na edição)
        Div(
            Label("Was the AI Diagnosis Correct?", For="correct_diagnosis"),
            Select(
                Option("-- Select Confirmation --", value="", selected=correct_diagnosis_str == ""),
                Option("Yes", value="true", selected=correct_diagnosis_str == "true"),
                Option("No", value="false", selected=correct_diagnosis_str == "false"),
                id="correct_diagnosis", name="correct_diagnosis"
            ),
            cls="form-group"
        ) if is_edit else "", # Só mostra na edição

        # Campo hidden para enviar o resultado original do modelo (se necessário)
        Hidden(id="model_result", name="model_result", value=attendance.get("model_result", "")),

        Div(
            Label("Observations (Optional)", For="observation"),
            Textarea(attendance.get("observation", ""), id="observation", name="observation", rows="4"),
            cls="form-group"
        ),

        Div(
            Button("Save Attendance" if not is_edit else "Update Attendance", type="submit", cls="btn btn-primary"),
            A("Cancel", href="/attendances" if is_edit else "/", cls="btn btn-secondary"), # Volta pra lista (edit) ou dashboard (add)
            cls="form-actions"
        )
    ]
    # Adiciona enctype="multipart/form-data" para permitir upload de arquivo
    return Form(*form_fields, method="post", action=action, enctype="multipart/form-data")


# --- LoginForm (Mantido como antes) ---
def LoginForm(error=None):
    return Form(
        H2("Login to Med Diag AI", style="text-align: center; margin-bottom: 1.5rem;"),
        Alert(error, type="error") if error else "",
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
        Button("Login", type="submit", cls="btn btn-primary", style="width: 100%; padding: 0.8rem; font-size: 1.1rem; margin-top: 1rem;"),
        method="post",
        action="/login",
        style="max-width: 400px; margin: 2rem auto; padding: 2rem; background: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
    )