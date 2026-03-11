from fastapi import APIRouter, Request, HTTPException

router = APIRouter(prefix="/api/v1/ai-vet/users", tags=["users"])


@router.post("/create")
async def create_user(request: Request, data: dict):
    user_id = str(data.get("user_id"))
    request.app.state.user_statuses[user_id] = {"role": "", "animal": ""}
    request.app.state.conversations[user_id] = {"messages": [], "summary": ""}
    return {"status": "created", "user_id": user_id}


@router.get("/{user_id}")
async def get_user(request: Request, user_id: str):
    user = request.app.state.user_statuses.get(user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return {"user_id": user_id, "role": user["role"], "animal": user["animal"]}


@router.patch("/{user_id}")
async def update_user(request: Request, user_id: str, data: dict):
    user = request.app.state.user_statuses.get(user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    if "role" in data:
        request.app.state.user_statuses[user_id]["role"] = data["role"]
    if "animal" in data:
        request.app.state.user_statuses[user_id]["animal"] = data["animal"]
    return {"status": "updated", "user_id": user_id}


# Legacy compatibility endpoints (old paths used by bot)
compat_router = APIRouter(prefix="/api/v1/ai-vet", tags=["compat"])


@compat_router.post("/create_user")
async def legacy_create_user(request: Request, data: dict):
    return await create_user(request, data)


@compat_router.post("/set_user_role")
async def legacy_set_user_role(request: Request, data: dict):
    user_id = str(data.get("user_id"))
    role = data.get("role")
    if user_id not in request.app.state.user_statuses:
        request.app.state.user_statuses[user_id] = {"role": "", "animal": ""}
    request.app.state.user_statuses[user_id]["role"] = role
    return {"message": "User role set successfully."}


@compat_router.post("/set_user_animal")
async def legacy_set_user_animal(request: Request, data: dict):
    user_id = str(data.get("user_id"))
    animal = data.get("animal")
    if user_id not in request.app.state.user_statuses:
        request.app.state.user_statuses[user_id] = {"role": "", "animal": ""}
    request.app.state.user_statuses[user_id]["animal"] = animal
    return {"message": "User animal set successfully."}
