from fastapi import APIRouter, HTTPException, Depends
from app.models.user_models import UserModel
from app.models.user_filter_models import UserFilterModel
from app.controllers import user_controllers
from pydantic import BaseModel
from app.core.security import user_auth
from typing import Optional

router = APIRouter()


class LoginSchema(BaseModel):
    username: str
    password: str

class UpdateUserSchema(BaseModel):
    image: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[int] = None
    role: Optional[str] = None
    status: Optional[bool] = None
    password: Optional[str] = None  
    new_password: Optional[str] = None


@router.post("/users/getAll")
def list_users(filters: UserFilterModel, _ = Depends(user_auth)):
    return user_controllers.get_users(filters)


@router.post("/users/add")
def create_user(user: UserModel):
    user_data = user_controllers.create_user(user)
    return {"message": "User created", "user": user_data}


@router.get("/users/{user_id}")
def get_user(user_id: str, _ = Depends(user_auth)):
    result = user_controllers.get_user_by_id(user_id)
    
    # Handle response yang sudah dalam format {status, data, message}
    if not result["status"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result


@router.put("/users/update/{user_id}")
def update_user(user_id: str, user_data: UpdateUserSchema, _ = Depends(user_auth)):
    # Convert to dict and remove None values
    update_data = user_data.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    updated_user = user_controllers.update_user(user_id, update_data)
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "message": "User updated successfully",
        "user": updated_user
    }


@router.delete("/users/delete/{user_id}")
def delete_user(user_id: str, _ = Depends(user_auth)):
    success = user_controllers.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}


@router.post("/users/login")
def login(request: LoginSchema):
    result = user_controllers.login_user(request.username, request.password)
    if not result["status"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return result