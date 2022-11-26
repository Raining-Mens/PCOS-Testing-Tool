from flask import Flask, request, jsonify, redirect, url_for, render_template, session
import pickle
from openpyxl.workbook import Workbook
from openpyxl import load_workbook
from werkzeug.utils import secure_filename
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from sklearn.ensemble import ExtraTreesClassifier
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score

app = Flask(__name__)

app.secret_key = "hello"

app.config["EXCEL_UPLOADS"] = "./static/assets/uploads"
app.config["ALLOWED_EXCEL_EXTENSIONS"] = ["XLSX", "CSV", "XLS"]



def allowed_excel(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_EXCEL_EXTENSIONS"]:
        return True
    else:
        return False

def data_import(model_fin):
    file_path_with_infertility="static/assets/PCOS_infertility.csv"
    file_path_without_infertility="static/assets/PCOS_data_without_infertility.xlsx"

    PCOS_inf = pd.read_csv(file_path_with_infertility)
    PCOS_woinf = pd.read_excel(file_path_without_infertility, sheet_name="Full_new")

    data = pd.merge(PCOS_woinf,PCOS_inf, on='Patient File No.', suffixes={'','_y'},how='left')

    #Dropping the repeated features after merging
    data =data.drop(['Unnamed: 44', 'Sl. No_y', 'PCOS (Y/N)_y', '  I   beta-HCG(mIU/mL)_y',
        'II    beta-HCG(mIU/mL)_y', 'AMH(ng/mL)_y'], axis=1)

    # data = pd.read_excel(path, sheet_name="Sheet1")
    data["AMH(ng/mL)"] = pd.to_numeric(data["AMH(ng/mL)"], errors='coerce')
    data["II    beta-HCG(mIU/mL)"] = pd.to_numeric(data["II    beta-HCG(mIU/mL)"], errors='coerce')

    data['Marraige Status (Yrs)'].fillna(data['Marraige Status (Yrs)'].median(),inplace=True)
    data['II    beta-HCG(mIU/mL)'].fillna(data['II    beta-HCG(mIU/mL)'].median(),inplace=True)
    data['AMH(ng/mL)'].fillna(data['AMH(ng/mL)'].median(),inplace=True)
    data['Fast food (Y/N)'].fillna(data['Fast food (Y/N)'].median(),inplace=True)

    data.columns = [col.strip() for col in data.columns]

    data = data[(data["BP _Diastolic (mmHg)"]>20)]
    data = data[(data["AMH(ng/mL)"]<40)]
    data = data[(data["BP _Systolic (mmHg)"]>20)]
    data = data[(data["Endometrium (mm)"]>0)]
    data = data[(data["Avg. F size (L) (mm)"]>0)]
    data = data[(data["Avg. F size (R) (mm)"]>0)]
    data = data[(data["RBS(mg/dl)"]<200)]
    data = data[(data["PRG(ng/mL)"]<20)]
    data = data[(data["Pulse rate(bpm)"]>20)]
    data = data[(data["FSH(mIU/mL)"]<4000)]
    data = data[(data["LH(mIU/mL)"]<1500)]
    data = data[(data["Cycle(R/I)"]<4.5)]

    print(data.shape)

    X=data.drop(["PCOS (Y/N)","Sl. No","Patient File No."],axis = 1) #droping out index from features too
    y=data["PCOS (Y/N)"]
    # print(X.shape)
    # print(y.shape)
    
    modelfeat = ExtraTreesClassifier()
    modelfeat.fit(X,y)

    modelfeat.feature_importances_
    feat_importances = pd.Series(modelfeat.feature_importances_, index=X.columns)

    fimp = feat_importances.nlargest(15)
    df_again = data[fimp.index]

    X_train,X_test, y_train, y_test = train_test_split(df_again,y, test_size=0.2, random_state=42)
    y_train = np.array(y_train)
    y_test = np.array(y_test)

    pred_rfc = model_fin.predict(X_test)
    accuracy = accuracy_score(y_test, pred_rfc)
    print('Training set score: {:.4f}'.format(model_fin.score(X_train, y_train)))
    print('Test set score: {:.4f}'.format(model_fin.score(X_test, y_test)))
    session["accuracy"] = accuracy

    classi_report = classification_report(y_test, pred_rfc)
    session["classi_report"] = classi_report

    try:
        # cofusion matrix
        plt.subplots(figsize=(15,5))
        cf_matrix = confusion_matrix(y_test, pred_rfc)
        sns.heatmap(cf_matrix/np.sum(cf_matrix), annot = True, annot_kws = {'size':15}, cmap = 'Pastel1')
        cf_matrix.savefig('/static/assets/new_plot.png')
        sns.savefig('/static/assets/new_plot.png')
        plt.savefig('/static/assets/new_plot.png')
    except:
        print("error in cfm")
    else:
        print("cf matrix saved")



@app.route("/", methods=["GET", "POST"])
def tool():
    session.pop("accuracy", None)
    session.pop("classi_report", None)
    if request.method == "POST":

        radio = request.form['radio']
        if radio == "SVM":
            model_fin = pickle.load(open('models\without-svm-model.pkl', 'rb'))
            # try:
            data_import(model_fin)
                # print("imported excel and model")
            # except:
                # print("Error in importing")
            # else:
            #     print("Model selected and good in importing")
            print("Moving to Results")
            return redirect(url_for("result"))
        elif radio == "DT":
            model_fin = pickle.load(open('models\dt-model.pkl', 'rb'))
            data_import(model_fin)
            return redirect(url_for("result"))
        else:
            redirect(url_for("tool"))
            print("Error in Tool")
            
    return render_template("tool.html")


@app.route("/result", methods=["GET", "POST"])
def result():
    # if request.method == "POST":
    accuracy = session["accuracy"]
    classi_report = session["classi_report"]

    return render_template("results.html", ACC=accuracy, REP=classi_report)
    # else:
    #     print("Requesting Error")
    #     return redirect(url_for("tool"))
# @app.route("/pop")
# def pop():
#     session.pop("result", None)
#     session.pop("model", None)
#     return redirect(url_for("tool"))

if __name__ == "__main__":
    app.run(debug=True)
