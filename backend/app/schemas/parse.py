"""Request schemas for parse endpoints."""

from pydantic import BaseModel, Field


class ParseUrlRequest(BaseModel):
    url: str = Field(..., examples=["https://eda.rambler.ru/recepty/osnovnye-blyuda/example"])


class ParseHtmlRequest(BaseModel):
    html: str = Field(..., min_length=1)
    source_name: str = Field(default="manual test", max_length=255)

