from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List


class AuthMethodField(BaseModel):
    """Defines a single input field for an authentication form."""

    name: str
    label: str
    type: str  # e.g., 'text', 'password'
    placeholder: Optional[str] = None


class SupportedAuthMethod(BaseModel):
    """Describes a supported authentication method for a service."""

    type: str  # e.g., 'api_key', 'oauth2'
    name: str
    preferred: bool = False
    help_text: Optional[str] = None
    help_url: Optional[str] = None
    fields: List[AuthMethodField]


class ApiCatalogBase(BaseModel):
    """Base fields for an entry in the API service catalog."""

    name: str
    description: Optional[str] = None
    category: str = "General"
    icon: Optional[str] = None
    docs_url: Optional[str] = None
    supported_auth_methods: List[SupportedAuthMethod] = Field(default_factory=list)
    primary_api_definition_id: Optional[str] = None  # Should be a string record ID

    connector_provider_key: Optional[str] = Field(
        default=None,
        description="The registration key for the connection strategy (e.g., 'rest-api_key').",
    )
    # This field holds the declarative blueprint for browsing and interaction.
    # We define it as a flexible dictionary.
    browse_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="A declarative blueprint for browsing this service via the VFS.",
    )
    # The blueprint for how to authenticate.
    auth_config: Optional[Dict[str, Any]] = Field(
        default=None, description="A declarative blueprint for handling authentication."
    )
    oauth_config: Optional[Dict[str, Any]] = Field(
        default=None, description="A declarative blueprint for handling OAuth 2.0."
    )
    # The blueprint for how to test the connection.
    test_connection_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Configuration for the 'Test Connection' functionality.",
    )


class ApiCatalog(ApiCatalogBase):
    """The full API Catalog model, including the database ID."""

    id: str
