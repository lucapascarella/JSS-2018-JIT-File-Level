import os
from datetime import datetime
from typing import List, Dict, Set
from pydriller import RepositoryMining, GitRepository
from pydriller.domain.commit import ModificationType

from beans import MetricBean, MyMetricBeans, MyCommits
from saver import Saver


class Miner:
    def __init__(self, repo_path: str, allowed_extensions: List[str], csv_path: str, bic_commits: Set[str] = set(), fix_commits: Set[str] = [str]):
        if repo_path is None:
            print('A local repository path must be specified')
            exit(-1)
        elif os.path.isdir(repo_path):
            self.repo_path = repo_path
            self.csv_file = csv_path
            self.allowed_extensions = allowed_extensions
            self.bic_commits = bic_commits
            self.fix_commits = fix_commits
        else:
            print('The following path does not exist: ' + repo_path)
            exit(-1)

    def mine(self, start_date: datetime, stop_date: datetime) -> int:
        beans = MyMetricBeans()
        developers = {}
        my_commits = MyCommits()
        commits_to_analyze = -1
        print('Mining: ' + self.repo_path)
        gr = GitRepository(self.repo_path)

        # Unnecessary in production
        # Count commits to analyze
        print('Retrieve commits to analyze.')
        commits = []
        for commit in RepositoryMining(self.repo_path, since=start_date, to=stop_date).traverse_commits():
            commits.append(commit)
            print('{}) {} {}'.format(len(commits), commit.hash, commit.author_date))
        commits_to_analyze = len(commits)

        # Open CSV file and write header
        saver = Saver(self.csv_file, self.repo_path)
        saver.create_csv_file()
        saver.print_csv_header()

        # Traverse commits and calculate metrics
        commit_count = 0
        # for commit in RepositoryMining(self.repo_path, from_commit=last_commit, to_commit=first_commit, reversed_order=True, only_modifications_with_file_types=self.allowed_extensions).traverse_commits():
        for commit in RepositoryMining(self.repo_path, since=start_date, to=stop_date).traverse_commits():
            buggy = True if commit.hash in self.bic_commits else False
            fix = True if commit.hash in self.fix_commits else False
            mod_analyzed_count = 0
            count_files_per_commit = len(commit.modifications)
            for mod in commit.modifications:
                # Filter out unnecessary files
                count_methods_per_file = -1  # len(mod.methods)
                if mod.filename.endswith(tuple(self.allowed_extensions)):
                    package = self.get_package(mod.new_path, mod.old_path, mod.filename)
                    my_commits.append(commit.hash, mod.new_path, mod.old_path)
                    mb = MetricBean(commit.hash, mod.filename, mod.new_path, mod.old_path, package, mod.change_type.name,
                                    count_files_per_commit, mod.added, mod.removed, mod.nloc, mod.complexity, mod.token_count,
                                    buggy, fix,
                                    commit.author_date, commit.author.email, commit.committer_date, commit.committer.email,
                                    count_methods_per_file)
                    mod_analyzed_count += 1
                    if mod.change_type is ModificationType.ADD:
                        # Add new key and metrics
                        key = mod.new_path
                        beans.add(key, mb)
                    elif mod.change_type is ModificationType.COPY:
                        # Add new key and metrics
                        key = mod.new_path
                        beans.add(key, mb)
                        print("CASE COPY: {} {}".format(mod.new_path, mod.old_path))
                    elif mod.change_type is ModificationType.DELETE:
                        # Flush in file and remove key
                        key = mod.old_path
                        beans.add(key, mb)
                        commit_list_of_file = beans.get(key)
                        saver.flush(commit_list_of_file, beans, developers, my_commits)
                        beans.remove(key)
                    elif mod.change_type is ModificationType.RENAME:
                        # Update key and metrics
                        old_key = mod.old_path
                        new_key = mod.new_path
                        beans.add(old_key, mb)
                        beans.update_key(old_key, new_key)
                    else:
                        # Update metrics
                        key = mod.new_path
                        beans.add(key, mb)
                    if commit.author.email in developers:
                        developers[commit.author.email] += mod.added
                    else:
                        developers[commit.author.email] = mod.added
            commit_count += 1
            print('Files: {:>8} | Commit {:>6}/{:<6} {} Date: {} Mods: {:>4}/{:<4} | Bug: {} Fix: {}'.format(beans.get_count(), commit_count, commits_to_analyze, commit.hash, commit.author_date.strftime('%d/%m/%Y'),
                                                                                                             count_files_per_commit, mod_analyzed_count, buggy, fix))

        # Flush everything else
        print("Save metrics, it's require time!")
        count = 1
        key_number = len(beans.get_keys())
        for key in beans.get_keys():
            print("Save: {}/{}".format(count, key_number))
            saver.flush(beans.get(key), beans, developers, my_commits)
            count += 1
        saver.close_csv_file()
        print('Mining ended')
        return commit_count

    def get_package(self, new_path: str, old_path: str, filename: str) -> str:
        path = new_path if new_path is not None else old_path
        if path.endswith(filename):
            return path[:-(len(filename) + 1)]
        return "/"
