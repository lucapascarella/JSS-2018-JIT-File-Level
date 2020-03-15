import csv
import os

working_path = "../projects/"
project = "accumulo"


# projects = ["accumulo", "angular.js", "bugzilla", "gerrit", "gimp", "hadoop", "JDeodorant", "jetty.project", "jruby", "openjpa"]

class Bic:
    def __init__(self, hash: str):
        self.hash = hash
        self.defective = 0
        self.size = 0


def effort_optimal(input: str):
    total_size = 0
    total_bugs = 0
    bics = {}
    # for project in projects:
    in_file = os.path.abspath(working_path + project + input)
    in_csv = open(in_file, 'r', newline='', encoding="utf-8")
    csv_reader = csv.DictReader(in_csv, delimiter=',')
    for row in csv_reader:
        size = row["bic_file_size"]
        key = row["bic_hash"] + "$$" + row["bic_path"]
        if size is not "":
            size_int = int(size)
            defective = 1 if row["defective"].upper() == "TRUE" else 0
            if key not in bics:
                bics[key] = Bic(key)
            bics[key].defective = defective
            bics[key].size = size_int
            total_size += size_int
            total_bugs += defective

    header = ["eff", "def"]
    out_file = os.path.abspath(working_path + project + "_effort.csv")
    out_csv = open(out_file, 'w', newline='', encoding="utf-8")
    writer = csv.DictWriter(out_csv, delimiter=',', fieldnames=header)
    writer.writeheader()
    y_val_before = 0
    for i in range(0, 1000):
        x_val = i / 10
        avg = len = 0
        line_inspected = 0
        bug_found = 0
        for key in bics:
            bic = bics[key]
            line_inspected += bic.size
            bug_found += bic.defective
            perc_eff = line_inspected * 100 / total_size
            perc_def = bug_found * 100 / total_bugs
            if round(perc_eff, 1) == x_val:
                len += 1
                avg += perc_def
        if len > 0:
            y_val_before = y_val = avg / len
        else:
            y_val = y_val_before
        d = {"eff": x_val, "def": round(y_val, 1)}
        writer.writerow(d)
        out_csv.flush()
    out_csv.close()


def effort_pred():
    # for project in projects:
    in_file = os.path.abspath(working_path + project + "_partial_bic.csv")
    in_csv = open(in_file, 'r', newline='', encoding="utf-8")
    csv_reader = csv.DictReader(in_csv, delimiter=',')
    rows_ordered = []
    for row in csv_reader:
        rows_ordered.append(row)
    in_csv.close()
    # Read pred
    in_file = os.path.abspath(working_path + project + "_pred.csv")
    in_csv = open(in_file, 'r', newline='', encoding="utf-8")
    csv_reader = csv.DictReader(in_csv, delimiter=',')

    header = ["bic_hash", "bic_size", "bic_file_size", "bic_path", "defective"]
    out_file = os.path.abspath(working_path + project + "_partial_predict_bic.csv")
    out_csv = open(out_file, 'w', newline='', encoding="utf-8")
    writer = csv.DictWriter(out_csv, delimiter=',', fieldnames=header)
    writer.writeheader()

    for row in csv_reader:
        for r_o in rows_ordered:
            if row["bic_hash"].upper() == r_o["bic_hash"].upper() and row["bic_path"].upper() == r_o["bic_path"].upper():
                writer.writerow({"bic_hash": r_o["bic_hash"], "bic_size": r_o["bic_size"], "bic_file_size": r_o["bic_file_size"], "bic_path": r_o["bic_path"], "defective": row["defective"]})
                out_csv.flush()
    out_csv.close()
    in_csv.close()


if __name__ == '__main__':
    print("*** Effort started ***\n")
    effort_optimal("_partial_bic_ordered.csv")
    #effort_optimal("_partial_predict_bic.csv")
    # effort_pred()
    print("*** Effort ended ***\n")
