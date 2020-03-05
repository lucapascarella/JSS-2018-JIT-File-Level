import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from xgboost import XGBClassifier

working_path = "../projects/"
project = "hadoop"


def training():
    dataset = pd.read_csv(working_path + project + "_metrics.csv")
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
    rf_accuracy = metrics.accuracy_score(y_test, predicted)
    rf_roc_auc = metrics.roc_auc_score(y_test, probs[1])
    rf_confus_matrix = metrics.confusion_matrix(y_test, predicted)
    rf_classification_report = metrics.classification_report(y_test, predicted)
    rf_precision = metrics.precision_score(y_test, predicted, pos_label=1)
    rf_recall = metrics.recall_score(y_test, predicted, pos_label=1)
    rf_f1 = metrics.f1_score(y_test, predicted, pos_label=1)

    print("Precision: {:>5}%".format(round(rf_precision * 100, 1)))
    print("Recall: {:>8}%".format(round(rf_recall * 100, 1)))
    print("F-1: {:>11}%".format(round(rf_f1 * 100, 1)))
    print("AUC-ROC: {:>7}%".format(round(rf_roc_auc * 100, 1)))

    y_pred = model.predict(X_test)
    print(confusion_matrix(y_test, y_pred.round()))
    print(classification_report(y_test, y_pred.round()))
    print(accuracy_score(y_test, y_pred.round()))

if __name__ == '__main__':
    print("*** Classifier started ***\n")
    training()
    print("*** Classifier ended ***\n")
