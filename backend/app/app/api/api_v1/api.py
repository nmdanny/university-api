from fastapi import APIRouter

from app.api.api_v1.endpoints import items, login, users, utils, university, track, course

api_router = APIRouter()
api_router.include_router(university.router, prefix="/universities")
api_router.include_router(track.router, prefix="/universities/{university_id}/tracks")
api_router.include_router(course.router, prefix="/universities/{university_id}/courses")
# api_router.include_router(login.router, tags=["login"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
# api_router.include_router(items.router, prefix="/items", tags=["items"])
