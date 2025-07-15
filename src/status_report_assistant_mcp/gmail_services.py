import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
from .utils import get_parent_directory
from .customized_exception import (
    MissingEnvironmentVariables,
    FailToParseCredentials,
    MissingGoogleOAuth2Credentials,
    FailToGetTokenWithGoogleOAuth2Credentials,
    FailToBuildGmailService,
)

GOOGLE_OAUTH2_VAR = "GOOGLE_OAUTH2_CREDENTIALS"
TOKEN_VAR = "CREDENTIAL_TOKEN"

OAUTH2_CREDS_PATH = os.getenv(GOOGLE_OAUTH2_VAR)
CREDENTIAL_TOKEN = os.getenv(TOKEN_VAR)

SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def get_gmail_service():
    creds = None

    if not OAUTH2_CREDS_PATH:
        raise MissingEnvironmentVariables(GOOGLE_OAUTH2_VAR)

    if not CREDENTIAL_TOKEN:
        raise MissingEnvironmentVariables(TOKEN_VAR)

    if os.path.exists(CREDENTIAL_TOKEN):
        try:
            creds = Credentials.from_authorized_user_file(
                CREDENTIAL_TOKEN, scopes=SCOPES
            )
        except Exception:
            raise FailToParseCredentials(CREDENTIAL_TOKEN)

    if not creds:
        if os.path.exists(OAUTH2_CREDS_PATH):
            creds = get_new_token_with_flow(OAUTH2_CREDS_PATH)

            # Create the token credentials
            os.makedirs(get_parent_directory(CREDENTIAL_TOKEN), exist_ok=True)
            with open(CREDENTIAL_TOKEN, "w") as file:
                file.write(creds.to_json())

        else:
            raise MissingGoogleOAuth2Credentials(OAUTH2_CREDS_PATH)
    elif not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = get_new_token_with_flow(OAUTH2_CREDS_PATH)

        # Update the token credentials
        os.makedirs(get_parent_directory(CREDENTIAL_TOKEN), exist_ok=True)
        with open(CREDENTIAL_TOKEN, "w") as file:
            file.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        return service
    except Exception as e:
        raise FailToBuildGmailService(str(e))


def get_new_token_with_flow(oauth2_creds_path: str):
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            oauth2_creds_path, scopes=SCOPES
        )
        creds = flow.run_local_server(port=0)
        return creds

    except Exception:
        raise FailToGetTokenWithGoogleOAuth2Credentials(oauth2_creds_path)


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"message": {"raw": raw}}


def create_draft(service, user_id, message_body):
    draft = service.users().drafts().create(userId=user_id, body=message_body).execute()
    print("Draft created with ID:", draft["id"])
    return draft
