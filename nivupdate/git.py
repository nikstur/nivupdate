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
    ssh_cmd: Path | None

    def __init__(self, user: str, email: str, ssh_cmd: Path | None) -> None:
        self.repo = Repo(Path.cwd())
        # This assumes the currently active branch at the time of invocation is
        # the default branch
        self.default_branch = self.repo.active_branch
        self.origin = self.repo.remotes.origin
        self.actor = Actor(user, email)
        self.ssh_cmd = ssh_cmd

    def commit(self, message: str) -> None:
        self.repo.index.add("nix/sources.json")
        self.repo.index.commit(
            message, author=self.actor, committer=self.actor, skip_hooks=True
        )

    def checkout(self, branch: str) -> None:
        try:
            new_branch = self.repo.branches[branch]  # type: ignore
        except IndexError:
            new_branch = self.repo.create_head(branch)

        # This fails if the working tree is dirty.
        new_branch.checkout()

    def checkout_default(self) -> None:
        self.default_branch.checkout()

    def push(self, branch: str) -> None:
        if self.ssh_cmd:
            with self.repo.git.custom_environment(GIT_SSH_COMMAND=self.ssh_cmd):
                self._push(branch)
        else:
            self._push(branch)

    def _push(self, branch: str) -> None:
        self.repo.git.push("--force", "--set-upstream", self.origin.name, branch)
