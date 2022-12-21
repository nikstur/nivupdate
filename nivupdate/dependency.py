import json
import subprocess
import sys


class Dependency:
    name: str

    def __init__(self, name: str):
        self.name = name

    def read_revision(self) -> str:
        sources = read_sources()
        return sources[self.name]["rev"]

    def commit_message(self, old_revision, new_revision) -> str:
        return f"""sources.json: update {self.name}

• Updated dependency '{self.name}':
    '{old_revision}'
  → '{new_revision}'"""

    def update(self) -> str:
        old_revision = self.read_revision()

        output = subprocess.run(
            ["niv", "update", self.name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if output.returncode != 0:
            print("Failed to run niv:")
            print(output.stdout)
            raise Exception

        new_revision = self.read_revision()

        message = self.commit_message(old_revision, new_revision)

        if old_revision == new_revision:
            print(f"Dependency '{self.name}' already up to date")
            return ""
        else:
            # Only print the body of the message not the subject
            print("\n".join(message.splitlines()[2:]))
            return message


def read_sources() -> dict[str, dict[str, str]]:
    try:
        with open("nix/sources.json") as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit("'nix/sources.json' does not exist.")
