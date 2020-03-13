import os

working_path = "projects/"
projects = ["accumulo", "angular.js", "bugzilla", "gerrit", "gimp", "hadoop", "JDeodorant", "jetty.project", "jruby", "openjpa"]


def merge():
    # Flush header
    in_file_path = os.path.abspath(working_path + projects[0] + "_metrics.csv")
    in_file = open(in_file_path, 'r', newline='', encoding="utf-8")
    header = in_file.read()
    out_file = open(os.path.abspath(working_path + "all_metrics.csv"), 'w')
    out_file.write(header)
    in_file.close()

    for project in projects:
        first_line = False
        in_file_path = os.path.abspath(working_path + project + "_metrics.csv")
        in_file = open(in_file_path, 'r', newline='', encoding="utf-8")
        for line in in_file.readlines():
            if not first_line:
                first_line = True
            else:
                out_file.write(line)
        in_file.close()
    out_file.close()


if __name__ == '__main__':
    print("*** Merge started ***\n")
    merge()
    print("*** Merge ended ***\n")
