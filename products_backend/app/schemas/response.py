from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel):
    """Base response schema"""
    success: bool = True
    message: str = "Success"


class DataResponse(BaseResponse, Generic[T]):
    """Response with data"""
    data: Optional[T] = None


class ListResponse(BaseResponse, Generic[T]):
    """Response for list of items"""
    data: List[T] = []


class PaginatedResponse(ListResponse[T], Generic[T]):
    """Paginated response"""
    total: int = 0
    page: int = 1
    per_page: int = 10
    total_pages: int = 0


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    message: str
    detail: Optional[str] = None
