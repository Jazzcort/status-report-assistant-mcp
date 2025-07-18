# Git commands related errors
class UserEmailNotFound(Exception):
    def __init__(self, message: str = ""):
        if message:
            super().__init__(f"Can't find user.email for git: {message}")
        else:
            super().__init__("Can't find user.email for git")


class GitCommandNotFound(Exception):
    def __init__(self):
        super().__init__("Git command not found in the specified directory or PATH")


class FailToGetCommitHashes(Exception):
    def __init__(self, dir: str):
        super().__init__(f"Fail to get commit hashes for the given directoies: {dir}")


# Gmail API related errors
class MissingGoogleOAuth2Credentials(Exception):
    def __init__(self, path: str):
        super().__init__(
            f"Can't find the Google OAuth2 credentials with the given path: {path}"
        )


class FailToGetTokenWithGoogleOAuth2Credentials(Exception):
    def __init__(self, path: str):
        super().__init__(
            f"Fail to get token credentials with the given Google OAuth2 credentials: {path}"
        )


class MissingEnvironmentVariables(Exception):
    def __init__(self, var_name: str):
        super().__init__(f"Can't find {var_name} in the given .env file")


class FailToParseCredentials(Exception):
    def __init__(self, path: str):
        super().__init__(f"Fail to parse the credentials for the given file: {path}")


class FailToBuildGmailService(Exception):
    def __init__(self, err: str):
        super().__init__(f"Fail to build a service with gmail: {err}")


# Github search requests errors
class GithubHttpRequestsFailed(Exception):
    def __init__(self, err: str):
        super().__init__(f"Github HTTP request error: {err}")
