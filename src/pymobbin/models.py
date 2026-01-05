"""Data models for the Mobbin API."""

from typing import Optional, List
import msgspec

# Auth models use snake_case by default

class Token(msgspec.Struct):
    """Auth token response."""
    access_token: str
    refresh_token: str

class UserMetadata(msgspec.Struct):
    """User metadata from Supabase."""
    avatar_url: Optional[str] = None
    full_name: Optional[str] = None

class UserInfo(msgspec.Struct):
    """User information from Supabase auth."""
    id: str
    aud: str
    role: str
    email: str
    email_confirmed_at: Optional[str] = None
    recovery_sent_at: Optional[str] = None
    last_sign_in_at: Optional[str] = None
    user_metadata: UserMetadata = msgspec.field(default_factory=UserMetadata)

class AuthResponse(msgspec.Struct):
    """Response from /auth/v1/verify."""
    access_token: str
    refresh_token: str
    user: UserInfo

# Domain models use camelCase

class Screen(msgspec.Struct, rename="camel"):
    """A screen in an app."""
    id: str
    screen_url: str
    app_version_id: str
    screen_number: Optional[int] = None
    screen_elements: List[str] = []
    screen_patterns: List[str] = []
    updated_at: Optional[str] = None
    created_at: Optional[str] = None

class FlowScreen(msgspec.Struct, rename="camel"):
    """A screen within a flow."""
    app_screen_id: str
    order: int
    screen_url: str
    hotspot_width: Optional[float] = None
    hotspot_height: Optional[float] = None
    hotspot_x: Optional[float] = None
    hotspot_y: Optional[float] = None
    hotspot_type: Optional[str] = None

class Flow(msgspec.Struct, rename="camel"):
    """A user flow."""
    id: str
    name: str
    actions: List[str]
    order: int
    updated_at: str
    app_version_id: str
    screens: List[FlowScreen] = []
    parent_app_section_id: Optional[str] = None

class App(msgspec.Struct, rename="camel"):
    """An iOS app."""
    id: str
    app_name: str
    app_category: str
    app_logo_url: str
    app_tagline: str
    company_hq_region: str
    company_stage: str
    platform: str
    created_at: str
    app_version_id: str
    app_version_created_at: str
    app_version_updated_at: str
    app_version_published_at: str
    preview_screen_urls: List[str]
    app_style: Optional[str] = None

class CollectionApp(msgspec.Struct, rename="camel"):
    """An app within a collection."""
    id: str
    app_name: str
    app_category: str
    app_logo_url: str
    app_tagline: str
    company_hq_region: str
    company_stage: str
    platform: str
    created_at: str
    app_version_id: str
    app_version_created_at: str
    app_version_updated_at: str
    app_version_published_at: str
    collection_app_id: str
    collection_id: str
    collection_app_created_at: str
    collection_app_updated_at: str
    preview_screen_urls: List[str]
    app_style: Optional[str] = None

class Collection(msgspec.Struct, rename="camel"):
    """A user collection."""
    id: str
    name: str
    description: Optional[str] = None
    updated_at: Optional[str] = None
    created_at: Optional[str] = None
    type: Optional[str] = None

class Workspace(msgspec.Struct, rename="camel"):
    """A user workspace."""
    id: str
    name: str
    type: str
