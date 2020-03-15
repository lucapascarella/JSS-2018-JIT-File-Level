import csv
import os

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

working_path = "../projects/"
project = "angular.js"


def training():
    dataset = pd.read_csv(working_path + project + "_metrics.csv")
    X = dataset.iloc[:, 6:30].values
    y = dataset.iloc[:, 31].values
    offset = 10000
    X_proba = dataset.iloc[-offset:, 6:30].values
    y_proba = dataset.iloc[-offset:, 31].values

    X_train, X_test, y_train, y_test = train_test_split(X, y)
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)

    model = RandomForestClassifier()
    rf_model = model.fit(X_train, y_train)
    rf_model.score(X_train, y_train)

    # Get classification
    y_pred_proba = model.predict(sc.fit_transform(X_proba))
    print(confusion_matrix(y_proba, y_pred_proba.round()))
    print(classification_report(y_proba, y_pred_proba.round()))

    in_file = os.path.abspath(working_path + project + "_metrics.csv")
    in_csv = open(in_file, 'r', newline='', encoding="utf-8")
    csv_reader = csv.DictReader(in_csv, delimiter=',')
    rows = []
    for row in csv_reader:
        rows.append(row)

    header = ["bic_hash", "bic_path", "defective"]
    out_file = os.path.abspath(working_path + project + "_pred.csv")
    out_csv = open(out_file, 'w', newline='', encoding="utf-8")
    writer = csv.DictWriter(out_csv, delimiter=',', fieldnames=header)
    writer.writeheader()
    for i in range(0, len(y_pred_proba)):
        row = rows[len(rows) - offset + i]
        # print("Hash: {} Test: {} Pred {}".format(row["key"], y_proba[i], y_pred_proba[i]))
        d = {"bic_hash": row["git_hash"], "bic_path": row["path"], "defective": y_pred_proba[i]}
        writer.writerow(d)

    # Predictions/probs on the test dataset
    predicted = pd.DataFrame(rf_model.predict(X_test))
    probs = pd.DataFrame(rf_model.predict_proba(X_test))

    # Store metrics
    rf_roc_auc = metrics.roc_auc_score(y_test, probs[1])
    print("AUC-ROC: {:>7}%".format(round(rf_roc_auc * 100, 1)))

    y_pred = model.predict(X_test)
    # for i in range(0, len(y_test)):
    #    print("Test: {} Pred {}".format(y_test[i], y_pred[i]))
    print(confusion_matrix(y_test, y_pred.round()))
    print(classification_report(y_test, y_pred.round()))
    print(accuracy_score(y_test, y_pred.round()))


if __name__ == '__main__':
    print("*** Classifier started ***\n")
    training()
    print("*** Classifier ended ***\n")
