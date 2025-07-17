import os
import subprocess
from typing import Annotated, List

from fastmcp import FastMCP
from pydantic import Field

from .customized_exception import (
    FailToGetCommitHashes,
    GitCommandNotFound,
    UserEmailNotFound,
)
from .dirs import HOME_DIR
from .gmail_services import create_draft, create_message, get_gmail_service

mcp = FastMCP("local_git_summary")

# Set up $HOME for Continue
os.environ["HOME"] = HOME_DIR


@mcp.tool()
async def get_root_directory() -> str:
    """Get the root directory of the running machine which usually represents as ~"""
    return os.path.expanduser("~")


@mcp.tool()
async def gather_work_log(
    dirs: Annotated[
        List[str],
        Field(
            description="Path of the directory where the work log should be generated from. Never pass the directory that contains . in its path, but ~ is okay."
        ),
    ],
    after: Annotated[
        str, Field(description="The starting point of the time span for the work log")
    ],
    before: Annotated[
        str, Field(description="The ending point of the time span for the work log")
    ] = "now",
) -> str:
    """Gather all the commit messages within the given time span for the given direscories"""

    log = ""

    try:
        for dir in dirs:
            dir_log = gather_git_commits(
                convert_relative_to_absolute(dir), after, before
            )
            if dir_log:
                log += f"{dir_log}\n"

        return log if log else "No work log in the given time span"
    except Exception as e:
        return f"Failed to gather work log: {e}"


@mcp.tool()
async def create_draft_email(
    to: Annotated[List[str], Field(description="Recipients of this email draft")],
    subject: Annotated[str, Field(description="Subject of this draft email")],
    content: Annotated[str, Field(description="Content of this draft email")],
) -> str:
    """Create a draft email with the given subject, content, and receiver"""
    try:
        service = get_gmail_service()
        message_body = create_message("me", to, subject, content)
        create_draft(service, "me", message_body)
        return "Successfully created the draft email!"
    except Exception as e:
        return f"Failed to create the draft email: {e}"


def convert_relative_to_absolute(path: str) -> str:
    if not path:
        return path

    path_parts = path.split("/")

    if path_parts[0] == "~":
        path_parts[0] = HOME_DIR

    return "/".join(path_parts)


def gather_commit_details(dir: str, commit_hash: str) -> str:
    try:
        result = subprocess.run(
            ["git", "show", "--stat", f"{commit_hash}"],
            cwd=dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def gather_git_commits(dir: str, after: str, before: str = "now") -> str:
    hashes = gather_git_commit_hash(dir, after, before)

    full_content = ""

    for hash in hashes:
        details = gather_commit_details(dir, hash)
        # Ignore if no details for this commit (e.g. command failed for some reasons)
        if details:
            full_content += f"{details}\n"

    return full_content


def gather_git_commit_hash(dir: str, after: str, before: str = "now") -> List[str]:
    user_email = get_author_email()

    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--all",
                '--pretty=format:"%h"',
                f"--author={user_email}",
                f'--after="{after}"',
                f'--before="{before}"',
            ],
            cwd=dir,
            capture_output=True,
            text=True,
            check=True,
        )

        commits = result.stdout.split("\n")

        return [commit.strip('"') for commit in commits]
    except Exception:
        raise FailToGetCommitHashes(dir)


def get_author_email() -> str:
    try:
        result = subprocess.run(
            ["git", "config", "--global", "user.email"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise UserEmailNotFound(str(e))

    except FileExistsError:
        raise GitCommandNotFound()


def main():
    # trigger()
    mcp.run()


if __name__ == "__main__":
    main()
