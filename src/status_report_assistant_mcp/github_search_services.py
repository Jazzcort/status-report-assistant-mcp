import requests
from .customized_exception import GithubHttpRequestsFailed
from typing import List, Dict


URL = "https://api.github.com/search/issues"
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}


def get_merged_pull_requests(
    author: str, after: str, before: str
) -> List[Dict[str, str]]:
    params = {"q": f"type:pr author:{author} merged:{after}..{before}", "per_page": 100}

    try:
        response = requests.get(URL, headers=HEADERS, params=params)
        response.raise_for_status()
    except Exception:
        raise GithubHttpRequestsFailed(
            "Failed to gather merged pull requests in the given time span"
        )

    data = response.json()
    res = []

    for issue in data["items"]:
        res.append(
            {
                "title": issue["title"],
                "url": issue["html_url"],
                "description": issue["body"],
            }
        )

    return res


def get_pull_requests_created(
    author: str, after: str, before: str
) -> List[Dict[str, str]]:
    params = {
        "q": f"type:pr author:{author} created:{after}..{before}",
        "per_page": 100,
    }

    try:
        response = requests.get(URL, headers=HEADERS, params=params)
        response.raise_for_status()
    except Exception:
        raise GithubHttpRequestsFailed(
            "Failed to gather pull requests created in the given time span"
        )

    data = response.json()
    res = []

    for pr in data["items"]:
        res.append(
            {"title": pr["title"], "url": pr["html_url"], "description": pr["body"]}
        )

    return res


def get_issues_created(author: str, after: str, before: str) -> List[Dict[str, str]]:
    params = {
        "q": f"type:issue author:{author} created:{after}..{before}",
        "per_page": 100,
    }

    try:
        response = requests.get(URL, headers=HEADERS, params=params)
        response.raise_for_status()
    except Exception:
        raise GithubHttpRequestsFailed(
            "Failed to gather issues created in the given time span"
        )

    data = response.json()
    res = []

    for issue in data["items"]:
        res.append(
            {
                "title": issue["title"],
                "url": issue["html_url"],
                "description": issue["body"],
            }
        )

    return res
