from pathlib import Path

from git.refs import Head
from git.remote import Remote
from git.repo import Repo
from git.util import Actor


class Repository:
    repo: Repo
    default_branch: Head
    origin: Remote
    actor: Actor

    def __init__(self):
        self.repo = Repo(Path.cwd())
        # This assumes the currently active branch at the time of invocation is
        # the default branch
        self.default_branch = self.repo.active_branch
        self.origin = self.repo.remotes.origin
        # The email is empty for now. This might be replaced with a GitHub
        # email
        self.actor = Actor("Nivupdate Bot", "")

    def commit(self, message: str):
        self.repo.index.add("nix/sources.json")
        self.repo.index.commit(message, author=self.actor, committer=self.actor)

    def commit_on_branch_and_push(self, branch: str, message: str):
        try:
            new_branch = self.repo.branches[branch]  # type: ignore
        except IndexError:
            new_branch = self.repo.create_head(branch)

        # This fails if the working tree is dirty.
        new_branch.checkout()

        self.commit(message)

        self.origin.push(refspec=f"{branch}:{branch}")

        self.default_branch.checkout()
