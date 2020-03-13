import csv
import os

working_path = "../projects/"
projects = ["accumulo"]


# projects = ["accumulo", "angular.js", "bugzilla", "gerrit", "gimp", "hadoop", "JDeodorant", "jetty.project", "jruby", "openjpa"]

class Bic:
    def __init__(self, hash: str):
        self.hash = hash
        self.defective = 0
        self.size = 0


def effort():
    total_size = 0
    total_bugs = 0
    bics = {}
    for project in projects:
        in_file = os.path.abspath(working_path + project + "_partial_bic_ordered.csv")
        in_csv = open(in_file, 'r', newline='', encoding="utf-8")
        csv_reader = csv.DictReader(in_csv, delimiter=',')
        for row in csv_reader:
            size = row["bic_file_size"]
            key = row["bic_hash"] + "$$" + row["bic_path"]
            if size.isdigit():
                size_int = int(size)
                defective = 1 if row["defective"] == "TRUE" else 0
                if key not in bics:
                    bics[key] = Bic(key)
                bics[key].defective = defective
                bics[key].size = size_int
                total_size += size_int
                total_bugs += defective

    header = ["eff", "def"]
    out_file = os.path.abspath(working_path + "effort.csv")
    out_csv = open(out_file, 'w', newline='', encoding="utf-8")
    writer = csv.DictWriter(out_csv, delimiter=',', fieldnames=header)
    writer.writeheader()
    line_inspected = 0
    bug_found = 0
    for key in bics:
        bic = bics[key]
        line_inspected += bic.size
        bug_found += bic.defective
        perc_eff = line_inspected * 100 / total_size
        perc_def = bug_found * 100 / total_bugs
        d = {"def": perc_def, "eff": perc_eff}
        writer.writerow(d)
        out_csv.flush()
    out_csv.close()


if __name__ == '__main__':
    print("*** Effort started ***\n")
    effort()
    print("*** Effort ended ***\n")
