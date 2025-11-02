from fastapi import APIRouter, HTTPException, Depends
from app.models.product_models import ProductModel
from app.controllers import product_controller
from app.models.product_filter_models import ProductFilterModel
from app.core.security import user_auth

router = APIRouter()


@router.post("/products/getAll")
def list_products(filters: ProductFilterModel, _ = Depends(user_auth)):
    return product_controller.get_products(filters)


@router.post("/products/add")
def create_product(product: ProductModel, _ = Depends(user_auth)):
    new_product = product_controller.create_product(product)
    print(f"{product=}")
    return {"message": "Product created", "product": new_product}


@router.get("/products/getOne/{product_id}")
def get_product(product_id: str, _ = Depends(user_auth)):
    product = product_controller.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/products/update/{product_id}")
def update_product(product_id: str, product: ProductModel, _ = Depends(user_auth)):
    updated_product = product_controller.update_product(product_id, product.dict())
    if not updated_product:
        raise HTTPException(
            status_code=404, detail="Product not found or no changes made"
        )
    return {"message": "Product updated", "product": updated_product}


@router.delete("/products/delete/{product_id}")
def delete_product(product_id: str, _ = Depends(user_auth)):
    success = product_controller.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}
