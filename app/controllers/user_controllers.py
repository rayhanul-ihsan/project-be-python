from app.database import db
from app.models.user_models import UserModel
from app.models.user_filter_models import UserFilterModel
from bson import ObjectId
from passlib.context import CryptContext
from app.core.security import create_access_token
from datetime import timedelta
import uuid
import datetime
import re

users_collection = db["users"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_users(filters: UserFilterModel):
    # Build query filter
    query = {}
    
    # Handle search
    if filters.search and filters.search_by:
        search_conditions = []
        search_pattern = re.compile(filters.search, re.IGNORECASE)
        
        for field in filters.search_by:
            search_conditions.append({field: {"$regex": search_pattern}})
        
        if filters.operator == "or":
            query["$or"] = search_conditions
        else:  # default "and"
            query["$and"] = search_conditions
    
    # Calculate pagination
    skip = (filters.page - 1) * filters.size
    limit = filters.size
    
    # Handle sorting
    sort_field = filters.orderBy
    sort_direction = -1 if filters.order == "desc" else 1
    
    # Get total count for pagination
    total_count = users_collection.count_documents(query)
    
    # Get users with filters applied
    cursor = users_collection.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit)
    
    users = []
    for user in cursor:
        user["_id"] = str(user["_id"])
        user.pop("password", None)  # Remove password from response
        users.append(user)
    
    # Calculate pagination info
    total_pages = (total_count + filters.size - 1) // filters.size  # Ceiling division
    
    return {
        "data": users,
        "pagination": {
            "page": filters.page,
            "size": filters.size,
            "total": total_count,
            "pages": total_pages,
        }
    }

def create_user(user: UserModel):
    user_dict = user.dict()
    user_dict['_id'] = str(uuid.uuid4())
    user_dict["password"] = hash_password(user.password)
    user_dict["created_at"] = datetime.datetime.now()
    result = users_collection.insert_one(user_dict)
    inserted_id = result.inserted_id
    new_user = users_collection.find_one({"_id": inserted_id})
    new_user["_id"] = str(new_user["_id"])
    new_user.pop("password", None)
    return new_user


def delete_user(user_id: str):
    result = users_collection.delete_one({"_id": user_id})
    return result.deleted_count > 0


def login_user(username: str, password: str):
    user = users_collection.find_one({"username": username})
    if not user:
        # user tidak ditemukan
        return {"status": False, "message": "User not found, please re-enter your username"}

    if not verify_password(password, user["password"]):
        # password salah
        return {"status": False, "message": "User not found, please re-enter your password"}

    # buat JWT token
    token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "username": user["username"]},
        expires_delta=token_expires,
    )

    # bersihkan password sebelum dikirim
    user["_id"] = str(user["_id"])
    user.pop("password", None)

    return {
        "status": True,
        "message": "Login successful",
        "data": user,
        "access_token": access_token,
        "token_type": "bearer",
    }


def get_user_by_id(user_id: str):

    user = users_collection.find_one({"_id": user_id})
    if not user:
        return None

    user["_id"] = str(user["_id"])
    user.pop("password", None)  # jangan expose password
    return user

def update_user(user_id: str, user_data: dict):
    # Cek apakah user exists
    existing_user = users_collection.find_one({"_id": user_id})
    if not existing_user:
        return None
    
    if user_data.get("password"): 
        if not verify_password(user_data["password"], existing_user["password"]):
        # password salah
            return {"status": False, "message": "User not found or invalid credentials"}
    
    # Prepare update data
    update_dict = {}
    
    # Fields yang boleh diupdate
    allowed_fields = ["image","username", "email", "phone", "password", "role", "status"]
    
    for field in allowed_fields:
        if field in user_data and user_data[field] is not None:
            update_dict[field] = user_data[field]
    
    # Handle password update secara terpisah
    if "new_password" in user_data and user_data["new_password"]:
        update_dict["password"] = hash_password(user_data["new_password"])
    
    # Add updated timestamp
    update_dict["updated_at"] = datetime.datetime.now()
    
    # Update user
    if update_dict:
        result = users_collection.update_one(
            {"_id": user_id},
            {"$set": update_dict}
        )
        
        if result.modified_count > 0 or result.matched_count > 0:
            # Get updated user
            updated_user = users_collection.find_one({"_id": user_id})
            updated_user["_id"] = str(updated_user["_id"])
            updated_user.pop("password", None)
            return updated_user
    
    return None