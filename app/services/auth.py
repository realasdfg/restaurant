# from app.services.crud_base import BaseCRUDService
#
#
# class AuthService(BaseCRUDService):
#
#     async def register(self):
#         category_dict = menu_category.model_dump()
#         return await self._create(category_dict)
#
#     async def login(self):
#         return await self._get_all()
#
#     async def token_refresh(self):
#         return await self._get_one({'id': category_id})