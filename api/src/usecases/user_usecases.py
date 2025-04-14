from datetime import datetime
from typing import Dict
from fastapi import HTTPException
from ..utils.verify_email import is_email_valid
from ..utils.logger import get_logger
from ..adapters.token_adapter import TokenAdapter
from ..adapters.password_adapter import PasswordAdapter
from ..interfaces.login_user import LoginUser
from ..interfaces.create_user import CreateUser
from ..interfaces.update_user import UpdateUser
from ..interfaces.create_subscriptions import CreateSubscriptions
from ..repositories.user_repository import UserRepository
from ..utils.error_handler import raise_http_error
from src.config.settings import Settings


settings = Settings()
logger = get_logger(__name__)


class UserUseCases:
    def __init__(self):
        self.user_repository = UserRepository()
        self.password_adapter = PasswordAdapter()
        self.token_adapter = TokenAdapter()
    
    async def add_user(self, admin_profile: str, admin_id: str, user: CreateUser, audit_data: Dict = None) -> Dict:
       """
       Adiciona um novo usuário após validar seus dados.
       Trata corretamente o admin_id com base no perfil do criador e do usuário sendo criado.

       Args:
           admin_profile: Perfil do usuário fazendo a requisição ("administrator" ou "general_administrator").
           admin_id: ID do usuário fazendo a requisição.
           user: Objeto CreateUser vindo da requisição (agora DEVE conter admin_id opcional).
           audit_data: Dados para auditoria (opcional).

       Returns:
           Dicionário com mensagem de sucesso ou lança HTTPException em caso de erro.
       """
       try:
           # user.dict() agora incluirá 'admin_id' se foi enviado e definido no Pydantic
           user_data = user.dict()
           logger.info(f"Attempting to add user with data (before hashing): { {k: v for k, v in user_data.items() if k != 'password'} }") # Log sem a senha

           # 1. Validações de campos obrigatórios e formato
           required_fields = ["full_name", "email", "password", "profile"]
           for field in required_fields:
               if field not in user_data or not user_data[field]:
                   logger.error(f"Error adding user '{user_data.get('email', 'N/A')}': Field '{field}' cannot be empty")
                   raise_http_error(400, f"Field '{field}' cannot be empty")

           valid_profiles = ["general_administrator", "administrator", "professional"]
           if user_data["profile"] not in valid_profiles:
               logger.error(f"Error adding user '{user_data.get('email', 'N/A')}': Invalid profile '{user_data['profile']}'")
               raise_http_error(422, f"Invalid profile. Must be one of: {', '.join(valid_profiles)}")

           if "status" in user_data and user_data["status"] not in ["active", "inactive"]:
                user_data["status"] = "active" # Define um padrão seguro se inválido
                logger.warning(f"Invalid status provided for user '{user_data.get('email', 'N/A')}'. Defaulting to 'active'.")
                # Ou lance um erro:
                # logger.error(f"Error adding user '{user_data.get('email', 'N/A')}': Invalid status '{user_data['status']}'")
                # raise_http_error(422, "Invalid status. Must be 'active' or 'inactive'")

           if not is_email_valid(user_data["email"]):
               logger.error(f"Error adding user: Invalid email format '{user_data['email']}'")
               raise_http_error(422, "Invalid email format")

           # 2. Verifica se o usuário já existe
           user_exists = await self.user_repository.get_user_by_email(user_data["email"])
           if user_exists:
               logger.error(f"Error adding user: User with email '{user_data['email']}' already exists")
               raise_http_error(409, "User with this email already exists")

           # 3. Lógica do ADMIN_ID REVISADA
           profile_being_created = user_data["profile"]
           admin_id_from_payload = user_data.get("admin_id") # Pode ser None se não veio ou não foi definido no Pydantic

           logger.info(f"Processing admin_id logic. Creator profile: {admin_profile}, Creating profile: {profile_being_created}, Admin ID from payload: {admin_id_from_payload}")

           if profile_being_created == "professional":
               # Se criando um profissional, admin_id é obrigatório e deve vir do payload
               if not admin_id_from_payload:
                    logger.error(f"Error adding professional '{user_data['email']}': admin_id is missing in request payload")
                    raise_http_error(400, "Associated administrator ID is required when creating a professional.")

               # Opcional: Validar se o admin_id fornecido existe e é um administrador
               # Nota: Certifique-se que get_user_by_id aceita UUID ou string e trata corretamente
               admin_user = await self.user_repository.get_user_by_id(admin_id_from_payload)
               if not admin_user:
                   logger.error(f"Error adding user '{user_data['email']}': Selected Admin with ID {admin_id_from_payload} not found")
                   raise_http_error(404, "Selected Administrator not found")
               # Ajuste a verificação de perfil conforme sua regra (só admin ou GA também pode ser?)
               elif admin_user["profile"] not in ["administrator", "general_administrator"]:
                   logger.error(f"Error adding user '{user_data['email']}': User with ID {admin_id_from_payload} is not an administrator")
                   raise_http_error(403, f"Selected user '{admin_user['full_name']}' is not an administrator profile.")

               # Se passou nas validações, o admin_id do payload é usado.
               # user_data['admin_id'] já está correto vindo do payload.
               logger.info(f"Professional '{user_data['email']}' will be associated with admin_id: {admin_id_from_payload}")

           elif profile_being_created in ["administrator", "general_administrator"]:
               # Ao criar admins, garantir que admin_id seja NULL no banco.
               # Se o frontend enviou por engano, sobrescrevemos para None.
               if admin_id_from_payload is not None:
                   logger.warning(f"Received admin_id '{admin_id_from_payload}' when creating an admin/general_admin profile ('{user_data['email']}'). Setting admin_id to None.")
               user_data["admin_id"] = None # Garante que seja nulo para admins
               logger.info(f"Admin/General Admin '{user_data['email']}' will have admin_id set to None.")


           # 4. Hash da senha
           try:
                user_data["password_hash"] = await self.password_adapter.hash_password(user_data["password"])
           except Exception as hash_error:
                logger.error(f"Error hashing password for user '{user_data['email']}': {hash_error}", exc_info=True)
                raise_http_error(500, "Error processing password.")

           # 5. Remove a senha original antes de salvar
           if "password" in user_data:
               del user_data["password"]

           # 6. Chama o repositório para adicionar o usuário
           logger.info(f"Calling repository to add user. Final data (excluding hash): { {k: v for k, v in user_data.items() if k != 'password_hash'} }")
           result = await self.user_repository.add_user(user_data)

           # 7. Retorna o resultado
           if result.get("added"):
               user_id_created = result.get("user_id")
               logger.info(f"User '{user_data['email']}' added successfully with ID: {user_id_created}. Audit data: {audit_data}")
               # Considerar adicionar uma tarefa de auditoria aqui se necessário
               return {
                   "detail": {
                       "message": "User added successfully",
                       "user_id": user_id_created,
                       "status_code": 201
                   }
               }
           else:
               # O repositório já deve ter logado o erro específico
               logger.error(f"Error adding user '{user_data['email']}': Repository returned added=False.")
               raise_http_error(500, "Failed to add user to the database.")


       except HTTPException as http_exc:
            # Re-lança exceções HTTP para o handler global tratar a resposta
            logger.warning(f"HTTP Exception during add_user for '{user_data.get('email', 'N/A')}': {http_exc.status_code} - {http_exc.detail}")
            raise http_exc
       except Exception as e:
            # Captura outros erros inesperados
            logger.error(f"Unexpected error adding user '{user_data.get('email', 'N/A')}': {e}", exc_info=True)
            raise_http_error(500, f"An unexpected error occurred while adding the user.")
            
    
    async def login_user(self, user: LoginUser, audit_data=None):
        """Authenticate a user and generate a token."""
        try:
            
            user_login = user.dict()
            email = user_login["email"]
            

            user_info = await self.user_repository.get_user_by_email(email)
            
            if not user_info:
                logger.error(f"Login attempt failed: User {email} not found")
                raise_http_error(404, "User not found")

            if user_info["status"] != "active":
                logger.error(f"Login attempt failed: User {email} is inactive")
                raise_http_error(403, "User account is inactive")


            if not await self.password_adapter.verify_password(
                user_login["password"], user_info["password_hash"]
            ):
                logger.error(f"Login attempt failed: Incorrect password for {email}")
                raise_http_error(401, "Incorrect password")


            token = await self.token_adapter.create_token(
                user_info["id"],
                user_info["full_name"],
                email,
                user_info["profile"],
                user_info.get("admin_id")
            )

            logger.info(f"User {email} logged in successfully")

            return {
                "detail": {
                    "message": "Login successful",
                    "user_name": user_info["full_name"],
                    "user_id": user_info["id"],
                    "profile": user_info["profile"],
                    "token": token,
                    "status_code": 200,
                }
            }
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            raise_http_error(500, "Internal server error during login process")
    
    async def get_users(self, admin_id=None, audit_data=None):
        """
        Retrieve all users or users associated with an admin.
        If admin_id is provided, return only users associated with that admin.
        """
        try:

            users = await self.user_repository.get_users(admin_id)


            users_without_password = [
                {key: user[key] for key in user if key != 'password_hash'} 
                for user in users
            ]

            return {
                "detail": {
                    "message": "Users retrieved successfully",
                    "users": users_without_password,
                    "count": len(users_without_password),
                    "status_code": 200
                }
            }
        except Exception as e:
            logger.error(f"Error retrieving users: {e}")
            raise_http_error(500, "Error retrieving users")

    async def get_user_by_id(self, user_id: str, audit_data=None):
        """Retrieve a user by their ID, excluding the password."""
        try:

            user = await self.user_repository.get_user_by_id(user_id)

            if user:

                user_without_password = {
                    key: user[key] for key in user if key != 'password_hash'
                }
                
                return {
                    "detail": {
                        "message": "User retrieved successfully",
                        "user": user_without_password,
                        "status_code": 200
                    }
                }
            else:
                logger.error(f"User with ID {user_id} not found")
                raise_http_error(404, "User not found")
                
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Error retrieving user by ID: {e}")
            raise_http_error(500, "Error retrieving user")
            
    
    async def update_user(self, current_user_id: str, current_user_profile: str, user_id_to_update: str, user_update_data: UpdateUser, audit_data: Dict = None) -> Dict:
        """
        Atualiza informações do usuário, tratando admin_id corretamente na mudança de perfil
        e na edição por administradores.
        """
        try:
            # 1. Verifica se o usuário a ser atualizado existe
            existing_user = await self.user_repository.get_user_by_id(user_id_to_update)
            if not existing_user:
                logger.error(f"Error updating user: User with ID {user_id_to_update} not found")
                raise_http_error(404, "User not found")

            # 2. Prepara os dados para atualização (excluindo campos não definidos no payload)
            update_data = user_update_data.dict(exclude_unset=True)
            logger.info(f"Attempting to update user {user_id_to_update}. Received update data: {update_data}")

            # 3. Validações (Email, Perfil, Status) - Aplicar apenas se os campos estiverem no payload
            if "email" in update_data:
                 # ... (validação de email como antes) ...
                if not is_email_valid(update_data["email"]):
                    logger.error(f"Error updating user {user_id_to_update}: Invalid email format '{update_data['email']}'")
                    raise_http_error(422, "Invalid email format")
                email_exists = await self.user_repository.get_user_by_email(update_data["email"])
                if email_exists and str(email_exists["id"]) != str(user_id_to_update):
                    logger.error(f"Error updating user {user_id_to_update}: Email '{update_data['email']}' already in use by user {email_exists['id']}")
                    raise_http_error(409, "Email already in use by another user")


            # 4. Verifica Permissões de Atualização ANTES de processar mudanças sensíveis
            # (quem pode atualizar quem) - Lógica movida para cima
            can_perform_update = False
            # GA pode editar qualquer um (exceto outro GA se a regra for essa)
            if current_user_profile == "general_administrator":
                 if existing_user["profile"] == "general_administrator" and str(existing_user["id"]) != str(current_user_id):
                      logger.warning(f"General Administrator {current_user_id} attempted to update another General Administrator {user_id_to_update}.")
                      # Decida se permite ou não. Se não: raise_http_error(403, "General Administrators cannot update each other.")
                      can_perform_update = True # Ou False se não permitir
                 else:
                      can_perform_update = True
            # Admin só pode editar a si mesmo OU profissionais vinculados a ele
            elif current_user_profile == "administrator":
                 if str(existing_user["id"]) == str(current_user_id) or \
                    (existing_user["profile"] == "professional" and str(existing_user.get("admin_id")) == str(current_user_id)):
                     can_perform_update = True
            # Profissional só pode editar a si mesmo
            elif current_user_profile == "professional":
                  if str(existing_user["id"]) == str(current_user_id):
                      can_perform_update = True

            if not can_perform_update:
                 logger.warning(f"User {current_user_id} ({current_user_profile}) does not have permission to update user {user_id_to_update} ({existing_user['profile']}).")
                 raise_http_error(403, "You do not have permission to update this user.")

            # 5. Processa Mudança de Perfil e ADMIN_ID
            new_profile = update_data.get("profile") # Perfil vindo do payload (pode ser None)
            admin_id_from_payload = update_data.get("admin_id") # Admin ID vindo do payload (pode ser None)
            final_admin_id: Optional[UUID] = existing_user.get("admin_id") # Começa com o valor atual no DB (pode ser None)

            if new_profile and new_profile != existing_user["profile"]:
                # --- Perfil ESTÁ sendo alterado ---
                logger.info(f"Profile change detected for user {user_id_to_update}: from '{existing_user['profile']}' to '{new_profile}'")
                # Apenas GA pode mudar perfil
                if current_user_profile != "general_administrator":
                    logger.warning(f"User {current_user_id} ({current_user_profile}) attempted to change profile of user {user_id_to_update}.")
                    raise_http_error(403, "Only General Administrators can change user profiles.")

                valid_profiles = ["general_administrator", "administrator", "professional"]
                if new_profile not in valid_profiles:
                    # Validação duplicada, mas segura
                    logger.error(f"Error updating user {user_id_to_update}: Invalid profile '{new_profile}'")
                    raise_http_error(422, f"Invalid profile. Must be one of: {', '.join(valid_profiles)}")

                if new_profile == "professional":
                    # Se GA está mudando para profissional, admin_id é obrigatório no payload
                    if not admin_id_from_payload:
                        logger.error(f"Error updating user {user_id_to_update} to 'professional': admin_id is missing in request payload")
                        raise_http_error(400, "Associated administrator ID is required when setting profile to professional.")

                    # Validação opcional do admin_id fornecido (como antes)
                    admin_user = await self.user_repository.get_user_by_id(admin_id_from_payload)
                    if not admin_user: raise_http_error(404, "Selected Administrator not found")
                    if admin_user["profile"] not in ["administrator", "general_administrator"]: raise_http_error(403, "Selected user is not an administrator profile.")

                    final_admin_id = admin_id_from_payload # Usa o ID do payload
                    logger.info(f"Setting profile to 'professional' for user {user_id_to_update}, associated with admin_id: {final_admin_id}")

                elif new_profile in ["administrator", "general_administrator"]:
                    # Se GA está mudando para admin/GA, admin_id deve ser NULL
                    if admin_id_from_payload is not None:
                        logger.warning(f"Received admin_id '{admin_id_from_payload}' when updating profile to '{new_profile}' for user {user_id_to_update}. Ignoring payload value and setting admin_id to None.")
                    final_admin_id = None # Garante que seja nulo
                    logger.info(f"Setting profile to '{new_profile}' for user {user_id_to_update}, ensuring admin_id is None.")

            elif admin_id_from_payload is not None and str(admin_id_from_payload) != str(final_admin_id):
                 # --- Perfil NÃO está sendo alterado, MAS admin_id foi enviado ---
                 # Isso indica uma tentativa de REASSOCIAR um profissional (provavelmente por um GA)
                 logger.info(f"Re-association attempt for user {user_id_to_update}. New admin_id from payload: {admin_id_from_payload}")
                 # Permite apenas se o usuário atual é profissional e o editor é GA?
                 if existing_user["profile"] != "professional":
                      logger.warning(f"Attempted to set admin_id for non-professional user {user_id_to_update}.")
                      # Decide se ignora ou lança erro. Ignorar é mais simples:
                      # del update_data["admin_id"] # Remove do dict final se não for permitido
                      # Ou lançar erro:
                      raise_http_error(400, "Cannot associate an administrator with a non-professional user.")
                 elif current_user_profile != "general_administrator":
                      logger.warning(f"User {current_user_id} ({current_user_profile}) attempted to re-associate professional {user_id_to_update}.")
                      raise_http_error(403, "Only General Administrators can re-associate professionals.")
                 else:
                      # Validar novo admin_id (como na mudança de perfil)
                      admin_user = await self.user_repository.get_user_by_id(admin_id_from_payload)
                      if not admin_user: raise_http_error(404, "Selected new Administrator not found")
                      if admin_user["profile"] not in ["administrator", "general_administrator"]: raise_http_error(403, "Selected user is not an administrator profile.")
                      final_admin_id = admin_id_from_payload # Usa o novo ID do payload
                      logger.info(f"Re-associating professional {user_id_to_update} with admin_id: {final_admin_id}")

            # Else (perfil não muda, admin_id não enviado): final_admin_id mantém o valor original do DB

            # Adiciona/Atualiza o admin_id no dicionário que vai para o repositório
            # Isso garante que o repositório sempre receba a intenção correta (seja ela manter, mudar ou anular)
            update_data["admin_id"] = final_admin_id
            logger.info(f"Final admin_id to be used in update for user {user_id_to_update}: {final_admin_id}")

            # 6. Processa Status (se presente)
            if "status" in update_data and update_data["status"] not in ["active", "inactive"]:
                logger.error(f"Error updating user {user_id_to_update}: Invalid status '{update_data['status']}'")
                raise_http_error(422, "Invalid status. Must be 'active' or 'inactive'")


            # 7. Remove campos que não devem ir para o update ou já foram processados
            if "password" in update_data: del update_data["password"]
            if "password_hash" in update_data: del update_data["password_hash"]
            # 'profile' pode ir se foi alterado, o repo deve lidar com isso.
            # 'admin_id' é tratado agora.

            # Garante que update_data não esteja vazio após processamento
            if not update_data:
                 logger.info(f"No relevant changes detected for user {user_id_to_update} after processing. Skipping update.")
                 return {"detail": {"message": "No relevant changes detected", "user_id": user_id_to_update, "status_code": 200}}


            # 8. Chama o repositório para atualizar
            logger.info(f"Calling repository to update user {user_id_to_update}. Final update data: {update_data}")
            result = await self.user_repository.update_user(user_id_to_update, update_data)

            # 9. Retorna o resultado
            if result.get("updated"):
                logger.info(f"User {user_id_to_update} updated successfully. Audit data: {audit_data}")
                # Considerar auditoria
                return {
                    "detail": {
                        "message": "User updated successfully",
                        "user_id": user_id_to_update,
                        "status_code": 200
                    }
                }
            elif result.get("not_found", False):
                 logger.error(f"Failed to update user: User with ID {user_id_to_update} not found during update operation.")
                 raise_http_error(404, "User not found during update.")
            else:
                logger.error(f"Failed to update user {user_id_to_update}: Repository returned updated=False.")
                raise_http_error(500, "Failed to update user in the database.")

        except HTTPException as http_exc:
            # Re-lança exceções HTTP
            raise http_exc
        except Exception as e:
            # Captura outros erros inesperados
            logger.error(f"Unexpected error updating user {user_id_to_update}: {e}", exc_info=True)
            raise_http_error(500, f"An unexpected error occurred while updating the user.")


    async def delete_user(self, current_user_id, current_user_profile, user_id: str, audit_data=None):
        """Delete a user by ID."""
        try:


            existing_user = await self.user_repository.get_user_by_id(user_id)
            if not existing_user:
                logger.error(f"Error deleting user: User with ID {user_id} not found")
                raise_http_error(404, "User not found")
            
            if existing_user["id"] == current_user_id:
                logger.error(f"Error deleting user: User cannot delete itself")
                raise_http_error(403, "User cannot delete itself")
            
            if current_user_profile != "general_administrator" and existing_user["id"] != current_user_id:

                current_user = await self.user_repository.get_user_by_id(current_user_id)
                if not current_user:
                    logger.error(f"Error deleting user: User with ID {current_user_id} not found")
                    raise_http_error(404, "Admin not found")
                

                if existing_user["admin_id"] != current_user_id:
                    logger.error(f"Error deleting user: Professional with ID {user_id} is not associated with this administrator")
                    raise_http_error(403, "Professional is not associated with this administrator")


            result = await self.user_repository.delete_user(user_id)
            
            if result["deleted"]:
                logger.info(f"User with ID {user_id} deleted successfully")
                return {
                    "detail": {
                        "message": "User deleted successfully",
                        "user_id": user_id,
                        "status_code": 200
                    }
                }
            else:
                logger.error(f"Failed to delete user with ID {user_id}")
                raise_http_error(500, "Failed to delete user")

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise_http_error(500, "Error deleting user")
            
    async def get_administrators(self, audit_data=None):
        """Retrieve all administrator users."""
        try:
            administrators = await self.user_repository.get_administrators()

            return {
                "detail": {
                    "message": "Administrators retrieved successfully",
                    "administrators": administrators,
                    "count": len(administrators),
                    "status_code": 200
                }
            }
        except Exception as e:
            logger.error(f"Error retrieving administrators: {e}")
            raise_http_error(500, "Error retrieving administrators")
            
    async def get_professionals(self, admin_id: str, current_user_profile, audit_data=None):
        """Retrieve all professionals associated with an administrator."""
        try:
            if current_user_profile == "general_administrator":
                professionals = await self.user_repository.get_professionals()
            else:

                admin = await self.user_repository.get_user_by_id(admin_id)
                if not admin:
                    logger.error(f"Error retrieving professionals: Admin with ID {admin_id} not found")
                    raise_http_error(404, "Administrator not found")

                if admin["profile"] != "administrator":
                    logger.error(f"Error retrieving professionals: User with ID {admin_id} is not an administrator")
                    raise_http_error(403, "User is not an administrator")

                professionals = await self.user_repository.get_professionals_by_admin(admin_id)

            return {
                "detail": {
                    "message": "Professionals retrieved successfully",
                    "professionals": professionals,
                    "count": len(professionals),
                    "status_code": 200
                }
            }
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Error retrieving professionals: {e}")
            raise_http_error(500, "Error retrieving professionals")
    

    async def create_subscription(self, subscription_data: CreateSubscriptions, audit_data=None):
        """Create a subscription for a user."""
        try:

            data_dict = subscription_data.dict()
    

            admin_exists = await self.user_repository.get_user_by_id(data_dict["admin_id"])
            if not admin_exists:
                logger.error(f"Error creating subscription: Admin with ID {data_dict['admin_id']} not found")
                raise_http_error(404, "Admin not found")
        

            subscription_exists = await self.user_repository.get_subscription_by_admin_id(data_dict["admin_id"])
            if subscription_exists:
                logger.error(f"Error creating subscription: User already has a subscription")
                raise_http_error(409, "User already has a subscription")
    

            try:
                start_date = datetime.strptime(data_dict["start_date"], "%d-%m-%Y")
                end_date = datetime.strptime(data_dict["end_date"], "%d-%m-%Y")
                

                data_dict["start_date"] = start_date
                data_dict["end_date"] = end_date
                
            except ValueError as e:
                logger.error(f"Invalid date format: {e}")
                raise_http_error(400, f"Invalid date format. Dates must be in DD-MM-YYYY format.")
    

            result = await self.user_repository.create_subscription(data_dict)
            
            if result["added"]:
                return {
                    "detail": {
                        "message": "Subscription created successfully",
                        "admin_id": data_dict["admin_id"],
                        "status_code": 201
                    }
                }
            else:
                logger.error(f"Failed to create subscription for user with ID {data_dict['admin_id']}")
                if "error" in result:
                    raise_http_error(500, f"Failed to create subscription: {result['error']}")
                else:
                    raise_http_error(500, "Failed to create subscription")
    
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            raise_http_error(500, "Error creating subscription")
    

    async def get_subscriptions(self, audit_data=None):
        """Retrieve all subscriptions."""
        try:

            user_id = audit_data.get("user_id") if audit_data else None
            logger.info(f"Retrieving subscriptions for user_id: {user_id}")
            

            if user_id:

                await self.get_user_by_id(user_id, audit_data)
            
            try:
                subscriptions = await self.user_repository.get_subscriptions(user_id)
                logger.info(f"Found {len(subscriptions)} subscriptions")
                

                return {
                    "detail": {
                        "message": "Subscriptions retrieved successfully",
                        "subscriptions": subscriptions,
                        "count": len(subscriptions),
                        "status_code": 200
                    }
                }
                
            except ValueError as e:

                if str(e) == "User not found":
                    logger.warning(f"User not found error for ID: {user_id}")
                    raise_http_error(404, "User not found")
                else:
                    raise
            
        except HTTPException as http_exc:

            raise http_exc
        except Exception as e:
            logger.error(f"Error retrieving subscriptions: {e}")
            raise_http_error(500, f"Error retrieving subscriptions: {str(e)}")
    

    async def get_subscription_by_id(self, subscription_id: str, audit_data=None):
        """Retrieve a subscription by its ID."""
        try:
            subscription = await self.user_repository.get_subscription_by_id(subscription_id)
            
            if subscription:
                return {
                    "detail": {
                        "message": "Subscription retrieved successfully",
                        "subscription": subscription,
                        "status_code": 200
                    }
                }
            else:
                logger.error(f"Subscription with ID {subscription_id} not found")
                raise_http_error(404, "Subscription not found")
            
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Error retrieving subscription: {e}")
            raise_http_error(500, "Error retrieving subscription")

    
    async def update_subscription(self, subscription_id: str, subscription_data: CreateSubscriptions, audit_data=None):
        """Update an existing subscription."""
        try:

            subscription_data = subscription_data.dict()


            subscription_exists = await self.user_repository.get_subscription_by_id(subscription_id)
            if not subscription_exists:
                logger.error(f"Error updating subscription: Subscription with ID {subscription_id} not found")
                raise_http_error(404, "Subscription not found")
    

            admin_exists = await self.user_repository.get_user_by_id(subscription_data["admin_id"])
            if not admin_exists:
                logger.error(f"Error updating subscription: Admin with ID {subscription_data['admin_id']} not found")
                raise_http_error(404, "Admin not found")
    

            try:
                start_date = datetime.strptime(subscription_data["start_date"], "%d-%m-%Y")
                end_date = datetime.strptime(subscription_data["end_date"], "%d-%m-%Y")
                

                subscription_data["start_date"] = start_date
                subscription_data["end_date"] = end_date
                
            except ValueError as e:
                logger.error(f"Invalid date format: {e}")
                raise_http_error(400, f"Invalid date format. Dates must be in DD-MM-YYYY format.")
    

            result = await self.user_repository.update_subscription(subscription_id, subscription_data)
            
            if result["updated"]:
                return {
                    "detail": {
                        "message": "Subscription updated successfully",
                        "admin_id": subscription_data["admin_id"],
                        "status_code": 200
                    }
                }
            else:
                logger.error(f"Failed to update subscription for user with ID {subscription_data['admin_id']}")
                if "error" in result:
                    raise_http_error(500, f"Failed to update subscription: {result['error']}")
                else:
                    raise_http_error(500, "Failed to update subscription")
    
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            raise_http_error(500, "Error updating subscription")