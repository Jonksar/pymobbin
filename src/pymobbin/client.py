"""Client for the Mobbin API."""

import asyncio
from typing import Optional, Any, List, TYPE_CHECKING
import httpx
import msgspec

from pymobbin.constants import BASE_URL, ANON_KEY, ORIGIN, REFERER, USER_AGENT
from pymobbin.models import Token, UserInfo, AuthResponse, App, Collection, Workspace

if TYPE_CHECKING:
    import polars as pl


class MobbinClient:
    """Async client for Mobbin API."""

    def __init__(self, access_token: Optional[str] = None, cookie: Optional[str] = None):
        """Initialize the client.
        
        Args:
            access_token: Optional Supabase access token (JWT).
            cookie: Optional 'sb-...' cookie string containing the token.
        """
        self.token: Optional[Token] = None
        if access_token:
            self.token = Token(access_token=access_token, refresh_token="")
        elif cookie:
            # Simple extraction of access_token from cookie if possible
            # Cookie format: sb-<project>-auth-token.0={"access_token":"...","refresh_token":"..."...}
            # We'll just look for the first access_token":"... pattern
            import re
            match = re.search(r'"access_token":"([^"]+)"', cookie)
            if match:
                self.token = Token(access_token=match.group(1), refresh_token="")
                
        self.user_info: Optional[UserInfo] = None
        self.client = httpx.AsyncClient(base_url=BASE_URL)

    async def close(self):
        """Close the underlying HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _headers(self, authenticated: bool = False) -> dict[str, str]:
        """Generate headers for requests."""
        headers = {
            "apikey": ANON_KEY,
            "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "User-Agent": USER_AGENT,
            "Origin": ORIGIN,
            "Referer": REFERER,
            "X-Client-Info": "supabase-js/1.35.7",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept": "*/*",
        }
        
        if authenticated and self.token:
            headers["Authorization"] = f"Bearer {self.token.access_token}"
            # If we have a user token but no custom ANON_KEY (default is likely broken),
            # we might want to let the token serve as the key or just hope for the best.
            # But the server requires 'apikey' header matching the project anon key.
        else:
            headers["Authorization"] = f"Bearer {ANON_KEY}"
            
        return headers

    async def send_email(self, email: str) -> None:
        """Send magic link email (OTP)."""
        url = "/auth/v1/otp"
        headers = self._headers()
        
        body = {
            "email": email,
            "create_user": True,
            "gotrue_meta_security": {}
        }
        
        response = await self.client.post(url, headers=headers, json=body)
        response.raise_for_status()

    async def verify_code(self, email: str, code: str) -> bool:
        """Verify the OTP code."""
        url = "/auth/v1/verify"
        headers = self._headers()
        
        body = {
            "email": email,
            "token": code,
            "type": "magiclink"
        }
        
        response = await self.client.post(url, headers=headers, json=body)
        response.raise_for_status()
        
        data = msgspec.json.decode(response.content, type=AuthResponse)
        
        self.token = Token(
            access_token=data.access_token,
            refresh_token=data.refresh_token
        )
        self.user_info = data.user
        
        return True

    async def refresh_token(self) -> None:
        """Refresh the auth token."""
        if not self.token:
            return

        url = "/auth/v1/token"
        headers = self._headers(authenticated=True)
        
        refresh_headers = headers.copy()
        refresh_headers["Authorization"] = f"Bearer {ANON_KEY}"
        
        params = {"grant_type": "refresh_token"}
        body = {"refresh_token": self.token.refresh_token}
        
        response = await self.client.post(url, headers=refresh_headers, params=params, json=body)
        response.raise_for_status()
        
        data = msgspec.json.decode(response.content)
        
        new_access = data.get("access_token")
        new_refresh = data.get("refresh_token")
        
        if new_access and new_refresh:
            self.token = Token(access_token=new_access, refresh_token=new_refresh)

    async def get_ios_apps(self, limit: int = 24) -> List[App]:
        """Fetch iOS apps."""
        url = "/rest/v1/rpc/get_apps_with_preview_screens_filter"
        headers = self._headers(authenticated=True)
        headers["Content-Profile"] = "public"
        
        all_apps = []
        last_app_id = None
        last_app_version_updated_at = None
        
        page_size = 24
        
        while True:
            body = {
                "filterAppCategories": None,
                "filterAppCompanyStages": None,
                "filterAppPlatform": "ios",
                "filterOperator": "and",
                "lastAppVersionUpdatedAt": last_app_version_updated_at,
                "filterAppStyles": None,
                "filterAppRegions": None,
                "pageSize": page_size,
                "lastAppId": last_app_id,
                "lastAppVersionPublishedAt": None
            }
            
            if all_apps:
                last_app = all_apps[-1]
                body["lastAppVersionPublishedAt"] = last_app.app_version_published_at
            else:
                body["lastAppVersionPublishedAt"] = None

            response = await self.client.post(url, headers=headers, json=body)
            response.raise_for_status()
            
            apps = msgspec.json.decode(response.content, type=List[App])
            if not apps:
                break
                
            all_apps.extend(apps)
            
            if limit and len(all_apps) >= limit:
                all_apps = all_apps[:limit]
                break
                
            last_app = apps[-1]
            last_app_id = last_app.id
            last_app_version_updated_at = last_app.app_version_updated_at

        return all_apps

    async def get_web_apps(self, limit: int = 24) -> List[App]:
        """Fetch Web apps."""
        url = "/rest/v1/rpc/get_apps_with_preview_screens_filter"
        headers = self._headers(authenticated=True)
        headers["Content-Profile"] = "public"
        
        all_apps = []
        last_app_id = None
        last_app_version_updated_at = None
        
        page_size = 24
        
        while True:
            body = {
                "filterAppCategories": None,
                "filterAppCompanyStages": None,
                "filterAppPlatform": "web",
                "filterOperator": "and",
                "lastAppVersionUpdatedAt": last_app_version_updated_at,
                "filterAppStyles": None,
                "filterAppRegions": None,
                "pageSize": page_size,
                "lastAppId": last_app_id,
                "lastAppVersionPublishedAt": None
            }
            
            if all_apps:
                last_app = all_apps[-1]
                body["lastAppVersionPublishedAt"] = last_app.app_version_published_at
            else:
                body["lastAppVersionPublishedAt"] = None

            response = await self.client.post(url, headers=headers, json=body)
            response.raise_for_status()
            
            apps = msgspec.json.decode(response.content, type=List[App])
            if not apps:
                break
                
            all_apps.extend(apps)
            
            if limit and len(all_apps) >= limit:
                all_apps = all_apps[:limit]
                break
                
            last_app = apps[-1]
            last_app_id = last_app.id
            last_app_version_updated_at = last_app.app_version_updated_at

        return all_apps

    async def get_web_apps_df(self, limit: int = 24) -> "pl.DataFrame":
        """Fetch Web apps as a Polars DataFrame."""
        import polars as pl
        apps = await self.get_web_apps(limit=limit)
        return pl.DataFrame([msgspec.structs.asdict(app) for app in apps])

    async def get_workspaces(self) -> List[Workspace]:
        """Fetch user workspaces."""
        if not self.token:
            return []

        url = "/rest/v1/workspaces"
        params = {
            "select": "name,id,type,collections(name,id,updatedAt,createdAt,description)"
        }
        headers = self._headers(authenticated=True)
        
        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        return msgspec.json.decode(response.content, type=List[Workspace])

    async def get_collections(self) -> List[Collection]:
        """Fetch user collections (from the first workspace)."""
        if not self.token:
            return []

        # We can implement this by calling get_workspaces and returning collections from the first one.
        # But we need to reuse the same endpoint/logic to match previous implementation logic.
        
        url = "/rest/v1/workspaces"
        params = {
            "select": "name,id,type,collections(name,id,updatedAt,createdAt,description)"
        }
        headers = self._headers(authenticated=True)
        
        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = msgspec.json.decode(response.content)
        if not data:
            return []
            
        first_workspace = data[0]
        collections_data = first_workspace.get("collections", [])
        return msgspec.convert(collections_data, List[Collection])

    async def create_collection(self, name: str, description: str, workspace_id: str) -> None:
        """Create a new collection."""
        if not self.token or not self.user_info:
            raise RuntimeError("Not authenticated")

        url = "/rest/v1/collections"
        headers = self._headers(authenticated=True)
        headers["Prefer"] = "return=minimal"
        headers["Accept"] = "application/vnd.pgrst.object+json"
        headers["Content-Profile"] = "public"
        
        body = {
            "workspaceId": workspace_id,
            "name": name,
            "description": description,
            "createdBy": self.user_info.id
        }
        
        response = await self.client.post(url, headers=headers, json=body)
        # Swift checks for 201
        if response.status_code != 201:
            response.raise_for_status()
