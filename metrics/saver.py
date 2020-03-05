from __future__ import division
from typing import List

from pydriller import GitRepository
from beans import MetricBean, MyMetricBeans, MyCommits


class Saver:

    def __init__(self, filename: str, repo_path: str):
        self.filename = filename
        self.repo_path = repo_path

    def create_csv_file(self):
        self.out_file = open(self.filename, 'w')

    def print_csv_header(self):
        header = 'key,git_hash,file_name,path,package,mod_type,' \
                 'COMM,ADEV,DDEV,ADD,DEL,OWN,MINOR,SCTR,NADEV,NDDEV,NCOMM,NSCTR,OEXP,EXP,ND,Entropy,' \
                 'LA,LD,LT,AGE,NUC,CEXP,REXP,SEXP,' \
                 'file_buggy,file_fix\n'

        # print('Header count: {}'.format(header.count(',')))
        self.out_file.write(header)

    def close_csv_file(self):
        self.out_file.flush()
        self.out_file.close()

    def get_COMM(self, index: int, commits: List[MetricBean]) -> int:
        return index

    def get_ADEV(self, index: int, commits: List[MetricBean], beans: MyMetricBeans) -> int:
        devs = set()
        for key in beans.get_keys():
            for mb in beans.get(key):
                devs.add(mb.committer_email)
        return len(devs)

    def get_DDEV(self, index: int, commits: List[MetricBean]) -> int:
        devs = set()
        for i in range(0, index):
            devs.add(commits[i].committer_email)
        return len(devs)

    def get_ADD(self, index: int, commits: List[MetricBean]) -> float:
        item = commits[index]
        if item.file_nloc is not None and item.file_nloc > 0:
            lines = item.file_added
            loc = item.file_nloc
            return lines / loc
        return 0

    def get_DEL(self, index: int, commits: List[MetricBean]) -> float:
        item = commits[index]
        if item.file_nloc is not None and item.file_nloc > 0:
            lines = item.file_removed
            loc = item.file_nloc
            return lines / loc
        return 0

    def get_OWN_MINOR(self, index: int, commits: List[MetricBean]) -> [int, int]:
        if index == 0:
            return 1, 0
        else:
            developers = []
            for i in range(0, index):
                item = commits[i]
                developers.append([item.author_email, item.file_added, item.file_removed])
            dev_cont = {}
            for dev in developers:
                dev_cont[dev[0]] = dev[1] + dev[2]
            dev_max = max(dev_cont, key=dev_cont.get)
            dev_min = min(dev_cont, key=dev_cont.get)
            if commits[index].author_email == dev_max:
                return 1, 0
            elif commits[index].author_email == dev_min:
                return 0, 1
        return 0, 0

    def get_SCTR(self, index: int, commits: List[MetricBean], beans: MyMetricBeans, my_commits: MyCommits) -> int:
        packages = set()
        # for i in range(0, index):
        #     git_hash = commits[i].git_hash
        #     if git_hash in my_commits.hashes:
        #         for path in my_commits.hashes[git_hash]:
        #             for mb in beans.get(path):
        #                 if commits[index].committer_email == mb.committer_email:
        #                     packages.add(mb.package)
        gr = GitRepository(self.repo_path)
        commit = gr.get_commit(commits[index].git_hash)
        if commits[index].committer_email == commit.committer.email:
            for mod in commit.modifications:
                path = mod.new_path if mod.new_path is not None else mod.old_path
                if path.endswith(mod.filename):
                    package = path[:-(len(mod.filename) + 1)]
                    packages.add(package)
        return len(packages)

    def get_NCOMM_NADEV_NNDEV_NSCTR(self, index: int, commits: List[MetricBean], beans: MyMetricBeans, my_commits: MyCommits) -> [int, int, int, int]:
        devs = []
        packages = set()
        # commit_count = set()
        # for i in range(0, index):
        #     git_hash = commits[i].git_hash
        #     if git_hash in my_commits.hashes:
        #         for path in my_commits.hashes[git_hash]:
        #             for mb in beans.get(path):
        #                 commit_count.add(mb.git_hash)
        #                 devs.append(mb.committer_email)
        #                 packages.add(mb.package)

        gr = GitRepository(self.repo_path)
        commit = gr.get_commit(commits[index].git_hash)
        commit_count = 1
        for mod in commit.modifications:
            if mod.new_path is not None and mod.new_path == commits[index].new_path:  # This must be changed
                commits_modified_file = gr.get_commits_modified_file(mod.new_path)
                for cmf in commits_modified_file:
                    commit_count += 1
                    c = gr.get_commit(cmf)
                    devs.append(c.author.email)
                    for m in c.modifications:
                        path = m.new_path if m.new_path is not None else m.old_path
                        if path.endswith(m.filename):
                            package = path[:-(len(m.filename) + 1)]
                            packages.add(package)
        return [commit_count, len(devs), len(set(devs)), len(packages)]

    def get_OEXP(self, index: int, commits: List[MetricBean], developers) -> float:
        if commits[index].author_email in developers:
            return developers[commits[index].author_email] * 100 / sum(developers.values())
        return 0

    def get_EXP(self, index: int, commits: List[MetricBean], developers) -> int:
        if commits[index].author_email in developers:
            return developers[commits[index].author_email]
        return 0

    def get_ND(self, index: int, commits: List[MetricBean], beans: MyMetricBeans) -> int:
        dirs = set()
        for key in beans.get_keys():
            for mb in beans.get(key):
                dirs.add(mb.package)
        return len(dirs)

    def get_Entropy(self, index: int, commits: List[MetricBean], beans: MyMetricBeans) -> float:
        files = {}
        for key in beans.get_keys():
            for mb in beans.get(key):
                if mb.new_path in files:
                    files[mb.new_path] += 1
                else:
                    files[mb.new_path] = 1
        key = commits[index].new_path
        return sum(files.values()) / files[key]

    def get_LT(self, index: int, commits: List[MetricBean]) -> int:
        return commits[index].file_nloc if commits[index].file_nloc is not None else 0

    def get_NUC(self, index: int, commits: List[MetricBean]) -> int:
        count = 0
        for i in range(0, index):
            item = commits[i]
            if item.file_count == 1:
                count += 1
        return count

    def get_AGE(self, index: int, commits: List[MetricBean]) -> int:
        if index > 1:
            return abs(commits[index].committer_date - commits[index - 1].committer_date).total_seconds()
        return 0

    def get_CEXP(self, index: int, commits: List[MetricBean]) -> int:
        count = 0
        for i in range(0, index):
            item = commits[i]
            if item.author_email == commits[index].author_email:
                count += 1
        return count

    def get_REXP(self, index: int, commits: List[MetricBean]) -> int:
        count = 0
        for i in range(0, index):
            item = commits[i]
            diff = abs(commits[index].committer_date - item.committer_date).total_seconds()
            if diff > 10368000 and item.author_email == commits[index].author_email:
                count += 1
        return count

    def get_SEXP(self, index: int, commits: List[MetricBean], beans: MyMetricBeans) -> int:
        package = commits[index].package
        count_commit = 0
        for key in beans.get_keys():
            for mb in beans.get(key):
                if package == mb.package:
                    count_commit += 1
        return count_commit

    def flush(self, commits: List[MetricBean], beans: MyMetricBeans, developers, my_commits: MyCommits):
        if commits is not None and len(commits) > 0:
            commit_count = len(commits)
            for index in range(0, commit_count):
                item = commits[index]
                commit_hash = item.git_hash
                file_name = item.file_name.replace(',', '-comma-')
                key = (commit_hash + "$$" + file_name).replace(',', '-comma-')
                path = item.new_path if item.new_path is not None else item.old_path
                mod_type = item.change_type
                package = item.package
                file_buggy = item.file_buggy
                file_fix = item.file_fix

                # 1
                COMM = self.get_COMM(index, commits)
                ADEV = self.get_ADEV(index, commits, beans)
                DDEV = self.get_DDEV(index, commits)
                ADD = self.get_ADD(index, commits)
                DEL = self.get_DEL(index, commits)
                OWN, MINOR = self.get_OWN_MINOR(index, commits)
                SCTR = self.get_SCTR(index, commits, beans, my_commits)
                NCOMM_NADEV_NNDEV_NSCTR = self.get_NCOMM_NADEV_NNDEV_NSCTR(index, commits, beans, my_commits)
                NCOMM = NCOMM_NADEV_NNDEV_NSCTR[0]
                NADEV = NCOMM_NADEV_NNDEV_NSCTR[1]
                NDDEV = NCOMM_NADEV_NNDEV_NSCTR[2]
                NSCTR = NCOMM_NADEV_NNDEV_NSCTR[3]
                OEXP = self.get_OEXP(index, commits, developers)
                EXP = self.get_EXP(index, commits, developers)
                ND = self.get_ND(index, commits, beans)
                Entropy = self.get_Entropy(index, commits, beans)
                # 2
                LA = item.file_added
                LD = item.file_removed
                LT = self.get_LT(index, commits)
                AGE = self.get_AGE(index, commits)
                NUC = self.get_NUC(index, commits)
                CEXP = self.get_CEXP(index, commits)
                REXP = self.get_REXP(index, commits)
                SEXP = self.get_SEXP(index, commits, beans)

                out_string = '{},{},{},{},{},{},' \
 \
                             '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},' \
                             '{},{},{},{},{},{},{},{},' \
 \
                             '{},{}\n'.format(
                    key, commit_hash, file_name, path, package, mod_type,
                    COMM, ADEV, DDEV, ADD, DEL, OWN, MINOR, SCTR, NADEV, NDDEV, NCOMM, NSCTR, OEXP, EXP, ND, Entropy,
                    LA, LD, LT, AGE, NUC, CEXP, REXP, SEXP,
                    ("TRUE" if file_buggy else "FALSE"), ("TRUE" if file_fix else "FALSE"))

                self.out_file.write(out_string)
        else:
            print("Empty list!")
