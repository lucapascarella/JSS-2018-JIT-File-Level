import csv, os
from datetime import datetime
from pydriller import RepositoryMining, GitRepository

working_path = "../projects/"
repo_name = "accumulo"
repo_git = "https://github.com/apache/accumulo.git"
extensions = [".java", ".js"] #, ".pm"
keywords = ["fix", "bug", "repair", "issue", "error"]


def miner():
    repo_path = os.path.abspath(working_path + repo_name)
    # Clone if necessary
    if not os.path.exists(repo_path):
        print("Cloning: {}".format(repo_name))
        for c in RepositoryMining(repo_git, clone_repo_to=os.path.abspath(working_path)).traverse_commits():
            pass
    else:
        print("{} clone done!".format(repo_name))

    # Extract FIX and BIC
    bic_csv = os.path.abspath(working_path + repo_name + "_bic.csv")
    header = ["hash", "path", "size", "developer", "fix", "bic_path", "bic_hash", "bic_size"]
    no_fix_count = fix_count = 0
    if not os.path.exists(bic_csv):
        print("Extracting FIX and BIC")
        out_file = open(bic_csv, 'w', newline='', encoding="utf-8")
        writer = csv.DictWriter(out_file, delimiter=',', fieldnames=header)
        writer.writeheader()
        to_date = datetime(2017, 6, 1, 12, 0, 0)
        gr = GitRepository(repo_path)
        gr2 = GitRepository(repo_path)
        for commit in RepositoryMining(repo_path, to=to_date, reversed_order=True).traverse_commits():
            msg = commit.msg.lower()
            mods = commit.modifications
            if any(word in msg for word in keywords):
                dout = {"hash": commit.hash, "size": len(mods), "developer": commit.author.email, "fix": True}
                fix_count += 1
                for mod in mods:
                    dout["path"] = mod.new_path
                    bics_per_mod = gr.get_commits_last_modified_lines(commit, mod)
                    for bic_path, bic_commit_hashs in bics_per_mod.items():
                        dout["bic_path"] = bic_path
                        for bic_commit_hash in bic_commit_hashs:
                            bic = gr2.get_commit(bic_commit_hash)
                            dout["bic_hash"] = bic_commit_hash
                            dout["bic_size"] = len(bic.modifications)
                            writer.writerow(dout)
                            out_file.flush()
                if (len(mods)) == 0:
                    dout["path"] = dout["bic_path"] = dout["bic_hash"] = dout["bic_size"] = "---"
                    writer.writerow(dout)
                    out_file.flush()
            else:
                no_fix_count += 1
                dout = {"hash": commit.hash, "size": len(mods), "developer": commit.committer.email, "fix": False, "bic_path": "---", "bic_hash": "---", "bic_size": "---"}
                for mod in mods:
                    dout["path"] = mod.new_path
                    writer.writerow(dout)
                    out_file.flush()
                if (len(mods)) == 0:
                    dout["path"] = "---"
                    writer.writerow(dout)
                    out_file.flush()
        out_file.close()
    else:
        print("Extracting FIX and BIC done!")

    # Get unique BIC
    in_file = open(bic_csv, 'r', newline='', encoding="utf-8")
    reader = csv.DictReader(in_file, delimiter=',')
    unique_devs = set()
    unique_commits = set()
    fixes = set()
    unique_bics = set()
    unique_fics = set()
    for row in reader:
        unique_commits.add(row["hash"])
        if row["path"].endswith(tuple(extensions)):
            unique_devs.add(row["developer"])
            unique_bics.add(row["bic_hash"])
            unique_fics.add(row["bic_path"])
        if row["fix"] == "True":
            fixes.add(row["hash"])
    unique_bics.remove("---")
    unique_fics.remove("---")
    in_file.close()
    print("Developers: {}, Commits: {} Defective: {} {} {}".format(len(unique_devs), len(unique_commits), len(fixes), no_fix_count, fix_count))

    # Count fully and partially defective commits, and defective files in defective commits
    bic_csv = os.path.abspath(working_path + repo_name + "_partial_bic.csv")
    header = ["bic_hash", "bic_size", "bic_file_size", "bic_path", "defective"]
    if not os.path.exists(bic_csv):
        print("Counting partial BIC")
        out_file = open(bic_csv, 'w', newline='', encoding="utf-8")
        writer = csv.DictWriter(out_file, delimiter=',', fieldnames=header)
        writer.writeheader()
        gr = GitRepository(repo_path)
        for bic_hash in unique_bics:
            commit = gr.get_commit(bic_hash)
            diff = count_file = len(commit.modifications)
            dout = {"bic_hash": bic_hash, "bic_size": len(commit.modifications)}
            for mod in commit.modifications:
                if mod.filename.endswith(tuple(extensions)):
                    dout["bic_path"] = mod.new_path
                    dout["bic_file_size"] = mod.nloc
                    if mod.new_path in unique_fics:
                        diff -= 1
                        dout["defective"] = True
                    else:
                        dout["defective"] = False
                    writer.writerow(dout)
                    out_file.flush()
                else:
                    count_file -= 1
                    diff -= 1
        out_file.close()
    else:
        print("Counting partial BIC done!")

    # Calculate partially defective commits
    in_file = open(bic_csv, 'r', newline='', encoding="utf-8")
    reader = csv.DictReader(in_file, delimiter=',')
    bics = {}
    fully_defective = partially_defective = 0
    partially_defective_files = total_defective_files = 0
    for row in reader:
        if row["bic_path"].endswith(tuple(extensions)):
            if row["bic_hash"] in bics:
                bics[row["bic_hash"]].append(row["defective"])
            else:
                bics[row["bic_hash"]] = [row["defective"]]
    for key, value in bics.items():
        count_defective_files = value.count("True")
        if len(value) > 1:
            total_defective_files += len(value)
        if len(value) == count_defective_files or count_defective_files == 1:
            fully_defective += 1
        else:
            partially_defective += 1
            partially_defective_files += count_defective_files
    ratio_defective_files_in_defective_commits = round((partially_defective_files / total_defective_files) * 100, 1)
    ratio_partially_defective_commits = round((partially_defective / (fully_defective + partially_defective)) * 100, 1)
    print("Partially def. commits: {}%. Defective files in partially def. commits: {}%".format(ratio_partially_defective_commits, ratio_defective_files_in_defective_commits))


if __name__ == '__main__':
    print("*** JIT started ***\n")

    miner()

    print("*** JIT finished ***\n")
