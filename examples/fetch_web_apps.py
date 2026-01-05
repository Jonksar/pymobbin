"""Example showing how to fetch web apps from Mobbin."""

import asyncio
from pymobbin.client import MobbinClient

async def main():
    # Option 1: Initialize with browser cookie
    cookie = "sb-ujasntkfphywizsdaapi-auth-token.0=<your_cookie_value>"
    
    async with MobbinClient(cookie=cookie) as client:
        print("Fetching web apps...")
        apps = await client.get_web_apps(limit=10)
        
        for app in apps:
            print(f"\n{app.app_name}")
            print(f"  Category: {app.app_category}")
            print(f"  Tagline: {app.app_tagline}")
            print(f"  Platform: {app.platform}")
            if app.keywords:
                print(f"  Keywords: {', '.join(app.keywords)}")

if __name__ == "__main__":
    asyncio.run(main())

