from typing import List, Literal, Optional, TypedDict

from ._base import Resource
from .types import DeletedResponse, SearchPaginationParams

TemplateStyle = Literal["HTML", "MARKUP"]


class _CreateTemplateParamsRequired(TypedDict):
    title: str
    content: str


class CreateTemplateParams(_CreateTemplateParamsRequired, total=False):
    style: TemplateStyle


class UpdateTemplateParams(TypedDict, total=False):
    title: str
    content: str
    style: TemplateStyle


class Template(TypedDict):
    id: str
    title: str
    content: str
    style: TemplateStyle
    projectId: str
    createdAt: str
    updatedAt: str


class _ListTemplatesResponseRequired(TypedDict):
    items: List[Template]


class ListTemplatesResponse(_ListTemplatesResponseRequired, total=False):
    total: int
    page: int
    totalPages: int
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class Templates(Resource):
    """Templates API resource"""

    def list(
        self, params: Optional[SearchPaginationParams] = None
    ) -> ListTemplatesResponse:
        """List reusable email templates with optional pagination and search."""
        return self._client.get("/templates", params)

    def create(self, data: CreateTemplateParams) -> Template:
        """Create a reusable email template from content and optional styles."""
        return self._client.post("/templates", data)

    def get(self, template_id: str) -> Template:
        """Retrieve a template by ID."""
        return self._client.get(f"/templates/{template_id}")

    def update(self, template_id: str, data: UpdateTemplateParams) -> Template:
        """Update a template while preserving omitted fields."""
        return self._client.put(f"/templates/{template_id}", data)

    def delete(self, template_id: str) -> DeletedResponse:
        """Delete a template without affecting email already sent from it."""
        return self._client.delete(f"/templates/{template_id}")

    def duplicate(self, template_id: str) -> Template:
        """Create an independent copy of a template for further editing."""
        return self._client.post(f"/templates/{template_id}/duplicate", {})
