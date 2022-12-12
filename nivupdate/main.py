import argparse
import json
import subprocess
from typing import Optional


class Dependency:
    name: str
    old_revision: Optional[str]
    new_revision: Optional[str]

    def __init__(self, name: str):
        self.name = name

    def read_revision(self) -> str:
        sources = read_sources()
        return sources[self.name]["rev"]

    def update_comment(self) -> str:
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

    comment_fragments = [update_dependency(dep) for dep in dependencies]
    comment_fragments = [i for i in comment_fragments if i != ""]
    if comment_fragments:
        comment_fragments = "\n".join(comment_fragments)
        comment = f"""source.json: update
{comment_fragments}"""

        print(comment)


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

    comment = dependency.update_comment()

    if dependency.old_revision == dependency.new_revision:
        print(f"Dependency '{dependency.name}' already up to date")
        return ""
    else:
        print(comment)
        return comment


if __name__ == "__main__":
    main()
