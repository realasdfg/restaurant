from app.models.enums import RoleEnum

ROLE_HIERARCHY = {
    RoleEnum.STAFF: 1,
    RoleEnum.ADMIN: 2,
}

async def has_access(user_role: RoleEnum, required_role: RoleEnum) -> bool:
    return ROLE_HIERARCHY[user_role] >= ROLE_HIERARCHY[required_role]
