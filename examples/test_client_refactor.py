import asyncio
from pymobbin.client import MobbinClient

# Extracted from browser
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsImtpZCI6ImUxb3dtd2dYV216TkhSVUEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3VqYXNudGtmcGh5d2l6c2RhYXBpLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2YjlhZWI4MS05NTY1LTRhYTAtOTg0YS03YmE2NGUxZDEwM2YiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY3NjIyNTEyLCJpYXQiOjE3Njc2MTg5MTIsImVtYWlsIjoiam9vbmF0YW5AcmVpdGVyYXRlLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZ29vZ2xlIiwicHJvdmlkZXJzIjpbImdvb2dsZSJdfSwidXNlcl9tZXRhZGF0YSI6eyJjdXN0b21fY2xhaW1zIjp7ImhkIjoicmVpdGVyYXRlLmNvbSJ9LCJlbWFpbCI6Impvb25hdGFuQHJlaXRlcmF0ZS5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZnVsbF9uYW1lIjoiSm9vbmF0YW4gU2FtdWVsIiwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tIiwibmFtZSI6Ikpvb25hdGFuIFNhbXVlbCIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwicHJvdmlkZXJfaWQiOiIxMDI2MDg5OTk2NTQzNzIwNDE3NDAiLCJzdWIiOiIxMDI2MDg5OTk2NTQzNzIwNDE3NDAifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJvdHAiLCJ0aW1lc3RhbXAiOjE3Njc2MTg5MTJ9XSwic2Vzc2lvbl9pZCI6IjVmN2U2MTdhLTdiY2YtNDcyZC1iNGNjLTI4MmVjNjJmMGFjOSIsImlzX2Fub255bW91cyI6ZmFsc2V9.TFjawXUkKrhBMw4fwNoDCBffWVP6YgY5QEdCVIEQv80"

async def main():
    async with MobbinClient(access_token=ACCESS_TOKEN) as client:
        print("Attempting to fetch web apps...")
        try:
            # We still expect this to fail with 401 because ANON_KEY is likely bad
            # But verifying the client structure works
            apps = await client.get_web_apps(limit=5)
            for app in apps:
                print(f"- {app.app_name}")
        except Exception as e:
            print(f"Expected failure (until Anon Key fixed): {e}")

if __name__ == "__main__":
    asyncio.run(main())

