# web/pages/health_units/list.py
from fasthtml.common import *
from datetime import datetime
from components.layout import MainLayout
from components.ui import Card, Table, Alert # Removido Pagination se não estiver usando/implementado
from services.health_units_service import HealthUnitsService
from services.auth_service import AuthService
# Para usar SVG embutido precisamos do NotStr
from fasthtml.components import NotStr

# --- Definições dos Ícones SVG ---
# Ícone de Lápis (Editar) - Exemplo do Bootstrap Icons
edit_icon_svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-square" viewBox="0 0 16 16">
  <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
  <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5z"/>
</svg>
"""

# Ícone de Lixeira (Deletar) - Exemplo do Bootstrap Icons
delete_icon_svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash3-fill" viewBox="0 0 16 16">
  <path d="M11 1.5v1h3.5a.5.5 0 0 1 0 1h-.538l-.853 10.66A2 2 0 0 1 11.115 16h-6.23a2 2 0 0 1-1.994-1.84L2.038 3.5H1.5a.5.5 0 0 1 0-1h3.5v-1A1.5 1.5 0 0 1 6.5 0h3A1.5 1.5 0 0 1 11 1.5m-5 0v1h4v-1a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5M4.5 5.029l.5 8.5a.5.5 0 1 0 .998-.06l-.5-8.5a.5.5 0 1 0-.998.06m6.53-.528a.5.5 0 0 0-.528.47l-.5 8.5a.5.5 0 0 0 .998.058l.5-8.5a.5.5 0 0 0-.47-.528M8 4.5a.5.5 0 0 0-.5.5v8.5a.5.5 0 0 0 1 0V5a.5.5 0 0 0-.5-.5"/>
</svg>
"""
# --------------------------------

async def health_units_list_page(request):
    """Renderiza a página de listagem de unidades de saúde com ícones de ação"""
    session = request.scope.get("session", {})
    token = session.get('token')
    user_id = session.get('user_id')
    user_profile = session.get('user_profile')

    # Verifica se o usuário pode gerenciar unidades de saúde
    can_manage = AuthService.is_admin(user_profile)

    # Obtém a lista de unidades de saúde
    result = await HealthUnitsService.get_health_units(token)

    page_title = "Health Units Management"
    content = []

    # Adiciona notificação caso haja uma mensagem na sessão
    if 'message' in session:
        message = session.pop('message')
        message_type = session.pop('message_type', 'success')
        content.append(Alert(message, type=message_type))

    # Cabeçalho da página
    content.append(
        Div(
            H1(page_title),
            Div(
                # Botão "Add Health Unit" continua com texto
                A("Add Health Unit", href="/health-units/add", cls="btn btn-primary"), # Usei btn-primary para destaque
                cls="page-actions"
            ) if can_manage else "",
            cls="page-header"
        )
    )

    # Conteúdo principal
    if result["success"]:
        health_units = result["health_units"]

        if health_units:
            # Prepara as linhas da tabela
            rows = []
            for unit in health_units:
                # Formata a data (opcional, mas recomendado)
                created_at_str = unit.get("created_at", "")
                try:
                    # Tenta formatar se for uma string ISO válida
                    if isinstance(created_at_str, str):
                         created_at_dt = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                         created_at_formatted = created_at_dt.strftime("%d/%m/%Y")
                    else:
                         created_at_formatted = created_at_str # Mantém como está se não for string
                except ValueError:
                    created_at_formatted = created_at_str # Mantém original em caso de erro de formato

                # Células de dados
                cells = [
                    Td(unit.get("name", "")),
                    Td(unit.get("cnpj", "")),
                    Td(Span(unit.get("status", "").capitalize(), cls=f"status-{unit.get('status', 'inactive')}")), # Adiciona classe para status
                    Td(created_at_formatted) # Usa a data formatada
                ]

                # Célula de Ações com Ícones
                if can_manage:
                    can_edit_delete = user_profile == "general_administrator" or unit.get("admin_id") == user_id
                    if can_edit_delete:
                        actions = Td(
                            A( # Link de Edição com Ícone
                               NotStr(edit_icon_svg), # Usa NotStr para renderizar o SVG
                               href=f"/health-units/edit/{unit['id']}",
                               cls="btn-icon btn-edit", # Classes para estilização do ícone
                               title="Edit Health Unit" # Tooltip para acessibilidade
                            ),
                            A( # Link de Deleção com Ícone e HTMX
                               NotStr(delete_icon_svg), # Usa NotStr para renderizar o SVG
                               hx_post=f"/health-units/delete/{unit['id']}", # Rota do frontend para POST
                               hx_target=f"#unit-row-{unit['id']}",
                               hx_swap="outerHTML",
                               hx_confirm="Tem certeza que deseja excluir esta unidade de saúde?",
                               cls="btn-icon btn-delete", # Classes para estilização do ícone
                               title="Delete Health Unit" # Tooltip para acessibilidade
                            ),
                            cls="actions-cell" # Classe para alinhar os ícones na célula
                        )
                        cells.append(actions)
                    else:
                        cells.append(Td(" ")) # Célula de ações vazia se não puder gerenciar
                else:
                     # Adiciona uma célula vazia se o usuário não puder gerenciar
                     # para manter o número de colunas consistente
                     cells.append(Td(" "))


                # Adiciona um ID à linha da tabela (tr) para ser alvo do hx_target
                rows.append(Tr(*cells, id=f"unit-row-{unit['id']}"))

            # Define as colunas da tabela
            headers = ["Name", "CNPJ", "Status", "Created At", "Actions"] # Adiciona cabeçalho "Actions"

            # Cria a tabela
            content.append(
                Card(
                    Table(headers, rows, id="health-units-table"), # Componente Table estilizado
                    title=f"Health Units List ({len(health_units)})"
                )
            )
        else:
            content.append(
                Card(
                    P("No health units found.", cls="no-data"),
                    title="Health Units List"
                )
            )
    else:
        content.append(
            Card(
                Alert(result.get("message", "Error loading health units"), type="error"),
                title="Health Units List"
            )
        )

    # Adiciona CSS específico da página, incluindo estilos para os ícones
    content.append(
        Style("""
            .page-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
                border-bottom: 1px solid var(--border-color, #e5e7eb); /* Adiciona linha separadora */
                padding-bottom: 1rem;
            }
            .page-header h1 {
                 margin-bottom: 0; /* Remove margem inferior do H1 */
            }
            .page-actions .btn { /* Estilo para o botão 'Add Health Unit' */
                padding: 0.6rem 1.2rem; /* Aumenta um pouco o padding */
                font-weight: 500;
            }
            .no-data {
                text-align: center;
                padding: 2rem;
                color: #6b7280;
            }
            .table-container { /* Garante que a tabela seja responsiva */
                overflow-x: auto;
            }
            /* Estilos para Célula de Ações */
            .actions-cell {
                display: flex;
                gap: 0.75rem; /* Espaço entre os ícones */
                align-items: center;
                justify-content: center; /* Centraliza os ícones na célula */
                white-space: nowrap; /* Impede que os ícones quebrem linha */
            }
            /* Estilos para Botões de Ícone */
            .btn-icon {
                display: inline-flex; /* Para alinhar o SVG corretamente */
                align-items: center;
                justify-content: center;
                padding: 0.3rem; /* Padding pequeno ao redor do ícone */
                border-radius: 50%; /* Faz o fundo redondo */
                border: 1px solid transparent; /* Borda inicial transparente */
                cursor: pointer;
                transition: background-color 0.2s, border-color 0.2s, transform 0.1s;
            }
            .btn-icon svg {
                width: 1em; /* Tamanho do ícone relativo ao font-size */
                height: 1em;
                vertical-align: middle; /* Alinha o SVG verticalmente */
            }
            /* Cores e Hover - Editar */
            .btn-edit {
                color: #2563eb; /* Azul (cor primária) */
                border-color: #bfdbfe; /* Borda azul clara */
            }
            .btn-edit:hover {
                background-color: #eff6ff; /* Fundo azul muito claro no hover */
                border-color: #93c5fd;
                transform: scale(1.1); /* Efeito leve de zoom */
            }
             /* Cores e Hover - Deletar */
            .btn-delete {
                color: #dc2626; /* Vermelho (cor de perigo) */
                border-color: #fecaca; /* Borda vermelha clara */
            }
            .btn-delete:hover {
                background-color: #fee2e2; /* Fundo vermelho muito claro no hover */
                border-color: #fca5a5;
                transform: scale(1.1); /* Efeito leve de zoom */
            }
            /* Estilos para o Status */
            .status-active {
                color: #059669; /* Verde escuro */
                font-weight: 500;
                background-color: #d1fae5; /* Fundo verde claro */
                padding: 0.2em 0.6em;
                border-radius: 0.25rem;
                display: inline-block; /* Para o background funcionar */
            }
            .status-inactive {
                color: #71717a; /* Cinza escuro */
                font-weight: 500;
                background-color: #f4f4f5; /* Fundo cinza claro */
                padding: 0.2em 0.6em;
                border-radius: 0.25rem;
                display: inline-block; /* Para o background funcionar */
            }
            /* Garante alinhamento vertical nas células da tabela */
            table td {
                vertical-align: middle;
            }
        """)
    )

    # Renderiza o layout principal com o conteúdo da lista de unidades
    return MainLayout(page_title, *content, active_page="health-units")