import csv
import os
import operator

import numpy

working_path = "../projects/"
projects = ["accumulo", "angular.js", "bugzilla", "gerrit", "gimp", "hadoop", "JDeodorant", "jetty.project", "jruby", "openjpa"]

#rojects = ["accumulo"]


class Bic:
    def __init__(self, hash: str):
        self.hash = hash
        self.defective = 0
        self.size = 0


def effort_optimal(project: str, input: str):
    total_size = 0
    total_bugs = 0
    bics = {}
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

    header = ["eff", "def_optimal"]
    out_file = os.path.abspath(working_path + project + "_effort_optimal.csv")
    out_csv = open(out_file, 'w', newline='', encoding="utf-8")
    writer = csv.DictWriter(out_csv, delimiter=',', fieldnames=header)
    writer.writeheader()
    y_val_before = 0
    for i in range(0, 1000):
        x_val = i / 10
        avg = length = 0
        line_inspected = 0
        bug_found = 0
        for key in bics:
            bic = bics[key]
            line_inspected += bic.size
            bug_found += bic.defective
            perc_eff = line_inspected * 100 / total_size
            perc_def = bug_found * 100 / total_bugs
            if round(perc_eff, 1) == x_val:
                length += 1
                avg += perc_def
        if length > 0:
            y_val_before = y_val = avg / length
        else:
            y_val = y_val_before
        d = {"eff": x_val, "def_optimal": round(y_val, 1)}
        writer.writerow(d)
        out_csv.flush()
    out_csv.close()


def write_data(clm, filename, bics, total_size, total_bugs):
    header = ["eff", clm]
    out_file = os.path.abspath(working_path + project + filename)
    out_csv = open(out_file, 'w', newline='', encoding="utf-8")
    writer = csv.DictWriter(out_csv, delimiter=',', fieldnames=header)
    writer.writeheader()
    y_val_before = 0
    for i in range(0, 1000):
        x_val = i / 10
        avg = length = 0
        line_inspected = 0
        bug_found = 0
        for key in bics:
            bic = bics[key]
            line_inspected += bic.size
            bug_found += bic.defective
            perc_eff = line_inspected * 100 / total_size
            perc_def = bug_found * 100 / total_bugs
            if round(perc_eff, 1) == x_val:
                length += 1
                avg += perc_def
        if length > 0:
            y_val_before = y_val = avg / length
        else:
            y_val = y_val_before
        d = {"eff": x_val, clm: round(y_val, 1)}
        writer.writerow(d)
        out_csv.flush()
    out_csv.close()


def effort_pred(project: str, input: str):
    # Read prediction
    in_file = os.path.abspath(working_path + project + "_pred.csv")
    in_csv = open(in_file, 'r', newline='', encoding="utf-8")
    csv_reader = csv.DictReader(in_csv, delimiter=',')
    prediction = {}
    for row in csv_reader:
        bic_hash = row["bic_hash"]
        if bic_hash not in prediction:
            prediction[bic_hash] = []
        actual = 1 if row["actual"].upper() == "TRUE" else 0
        defective = 1 if row["defective"].upper() == "TRUE" else 0
        prob = float(row["prob"])
        prediction[bic_hash].append((row["bic_path"], actual, defective, prob))
    in_csv.close()

    # Read partial BIC order and flush prediction in a new file
    in_file = os.path.abspath(working_path + project + "_partial_bic.csv")
    in_csv = open(in_file, 'r', newline='', encoding="utf-8")
    csv_reader = csv.DictReader(in_csv, delimiter=',')

    # Add missing column and save partial_bic order (by commit data)
    pred_bics = {}
    for row in csv_reader:
        bic_hash = row["bic_hash"]
        bic_path = row["bic_path"]
        key = bic_hash + "$$" + bic_path
        pred_files = prediction.get(bic_hash, [])
        for pred_file in pred_files:
            pred_bic_path = pred_file[0]
            actual = pred_file[1]
            defective = pred_file[2]
            prob = pred_file[3]
            if bic_path == pred_bic_path:
                pred_bics[key] = {"bic_hash": bic_hash, "bic_size": row["bic_size"], "bic_file_size": row["bic_file_size"], "bic_path": row["bic_path"], "actual": actual, "defective": defective, "prob": prob}
        if key not in pred_bics:
            pred_bics[key] = {"bic_hash": bic_hash, "bic_size": row["bic_size"], "bic_file_size": row["bic_file_size"], "bic_path": row["bic_path"], "actual": 0, "defective": -1, "prob": 0}

    # Defective is 1 => bug, 0 => no-bug, -1 => no part of prediction but part of the commit

    header = ["bic_hash", "bic_size", "bic_file_size", "bic_path", "actual", "defective", "prob"]
    out_file = os.path.abspath(working_path + project + input)
    out_csv = open(out_file, 'w', newline='', encoding="utf-8")
    writer = csv.DictWriter(out_csv, delimiter=',', fieldnames=header)
    writer.writeheader()
    for key in pred_bics:
        d = pred_bics[key]
        writer.writerow({"bic_hash": d["bic_hash"], "bic_size": d["bic_size"], "bic_file_size": d["bic_file_size"], "bic_path": d["bic_path"], "actual": d["actual"], "defective": d["defective"], "prob": d["prob"]})
        out_csv.flush()
    out_csv.close()
    in_csv.close()

    # Calculate cost-effectiveness for our model
    total_size = 0
    total_bugs = 0
    cost_eff = []
    in_file = os.path.abspath(working_path + project + input)
    in_csv = open(in_file, 'r', newline='', encoding="utf-8")
    csv_reader = csv.DictReader(in_csv, delimiter=',')
    s = sorted(csv_reader, key=operator.itemgetter("bic_file_size"))
    s.sort(key=operator.itemgetter("prob"), reverse=True)
    for row in s:
        size = row["bic_file_size"]
        if size is not "":
            size_int = int(size)
            actual = int(row["actual"])
            defective = int(row["defective"])
            if defective >= 0:
                total_size += size_int
                total_bugs += actual
                cost_eff.append((total_size, total_bugs))
    # Transform cost-effectiveness in percentage
    cost_eff_perc = []
    for i in range(0, len(cost_eff)):
        line_inspected = cost_eff[i][0]
        bug_found = cost_eff[i][1]
        perc_eff = line_inspected * 100 / total_size
        perc_def = bug_found * 100 / total_bugs
        cost_eff_perc.append((perc_eff, perc_def))

    # Save results in a CSV
    header = ["eff", "our"]
    out_file = os.path.abspath(working_path + project + "_effort_our.csv")
    out_csv = open(out_file, 'w', newline='', encoding="utf-8")
    writer = csv.DictWriter(out_csv, delimiter=',', fieldnames=header)
    writer.writeheader()
    # Discretize in 1000 steps only
    y_val_before = 0
    for x_val in numpy.arange(0, 100, 0.1):
        len_def = avg_def = 0
        for eff in cost_eff_perc:
            perc_eff = eff[0]
            perc_def = eff[1]
            if x_val <= perc_eff < x_val + 0.1:
                len_def += 1
                avg_def += perc_def
        if len_def > 0:
            y_val_before = y_val = avg_def / len_def
        else:
            y_val = y_val_before
        d = {"eff": x_val, "our": round(y_val, 1)}
        writer.writerow(d)
        out_csv.flush()
    out_csv.close()

    # write_data("def_our", "_effort_our.csv", bics, total_size, total_bugs)

    # Calculate cost-effectiveness for our Kamei
    total_size = 0
    total_bugs = 0
    cost_eff = []
    in_file = os.path.abspath(working_path + project + input)
    in_csv = open(in_file, 'r', newline='', encoding="utf-8")
    csv_reader = csv.DictReader(in_csv, delimiter=',')
    sort = sorted(csv_reader, key=operator.itemgetter("bic_hash", "prob"))
    for row in sort:
        size = row["bic_file_size"]
        if size is not "":
            size_int = int(size)
            actual = int(row["actual"])
            defective = int(row["defective"])
            if defective >= 0:
                total_size += size_int
                total_bugs += actual
                cost_eff.append((total_size, total_bugs))
    # Transform cost-effectiveness in percentage
    cost_eff_perc = []
    for i in range(0, len(cost_eff)):
        line_inspected = cost_eff[i][0]
        bug_found = cost_eff[i][1]
        perc_eff = line_inspected * 100 / total_size
        perc_def = bug_found * 100 / total_bugs
        cost_eff_perc.append((perc_eff, perc_def))

    # Save results in a CSV
    header = ["eff", "kamei"]
    out_file = os.path.abspath(working_path + project + "_effort_kamei.csv")
    out_csv = open(out_file, 'w', newline='', encoding="utf-8")
    writer = csv.DictWriter(out_csv, delimiter=',', fieldnames=header)
    writer.writeheader()
    # Discretize in 1000 steps only
    y_val_before = 0
    for x_val in numpy.arange(0, 100, 0.1):
        len_def = avg_def = 0
        for eff in cost_eff_perc:
            perc_eff = eff[0]
            perc_def = eff[1]
            if x_val <= perc_eff < x_val + 0.1:
                len_def += 1
                avg_def += perc_def
        if len_def > 0:
            y_val_before = y_val = avg_def / len_def
        else:
            y_val = y_val_before
        d = {"eff": x_val, "kamei": round(y_val, 1)}
        writer.writerow(d)
        out_csv.flush()
    out_csv.close()


if __name__ == '__main__':
    print("*** Effort started ***\n")
    for project in projects:
        print("Project: {}".format(project))
        effort_optimal(project, "_partial_bic_ordered.csv")
        effort_pred(project, "_partial_predict_bic.csv")
    print("*** Effort ended ***\n")
