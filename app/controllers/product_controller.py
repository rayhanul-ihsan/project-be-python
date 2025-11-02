from app.database import db
from app.models.product_models import ProductModel
from app.models.product_filter_models import ProductFilterModel
from bson import ObjectId
from pymongo import DESCENDING, ASCENDING
from datetime import datetime
import uuid


products_collection = db["products"]


def get_products(filters: ProductFilterModel):
    query = {}

    if filters.search and filters.search_by:
        conditions = []
        for field in filters.search_by:
            conditions.append({field: {"$regex": filters.search, "$options": "i"}})
        if filters.operator == "or":
            query["$or"] = conditions
        else:
            query["$and"] = conditions

    sort_order = DESCENDING if filters.order.lower() == "desc" else ASCENDING

    skip = (filters.page - 1) * filters.size
    cursor = (
        products_collection.find(query)
        .sort(filters.orderBy, sort_order)
        .skip(skip)
        .limit(filters.size)
    )

    products = []
    for product in cursor:
        product["_id"] = str(product["_id"])
        products.append(product)

    total = products_collection.count_documents(query)

    return {
        "data": products,
        "pagination": {
            "page": filters.page,
            "size": filters.size,
            "total": total,
            "pages": (total + filters.size - 1) // filters.size,
        },
    }


def create_product(product: ProductModel):
    product_dict = product.dict()
    product_dict["_id"] = str(uuid.uuid4())
    result = products_collection.insert_one(product_dict)
    inserted_id = result.inserted_id
    new_product = products_collection.find_one({"_id": inserted_id})
    new_product["_id"] = str(new_product["_id"])
    return new_product


def get_product_by_id(product_id: str):
   
    product = products_collection.find_one({"_id": product_id})

    if product:
        product["_id"] = str(product["_id"])
        return {
            "status": True,
            "data": product,
            "message": "Product found successfully.",
        }
    else:
        return {"status": False, "data": None, "message": "Product not found."}


def update_product(product_id: str, product_data: dict):
    update_data = {k: v for k, v in product_data.items() if v is not None}
    update_data["updatedAt"] = datetime.utcnow()

    result = products_collection.update_one({"_id": product_id}, {"$set": update_data})
    if result.modified_count == 0:
        return None

    updated_product = products_collection.find_one({"_id": product_id})
    updated_product["_id"] = str(updated_product["_id"])
    return updated_product


def delete_product(product_id: str):
    result = products_collection.delete_one({"_id": product_id})
    return result.deleted_count > 0
