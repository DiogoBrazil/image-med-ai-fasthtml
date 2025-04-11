# web/components/layout.py
from fasthtml.common import *

def MainLayout(title, *content, active_page=None):
    """Layout principal da aplicação"""
    nav_items = [
        {"url": "/", "label": "Dashboard", "id": "dashboard"},
        {"url": "/users", "label": "Users", "id": "users"},
        {"url": "/health-units", "label": "Health Units", "id": "health-units"},
        {"url": "/attendances", "label": "Attendances", "id": "attendances"},
    ]
    
    return [
        Title(f"{title} - Medical Diagnosis System"),
        Main(
            Header(
                Div(
                    H1(A("Medical Diagnosis System", href="/"), cls="logo"),
                    cls="brand"
                ),
                Nav(
                    Ul(*[
                        Li(
                            A(item["label"], href=item["url"], 
                              cls="active" if active_page == item["id"] else "")
                        ) for item in nav_items
                    ]),
                    A("Logout", href="/logout", cls="logout-btn"),
                    cls="main-nav"
                ),
                cls="main-header"
            ),
            Div(*content, cls="content-container"),
            Footer(
                Div(
                    "© 2025 Medical Diagnosis System. All rights reserved.",
                    cls="footer-text"
                ),
                cls="main-footer"
            ),
            cls="container"
        ),
        # CSS personalizado para o layout
        Style("""
            :root {
                --primary-color: #2563eb;
                --secondary-color: #1e3a8a;
                --bg-color: #f3f4f6;
                --text-color: #1f2937;
                --border-color: #e5e7eb;
                --success-color: #10b981;
                --error-color: #ef4444;
                --warning-color: #f59e0b;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
                margin: 0;
                padding: 0;
            }
            .container {
                display: flex;
                flex-direction: column;
                min-height: 100vh;
            }
            .main-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 1rem 2rem;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .brand .logo {
                color: var(--primary-color);
                text-decoration: none;
                font-size: 1.5rem;
                font-weight: bold;
            }
            .main-nav {
                display: flex;
                align-items: center;
            }
            .main-nav ul {
                display: flex;
                list-style: none;
                margin: 0;
                padding: 0;
            }
            .main-nav ul li {
                margin-right: 1.5rem;
            }
            .main-nav ul li a {
                color: var(--text-color);
                text-decoration: none;
                padding: 0.5rem 0;
                font-weight: 500;
                border-bottom: 2px solid transparent;
                transition: all 0.2s;
            }
            .main-nav ul li a:hover {
                color: var(--primary-color);
                border-bottom-color: var(--primary-color);
            }
            .main-nav ul li a.active {
                color: var(--primary-color);
                border-bottom-color: var(--primary-color);
                font-weight: 600;
            }
            .logout-btn {
                background-color: var(--primary-color);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 0.25rem;
                text-decoration: none;
                font-weight: 500;
                transition: background-color 0.2s;
            }
            .logout-btn:hover {
                background-color: var(--secondary-color);
            }
            .content-container {
                flex: 1;
                padding: 2rem;
                max-width: 1200px;
                margin: 0 auto;
                width: 100%;
            }
            .main-footer {
                background-color: white;
                padding: 1rem 2rem;
                text-align: center;
                border-top: 1px solid var(--border-color);
            }
            .card {
                background-color: white;
                border-radius: 0.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                padding: 1.5rem;
                margin-bottom: 1.5rem;
            }
            .btn {
                display: inline-block;
                background-color: var(--primary-color);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 0.25rem;
                text-decoration: none;
                font-weight: 500;
                border: none;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            .btn:hover {
                background-color: var(--secondary-color);
            }
            .btn-secondary {
                background-color: #6b7280;
            }
            .btn-secondary:hover {
                background-color: #4b5563;
            }
            .btn-danger {
                background-color: var(--error-color);
            }
            .btn-danger:hover {
                background-color: #dc2626;
            }
            .alert {
                padding: 1rem;
                border-radius: 0.25rem;
                margin-bottom: 1rem;
            }
            .alert-success {
                background-color: #d1fae5;
                color: #065f46;
                border: 1px solid #a7f3d0;
            }
            .alert-error {
                background-color: #fee2e2;
                color: #b91c1c;
                border: 1px solid #fecaca;
            }
            .alert-warning {
                background-color: #fffbeb;
                color: #92400e;
                border: 1px solid #fef3c7;
            }
            .form-group {
                margin-bottom: 1rem;
            }
            .form-group label {
                display: block;
                margin-bottom: 0.5rem;
                font-weight: 500;
            }
            .form-control {
                width: 100%;
                padding: 0.5rem;
                border: 1px solid var(--border-color);
                border-radius: 0.25rem;
                font-size: 1rem;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            table th, table td {
                padding: 0.75rem;
                text-align: left;
                border-bottom: 1px solid var(--border-color);
            }
            table th {
                background-color: #f9fafb;
                font-weight: 600;
            }
            .pagination {
                display: flex;
                list-style: none;
                padding: 0;
                margin: 1rem 0;
            }
            .pagination li {
                margin-right: 0.5rem;
            }
            .pagination li a {
                display: block;
                padding: 0.5rem 0.75rem;
                border: 1px solid var(--border-color);
                border-radius: 0.25rem;
                text-decoration: none;
                color: var(--text-color);
            }
            .pagination li.active a {
                background-color: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
            }
        """)
    ]