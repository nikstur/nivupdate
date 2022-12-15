import argparse
import json
import subprocess
from typing import Optional

from .git import Repository


class Dependency:
    name: str
    old_revision: Optional[str]
    new_revision: Optional[str]

    def __init__(self, name: str):
        self.name = name

    def read_revision(self) -> str:
        sources = read_sources()
        return sources[self.name]["rev"]

    def update_message(self) -> str:
        return f"""• Updated dependency '{self.name}':
    '{self.old_revision}'
  → '{self.new_revision}'"""


def main():
    args = parse_args()

    if not args.dependency:
        sources = read_sources()
        dependencies = sources.keys()
    else:
        dependencies = args.dependency

    repo = Repository()

    message_fragments = [update_dependency(dep) for dep in dependencies]
    message_fragments = [i for i in message_fragments if i != ""]
    if message_fragments:
        message_fragments = "\n".join(message_fragments)
        message = f"""sources.json: update {",".join(dependencies)}

{message_fragments}"""

        if args.pr:
            branch_name = f"nivupdate/{'-'.join(dependencies)}"
            repo.commit_on_branch_and_push(branch_name, message)
        else:
            repo.commit(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="nivupdate",
        description="""
        Update Niv dependencies via GitLab Pull Requests with a single command
        """,
    )

    parser.add_argument("dependency", nargs="*")
    parser.add_argument("--pr", action="store_true", help="Open a Pull Request (PR)")

    return parser.parse_args()


def read_sources() -> dict[str, dict[str, str]]:
    with open("nix/sources.json") as f:
        return json.load(f)


def update_dependency(name: str) -> str:
    dependency = Dependency(name)

    dependency.old_revision = dependency.read_revision()

    output = subprocess.run(
        ["niv", "update", dependency.name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if output.returncode != 0:
        print("Failed to run niv:")
        print(output.stdout)

    dependency.new_revision = dependency.read_revision()

    message = dependency.update_message()

    if dependency.old_revision == dependency.new_revision:
        print(f"Dependency '{dependency.name}' already up to date")
        return ""
    else:
        print(message)
        return message


if __name__ == "__main__":
    main()
