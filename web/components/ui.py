# web/components/ui.py
from fasthtml.common import *


_OriginalHtmlTable = Table

def Card(*content, title=None, footer=None, cls=""):
    """Componente Card"""
    card_content = []
    
    if title:
        card_content.append(Header(H2(title), cls="card-header"))
    
    card_content.append(Div(*content, cls="card-body"))
    
    if footer:
        card_content.append(Footer(footer, cls="card-footer"))
    
    return Div(*card_content, cls=f"card {cls}")

def Alert(message, type="info"):
    """Componente de alerta"""
    return Div(message, cls=f"alert alert-{type}")


def Table(headers, rows, id=None, cls=""): # Sua função wrapper customizada
    """Componente para renderizar uma tabela HTML estilizada."""

    # Cria a tabela HTML *usando a referência original*
    actual_html_table = _OriginalHtmlTable(
        Thead(
            Tr(*[Th(header) for header in headers])
        ),
        Tbody(*rows),
        id=id # Passa o id para a tag <table> interna, se fornecido
    )

    # Retorna a tabela HTML dentro das suas Divs de estilização
    return Div(
        Div(
            actual_html_table, # Usa a tabela HTML criada
            cls="table-responsive"
        ),
        cls=f"table-container {cls}"
    )

def Pagination(page, total_pages, base_url):
    """Componente de paginação"""
    if total_pages <= 1:
        return ""
    
    items = []
    
    # Botão anterior
    if page > 1:
        items.append(Li(A("Previous", href=f"{base_url}?page={page-1}")))
    else:
        items.append(Li(A("Previous", href="#", cls="disabled")))
    
    # Páginas
    for i in range(max(1, page-2), min(total_pages+1, page+3)):
        if i == page:
            items.append(Li(A(i, href=f"{base_url}?page={i}"), cls="active"))
        else:
            items.append(Li(A(i, href=f"{base_url}?page={i}")))
    
    # Botão próximo
    if page < total_pages:
        items.append(Li(A("Next", href=f"{base_url}?page={page+1}")))
    else:
        items.append(Li(A("Next", href="#", cls="disabled")))
    
    return Ul(*items, cls="pagination")