from flask import Flask, request, jsonify, redirect, url_for, render_template, session
import pickle
from openpyxl.workbook import Workbook
from openpyxl import load_workbook
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.secret_key = "hello"

@app.route("/")
def home():
    return render_template("index.html")

app.config["EXCEL_UPLOADS"] = "./static/assets/uploads"
app.config["ALLOWED_EXCEL_EXTENSIONS"] = ["XLSX", "CSV", "XLS"]

def predict_excel(excel):
    wb = load_workbook(excel)

    ws = wb.active

    PatID = ws["A2"].value
    Age = ws["B2"].value
    Hairgrowth = ws["I2"].value
    SkinDarkening = ws["J2"].value
    PulseRateBPM = ws["Q2"].value
    CycleRI = ws["T2"].value
    FSHmIUmL = ws["AA2"].value
    LHmIUmL = ws["AB2"].value
    AMHngmL = ws["AE2"].value
    PRGngmL = ws["AH2"].value
    RBSmgdl = ws["AI2"].value
    BP_SystolicmmHg = ws["AJ2"].value
    BP_DiastolicmmHg = ws["AK2"].value
    AvgFsizeLmm = ws["AN2"].value
    AvgFsizeRmm = ws["AO2"].value
    Endometriummm = ws["AP2"].value

    session["PatID"] = PatID
    session["Age"] = Age
    session["Hairgrowth"] = Hairgrowth
    session["CycleRI"] = CycleRI
    session["AvgFsizeLmm"] = AvgFsizeLmm
    session["AvgFsizeRmm"] = AvgFsizeRmm

    radio = request.form['radio']
    if radio == "SVM":
        model = pickle.load(open('models\svm-model.pkl', 'rb'))
        session['model'] = "SVM"
    elif radio == "DT":
        model = pickle.load(open('models\dt-model.pkl', 'rb'))
        session['model'] = "DT"
    else:
        redirect(url_for("tool"))

    makeprediction = model.predict([[Age, Hairgrowth, SkinDarkening,
                                    PulseRateBPM, CycleRI, FSHmIUmL, LHmIUmL,
                                    AMHngmL, PRGngmL, RBSmgdl, BP_SystolicmmHg,
                                    BP_DiastolicmmHg, AvgFsizeLmm, AvgFsizeRmm, Endometriummm]])

    output = round(makeprediction[0], 2)

    return(output)

def allowed_excel(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_EXCEL_EXTENSIONS"]:
        return True
    else:
        return False

@app.route("/tool", methods=["GET", "POST"])
def tool():
    session.pop("result", None)
    session.pop("model", None)
    if request.method == "POST":
        if request.files:
            excel = request.files["input"]

            if excel.filename == "":
                print("Excel file must have a filename")
                return redirect(request.url)

            if not allowed_excel(excel.filename):
                print("That excel extension is not allowed")
                return redirect(request.url)

            else:
                filename = secure_filename(excel.filename)

                excel.save(os.path.join(app.config["EXCEL_UPLOADS"], filename))

            output = predict_excel(excel)
            print(output)
            session['result'] = int(output)
            
            return redirect(url_for("result"))
    else:    
        if "result" in session:
            return redirect(url_for("pop"))
    return render_template("tool.html")


@app.route("/result", methods=["GET", "POST"])
def result():
    if "result" in session:
        result = session["result"]
        model = session["model"]
        PatID = session["PatID"]
        Age = session["Age"]
        Hairgrowth = session["Hairgrowth"]
        CycleRI = session["CycleRI"]
        AvgFsizeLmm = session["AvgFsizeLmm"]
        AvgFsizeRmm = session["AvgFsizeRmm"]
        if model == "SVM":
            model_name = "SVM"
        else:
            model_name = "DT"

        if result == 1:
            return render_template("results.html", RESULTS="POSITIVE", MODEL=model_name, ID=PatID, AGE=Age, HAIR=Hairgrowth, CYC=CycleRI, AFL=AvgFsizeLmm, AFR=AvgFsizeRmm)
        else:
            return render_template("results.html", RESULTS="NEGATIVE", MODEL=model_name, ID=PatID, AGE=Age, HAIR=Hairgrowth, CYC=CycleRI, AFL=AvgFsizeLmm, AFR=AvgFsizeRmm)
    else:
        return redirect(url_for("tool"))

@app.route("/pop")
def pop():
    session.pop("result", None)
    session.pop("model", None)
    return redirect(url_for("tool"))

if __name__ == "__main__":
    app.run(debug=True)
