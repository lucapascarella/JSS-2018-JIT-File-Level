import csv

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

working_path = "../projects/"
project = "accumulo"


def training():
    # Select partially defective only
    bic_csv = working_path + project + "_partial_bic.csv"
    in_file = open(bic_csv, 'r', newline='', encoding="utf-8")
    reader = csv.DictReader(in_file, delimiter=',')
    bics = {}
    for row in reader:
        if row["bic_hash"] in bics:
            bics[row["bic_hash"]].append(row["defective"])
        else:
            bics[row["bic_hash"]] = [row["defective"]]
    def_full = []
    def_part = []
    for key, value in bics.items():
        count_defective_files = value.count("True")
        if len(value) == count_defective_files or count_defective_files == 1:
            def_full.append(key)
        else:
            def_part.append(key)
    in_file.close()

    # Save only partial
    in_file = open(working_path + project + "_metrics.csv", 'r', newline='', encoding="utf-8")
    out_file = open(working_path + project + "_metrics_part.csv", 'w', newline='', encoding="utf-8")
    out_file.write("key,git_hash,file_name,path,package,mod_type,COMM,ADEV,DDEV,ADD,DEL,OWN,MINOR,SCTR,NADEV,NDDEV,NCOMM,NSCTR,OEXP,EXP,ND,Entropy,LA,LD,LT,AGE,NUC,CEXP,REXP,SEXP,file_buggy,file_fix\n")
    def_set = set(def_part)
    for row in in_file.readlines():
        commit  = row.split(',')[1]
        if commit in def_set:
            out_file.write(row)
    in_file.close()
    out_file.close()

    ## Train
    dataset = pd.read_csv(working_path + project + "_metrics_part.csv")
    X = dataset.iloc[:, 6:30].values
    y = dataset.iloc[:, 31].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)

    model = RandomForestClassifier()
    rf_model = model.fit(X_train, y_train)
    rf_model.score(X_train, y_train)

    # Predictions/probs on the test dataset
    predicted = pd.DataFrame(rf_model.predict(X_test))
    probs = pd.DataFrame(rf_model.predict_proba(X_test))

    # Store metrics
    rf_roc_auc = metrics.roc_auc_score(y_test, probs[1])

    print("AUC-ROC: {:>7}%".format(round(rf_roc_auc * 100, 1)))

    y_pred = model.predict(X_test)
    print(confusion_matrix(y_test, y_pred.round()))
    print(classification_report(y_test, y_pred.round()))
    print(accuracy_score(y_test, y_pred.round()))


if __name__ == '__main__':
    print("*** Classifier started ***\n")
    training()
    print("*** Classifier ended ***\n")
