from pydantic import BaseModel
from typing import List, Optional

class UserFilterModel(BaseModel):
    search: Optional[str] = None
    search_by: List[str] = []
    operator: Optional[str] = "and"  
    orderBy: Optional[str] = "created_at"
    order: Optional[str] = "desc"    
    page: int = 1
    size: int = 10
