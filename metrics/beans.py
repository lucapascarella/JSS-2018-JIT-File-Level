import datetime
from collections import KeysView
from typing import List, Dict


class MetricBean:
    def __init__(self, git_hash: str, file_name: str, new_path: str, old_path: str, package: str, change_type: str,
                 file_count: int, file_added: int, file_removed: int, file_nloc: int, file_comp: int, file_token_count: int,
                 file_buggy: bool, file_fix: bool,
                 author_date: datetime, author_email: str,
                 committer_date: datetime, committer_email: str,
                 method_count: int):
        self.git_hash = git_hash
        self.file_name = file_name
        self.new_path = new_path
        self.old_path = old_path
        self.package = package
        self.change_type = change_type

        self.file_count = file_count
        self.file_added = file_added
        self.file_removed = file_removed
        self.file_nloc = file_nloc
        self.file_comp = file_comp
        self.file_token_count = file_token_count

        self.file_buggy = file_buggy
        self.file_fix = file_fix

        self.autho_date = author_date
        self.author_email = author_email
        self.committer_date = committer_date
        self.committer_email = committer_email

        self.method_count = method_count


class MyCommits:
    def __init__(self):
        self.hashes = {}

    def append(self, hash: str, new_path: str, old_path: str):
        path = new_path if new_path is not None else old_path
        if hash in self.hashes:
            self.hashes[hash].append(path)
        else:
            self.hashes[hash] = [path]

    def getHashes(self) -> Dict[str, List[str]]:
        return self.hashes


class MyMetricBeans:
    def __init__(self):
        self.beans = {}  # Dict[str, List[MetricsBean]]

    def add(self, key: str, mb: MetricBean):
        if key not in self.beans:
            self.beans[key] = []
        self.beans.get(key, []).append(mb)

    def remove(self, key: str):
        if key in self.beans:
            del self.beans[key]

    def update_key(self, old_key: str, new_key: str):
        if old_key in self.beans:
            self.beans[new_key] = self.beans.pop(old_key)
        else:
            self.beans[new_key] = []

    def get(self, key: str) -> List[MetricBean]:
        return self.beans.get(key, [])

    def get_keys(self) -> KeysView:
        return self.beans.keys()

    def get_count(self) -> int:
        return len(self.beans)
