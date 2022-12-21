import argparse
from pathlib import Path

import requests

from . import gitlab
from .dependency import Dependency, read_sources
from .git import Repository


def main():
    args = parse_args()

    repo = Repository(args.user, args.email, args.ssh_key)

    for dependency_name in args.dependencies:
        dependency = Dependency(dependency_name)

        if args.mr:
            branch_name = f"nivupdate/{dependency.name}"
            repo.checkout(branch_name)

            message = dependency.update()
            if not message:
                repo.checkout_default()
                continue

            repo.commit(message)
            repo.push(branch_name)
            repo.checkout_default()

            subject_line = message.splitlines()[0]
            response = gitlab.open_merge_request(
                args.url, branch_name, repo.default_branch.name, title=subject_line
            )
            if response.status_code != requests.codes.created:
                print(response.reason, ":", response.text)
        else:
            message = dependency.update()
            if not message:
                continue
            repo.commit(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="nivupdate",
        description="""
        Update Niv dependencies via GitLab Pull Requests using a single command
        """,
    )

    parser.add_argument("dependencies", nargs="*")
    parser.add_argument("--mr", action="store_true", help="Open a Merge Request")
    parser.add_argument("--url", help="URL of project")
    parser.add_argument("--ssh-key", type=Path, help="Path to SSH key to use")
    parser.add_argument("--user", help="Git user name")
    parser.add_argument("--email", help="Git user email")

    args = parser.parse_args()

    # Update all dependencies if none are explicitly specified
    if not args.dependencies:
        sources = read_sources()
        args.dependencies = sources.keys()

    if (args.mr and not args.url) or (args.url and not args.mr):
        parser.error("Opening a MR requires an URL (--url).")

    return args


if __name__ == "__main__":
    main()
