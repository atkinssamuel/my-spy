import os

from dotenv import load_dotenv
from google_auth_wrapper import credentials

if __name__ == "__main__":
    load_dotenv()

    creds = credentials(
        scopes=[os.getenv("GOOGLE_SCOPE")],
        client=os.getenv("GOOGLE_CLIENT_ID"),
        secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        path_to_refresh="refresh.txt",
    )

    