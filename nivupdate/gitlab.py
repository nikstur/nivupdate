from urllib.parse import urlparse

import requests

PROJECTS_PATH = "api/v4/projects"


def open_merge_request(
    url: str,
    source_branch: str,
    target_branch: str,
    title: str,
    token: str,
) -> requests.Response:
    url = assemble_url(url)

    data = {
        "source_branch": source_branch,
        "target_branch": target_branch,
        "title": title,
        "remove_source_branch": True,
        "allow_collaboration": True,
        "labels": "nivupdate,bot",
    }

    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(url, data=data, headers=headers)


def assemble_url(project_url: str) -> str:
    parsed_url = urlparse(project_url)
    project_id = "%2F".join(parsed_url.path.strip("/").split("/"))
    return f"https://{parsed_url.netloc}/{PROJECTS_PATH}/{project_id}/merge_requests"
