from pydantic import BaseModel, Field
from typing import Optional


class ProductModel(BaseModel):
    image: Optional[str] = None
    name: str
    category: str
    stok: int
    stokMenipis: Optional[int] = Field(0)
    satuan: str
    price: float
    status: bool
    description: Optional[str] = None
