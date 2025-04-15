# api/src/controllers/health_unit_controller.py
from fastapi import Request
from ..interfaces.create_health_unit import CreateHealthUnit
from ..interfaces.update_health_unit import UpdateHealthUnit
from ..usecases.health_unit_usecases import HealthUnitUseCases
from ..utils.credentials_middleware import AuthMiddleware
from ..utils.logger import get_logger
from ..utils.error_handler import raise_http_error # Importar raise_http_error se não estiver importado

logger = get_logger(__name__)

class HealthUnitController:
    def __init__(self):
        self.health_unit_use_cases = HealthUnitUseCases()
        self.auth_middleware = AuthMiddleware()

    async def add_health_unit(self, request: Request, health_unit: CreateHealthUnit):
        """
        Adds a new health unit.
        Requires administrator profile.
        """
        await self.auth_middleware.verify_request(request)

        audit_data = {
            "user_id": request.state.user.get("user_id"),
            "action": "add_health_unit",
            "ip_address": request.client.host if request.client else "N/A"
        }

        user_profile = request.state.user.get("profile")
        if user_profile not in ["administrator", "general_administrator"]:
            logger.warning(f"User {audit_data['user_id']} attempted to add health unit without admin privileges")
            # Usar raise_http_error para consistência com outros erros
            raise_http_error(403, "Only administrators can add health units")

        # Passar admin_id correto para o use case (o ID do admin que está criando)
        admin_creator_id = request.state.user.get("user_id")
        return await self.health_unit_use_cases.add_health_unit(health_unit, admin_creator_id, audit_data)

    async def get_health_units(self, request: Request):
        """
        Retrieves health units.
        - General Administrators: See all units.
        - Administrators: See their own units.
        - Professionals: See units linked to their administrator.
        """
        await self.auth_middleware.verify_request(request)

        user_info = request.state.user
        user_id = user_info.get("user_id")
        user_profile = user_info.get("profile")

        audit_data = {
            "user_id": user_id,
            "action": "get_health_units",
            "ip_address": request.client.host if request.client else "N/A"
        }

        admin_id_to_filter = None # Inicializa como None

        if user_profile == "general_administrator":
            # General admin vê tudo, não filtra por admin_id
            logger.info(f"General Administrator {user_id} fetching all health units.")
            admin_id_to_filter = None
        elif user_profile == "administrator":
            # Admin vê apenas as suas unidades (user_id é o admin_id)
            logger.info(f"Administrator {user_id} fetching their health units.")
            admin_id_to_filter = user_id
        elif user_profile == "professional":
            # Professional vê as unidades do seu admin
            admin_id_from_token = user_info.get("admin_id")
            if not admin_id_from_token:
                logger.error(f"Professional {user_id} missing admin_id in token.")
                raise_http_error(400, "Administrator information missing for this professional.")
            logger.info(f"Professional {user_id} fetching health units for admin {admin_id_from_token}.")
            admin_id_to_filter = admin_id_from_token
        else:
            # Outros perfis não têm permissão
            logger.warning(f"User {user_id} with profile {user_profile} attempted to get health units without sufficient privileges.")
            raise_http_error(403, "Insufficient privileges to view health units.")

        # Chama o use case com o admin_id correto para filtro (ou None)
        return await self.health_unit_use_cases.get_health_units(audit_data, admin_id=admin_id_to_filter)

    async def get_health_unit_by_id(self, request: Request, unit_id: str):
        """
        Retrieves a health unit by ID.
        Users can only see units associated with their administrator (handled in use case/repo).
        """
        await self.auth_middleware.verify_request(request)

        user_info = request.state.user
        audit_data = {
            "user_id": user_info.get("user_id"),
            "action": "get_health_unit_by_id",
            "target_unit_id": unit_id,
            "ip_address": request.client.host if request.client else "N/A"
        }

        # A lógica de permissão (se o usuário pode ver esta unidade específica)
        # deve idealmente ser verificada no use case, comparando o admin_id da unidade
        # com o admin_id do token (para professional) ou user_id (para admin).
        return await self.health_unit_use_cases.get_health_unit_by_id(unit_id, user_info, audit_data)

    async def update_health_unit(self, request: Request, unit_id: str, health_unit: UpdateHealthUnit):
        """
        Updates information of a health unit.
        Only administrators can update their own units.
        """
        await self.auth_middleware.verify_request(request)

        user_info = request.state.user
        user_id = user_info.get("user_id")
        user_profile = user_info.get("profile")

        audit_data = {
            "user_id": user_id,
            "action": "update_health_unit",
            "target_unit_id": unit_id,
            "ip_address": request.client.host if request.client else "N/A"
        }

        if user_profile not in ["administrator", "general_administrator"]:
            logger.warning(f"User {user_id} attempted to update health unit {unit_id} without admin privileges.")
            raise_http_error(403, "Only administrators can update health units.")

        # Passa user_info para o use case verificar se o admin é dono da unidade
        return await self.health_unit_use_cases.update_health_unit(unit_id, health_unit, user_info, audit_data)

    async def delete_health_unit(self, request: Request, unit_id: str):
        """
        Removes a health unit.
        Only administrators can remove their own units.
        """
        await self.auth_middleware.verify_request(request)

        user_info = request.state.user
        user_id = user_info.get("user_id")
        user_profile = user_info.get("profile")

        audit_data = {
            "user_id": user_id,
            "action": "delete_health_unit",
            "target_unit_id": unit_id,
            "ip_address": request.client.host if request.client else "N/A",
            "profile": user_profile
        }

        if user_profile not in ["administrator", "general_administrator"]:
            logger.warning(f"User {user_id} attempted to delete health unit {unit_id} without admin privileges.")
            raise_http_error(403, "Only administrators can delete health units.")

        # Passa user_info para o use case verificar se o admin é dono da unidade
        return await self.health_unit_use_cases.delete_health_unit(unit_id, user_info, audit_data)