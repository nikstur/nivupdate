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
    ssh_key: Path | None

    def __init__(self, user: str, email: str, ssh_key: Path | None):
        self.repo = Repo(Path.cwd())
        # This assumes the currently active branch at the time of invocation is
        # the default branch
        self.default_branch = self.repo.active_branch
        self.origin = self.repo.remotes.origin
        self.actor = Actor(user, email)
        self.ssh_key = ssh_key

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
        if self.ssh_key:
            print(f"Using supplied SSH key: {self.ssh_key}")
            ssh_cmd = f"ssh -i {self.ssh_key}"
            with self.repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
                self._push(branch)
        else:
            self._push(branch)

    def _push(self, branch: str):
        print(f"Pushing to: {self.origin.url}")
        self.origin.push(refspec=f"{branch}:{branch}")
