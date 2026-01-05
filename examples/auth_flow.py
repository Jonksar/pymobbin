import asyncio
import os
from pymobbin.client import MobbinClient

async def main():
    print("Mobbin Auth Flow")
    email = input("Enter your email: ")
    
    async with MobbinClient() as client:
        print(f"Sending OTP to {email}...")
        try:
            await client.send_email(email)
            print("Email sent! Check your inbox.")
        except Exception as e:
            print(f"Error sending email: {e}")
            return

        code = input("Enter the 6-digit code: ")
        print("Verifying code...")
        
        try:
            success = await client.verify_code(email, code)
            if success:
                print("Login successful!")
                print(f"Access Token: {client.token.access_token[:10]}...")
                print(f"User: {client.user_info.email}")
            else:
                print("Login failed.")
        except Exception as e:
            print(f"Error verifying code: {e}")

if __name__ == "__main__":
    asyncio.run(main())

