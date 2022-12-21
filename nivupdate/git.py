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

    def __init__(self, user: str, email: str):
        self.repo = Repo(Path.cwd())
        # This assumes the currently active branch at the time of invocation is
        # the default branch
        self.default_branch = self.repo.active_branch
        self.origin = self.repo.remotes.origin
        self.actor = Actor(user, email)

    def commit(self, message: str):
        self.repo.index.add("nix/sources.json")
        self.repo.index.commit(message, author=self.actor, committer=self.actor)

    def checkout(self, branch: str):
        try:
            new_branch = self.repo.branches[branch]  # type: ignore
        except IndexError:
            new_branch = self.repo.create_head(branch)

        # This fails if the working tree is dirty.
        new_branch.checkout()

    def checkout_default(self):
        self.default_branch.checkout()

    def push(self, branch: str):
        self.origin.push(refspec=f"{branch}:{branch}")
