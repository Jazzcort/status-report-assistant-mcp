import os
import subprocess
from typing import Annotated, List, Dict

from fastmcp import FastMCP
from pydantic import Field

from .customized_exception import (
    FailToGetCommitHashes,
    GitCommandNotFound,
    UserEmailNotFound,
)
from .dirs import HOME_DIR
from .gmail_services import create_draft, create_message, get_gmail_service
from .github_search_services import (
    get_merged_pull_requests,
    get_issues_created,
    get_pull_requests_created,
)

mcp = FastMCP("local_git_summary")

# Set up $HOME for Continue
os.environ["HOME"] = HOME_DIR


@mcp.tool()
async def get_root_directory() -> str:
    """Get the root directory of the running machine which usually represents as ~"""
    return os.path.expanduser("~")


@mcp.tool()
async def get_github_summary(
    github_username: Annotated[
        str,
        Field(
            description="The Github username of the person that this github summary is created from"
        ),
    ],
    after: Annotated[
        str,
        Field(
            description="The beginning of the time span. It needs to be like this format YYYY-MM-DD."
        ),
    ],
    before: Annotated[
        str,
        Field(
            description="The end of the time span. It needs to be like this format YYYY-MM-DD."
        ),
    ],
) -> Dict[str, List[Dict[str, str]]] | str:
    """
    Gather the following three lists from Github for the given author in the given time span:
        1. Pull requests that are merged during this time span
        2. Pull requests that are created during this time span
        3. Issues that are created during this time span

    If a pull request appear to be both created and merged in the given time span, it will only appear in the merged pull requests.
    If nothing can be gathered for that specific list, an empty list will be returned
    """

    try:
        prs_merged = get_merged_pull_requests(github_username, after, before)
        prs_merged_url_set = set([pr["url"] for pr in prs_merged])

        prs_created = [
            pr
            for pr in get_pull_requests_created(github_username, after, before)
            if pr["url"] not in prs_merged_url_set
        ]
        issues_created = get_issues_created(github_username, after, before)
    except Exception as e:
        return f"{str(e)}"

    res = {
        "Pull requests merged": prs_merged,
        "Pull requests created": prs_created,
        "Issues created": issues_created,
    }

    return res


@mcp.tool()
async def gather_work_log_with_author_email(
    author_email: Annotated[
        str, Field(description="The email of the author of the commits")
    ],
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
) -> (
    Dict[
        Annotated[str, Field(description="Path of the directory")],
        Annotated[List[str], Field(description="List of all the commit messages")],
    ]
    | str
):
    """Gather all the commit messages with the given author's email within the given time span for the given direscories. This can be used as a fallback tool call when user.email is not set in the global scope or it can be used to gather the work log for a specific author."""

    log = dict()

    try:
        for dir in dirs:
            commit_lst = gather_git_commits(
                convert_relative_to_absolute(dir), after, before, author_email
            )
            if commit_lst:
                log[dir] = commit_lst

        return log if len(log) != 0 else "No work log in the given time span"
    except Exception as e:
        return f"Failed to gather work log: {e}"


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
) -> (
    Dict[
        Annotated[str, Field(description="Path of the directory")],
        Annotated[List[str], Field(description="List of all the commit messages")],
    ]
    | str
):
    """Gather all the commit messages with user.email as the author's email within the given time span for the given direscories"""

    log = dict()

    try:
        for dir in dirs:
            commit_lst = gather_git_commits(
                convert_relative_to_absolute(dir), after, before
            )
            if commit_lst:
                log[dir] = commit_lst

        return log if len(log) != 0 else "No work log in the given time span"
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


def gather_git_commits(
    dir: str, after: str, before: str = "now", author_email: str = ""
) -> List[str]:
    hashes = gather_git_commit_hash(dir, after, before, author_email)

    commit_lst = []

    for hash in hashes:
        details = gather_commit_details(dir, hash)
        # Ignore if no details for this commit (e.g. command failed for some reasons)
        if details:
            commit_lst.append(details)

    return commit_lst


def gather_git_commit_hash(
    dir: str, after: str, before: str = "now", author_email: str = ""
) -> List[str]:
    user_email = get_author_email() if not author_email else author_email

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
