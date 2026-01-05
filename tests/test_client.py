import pytest
import respx
import polars as pl
from httpx import Response
from pymobbin.client import MobbinClient
from pymobbin.constants import BASE_URL, ANON_KEY
from pymobbin.models import Token, UserInfo

@pytest.fixture
def authenticated_client():
    client = MobbinClient()
    client.token = Token(access_token="acc", refresh_token="ref")
    client.user_info = UserInfo(id="u1", aud="aud", role="role", email="e@mail.com")
    return client

# ... (previous tests) ...

@pytest.mark.asyncio
async def test_send_email():
    async with MobbinClient() as client:
        with respx.mock(base_url=BASE_URL) as mock:
            route = mock.post("/auth/v1/otp").mock(return_value=Response(200, json={}))
            
            email = "test@example.com"
            await client.send_email(email)
            
            assert route.called
            request = route.calls.last.request
            assert request.headers["apikey"] == ANON_KEY
            assert request.headers["Authorization"] == f"Bearer {ANON_KEY}"
            
            import json
            body = json.loads(request.content)
            assert body["email"] == email
            assert body["create_user"] is True

@pytest.mark.asyncio
async def test_verify_code():
    async with MobbinClient() as client:
        with respx.mock(base_url=BASE_URL) as mock:
            mock_response = {
                "access_token": "acc_123",
                "refresh_token": "ref_123",
                "user": {
                    "id": "u1",
                    "aud": "authenticated",
                    "role": "authenticated",
                    "email": "test@example.com",
                    "user_metadata": {
                        "full_name": "Test User",
                        "avatar_url": "http://example.com/avatar.jpg"
                    },
                    "email_confirmed_at": "2023-01-01T00:00:00Z",
                    "recovery_sent_at": "2023-01-01T00:00:00Z",
                    "last_sign_in_at": "2023-01-01T00:00:00Z"
                }
            }
            route = mock.post("/auth/v1/verify").mock(return_value=Response(200, json=mock_response))
            
            email = "test@example.com"
            code = "123456"
            result = await client.verify_code(email, code)
            
            assert result is True
            assert client.token.access_token == "acc_123"
            assert client.token.refresh_token == "ref_123"
            assert client.user_info.email == email

@pytest.mark.asyncio
async def test_get_ios_apps(authenticated_client):
    async with authenticated_client as client:
        with respx.mock(base_url=BASE_URL) as mock:
            mock_apps = [
                {
                    "id": "app1",
                    "appName": "Test App",
                    "appCategory": "Social",
                    "appLogoUrl": "http://logo.com",
                    "appTagline": "Tagline",
                    "companyHqRegion": "US",
                    "companyStage": "IPO",
                    "platform": "ios",
                    "createdAt": "2023-01-01",
                    "appVersionId": "v1",
                    "appVersionCreatedAt": "2023-01-01",
                    "appVersionUpdatedAt": "2023-01-01",
                    "appVersionPublishedAt": "2023-01-01",
                    "previewScreenUrls": []
                }
            ]
            route = mock.post("/rest/v1/rpc/get_apps_with_preview_screens_filter").mock(return_value=Response(200, json=mock_apps))
            
            apps = await client.get_ios_apps(limit=1)
            
            assert len(apps) == 1
            assert apps[0].app_name == "Test App"
            assert route.called

@pytest.mark.asyncio
async def test_get_collections(authenticated_client):
    async with authenticated_client as client:
        with respx.mock(base_url=BASE_URL) as mock:
            mock_workspace = [
                {
                    "id": "ws1",
                    "name": "Workspace 1",
                    "type": "team",
                    "collections": [
                        {
                            "id": "col1",
                            "name": "My Collection",
                            "updatedAt": "2023-01-01",
                            "createdAt": "2023-01-01"
                        }
                    ]
                }
            ]
            route = mock.get("/rest/v1/workspaces").mock(return_value=Response(200, json=mock_workspace))
            
            cols = await client.get_collections()
            
            assert len(cols) == 1
            assert cols[0].name == "My Collection"
            assert route.called

@pytest.mark.asyncio
async def test_get_ios_apps_df(authenticated_client):
    async with authenticated_client as client:
        with respx.mock(base_url=BASE_URL) as mock:
            mock_apps = [
                {
                    "id": "app1",
                    "appName": "Test App",
                    "appCategory": "Social",
                    "appLogoUrl": "http://logo.com",
                    "appTagline": "Tagline",
                    "companyHqRegion": "US",
                    "companyStage": "IPO",
                    "platform": "ios",
                    "createdAt": "2023-01-01",
                    "appVersionId": "v1",
                    "appVersionCreatedAt": "2023-01-01",
                    "appVersionUpdatedAt": "2023-01-01",
                    "appVersionPublishedAt": "2023-01-01",
                    "previewScreenUrls": []
                }
            ]
            route = mock.post("/rest/v1/rpc/get_apps_with_preview_screens_filter").mock(return_value=Response(200, json=mock_apps))
            
            df = await client.get_ios_apps_df(limit=1)
            
            assert isinstance(df, pl.DataFrame)
            assert df.height == 1
            assert df["app_name"][0] == "Test App"

@pytest.mark.asyncio
async def test_create_collection(authenticated_client):
    async with authenticated_client as client:
        with respx.mock(base_url=BASE_URL) as mock:
            route = mock.post("/rest/v1/collections").mock(return_value=Response(201, json={}))
            
            await client.create_collection("New Col", "Desc", "ws1")
            
            assert route.called
            request = route.calls.last.request
            import json
            body = json.loads(request.content)
            assert body["workspaceId"] == "ws1"
            assert body["name"] == "New Col"
            assert body["createdBy"] == "u1"
