from fastapi import FastAPI
import uvicorn
import pickle

app = FastAPI(debug=True)

@app.get('/')
def home():
    return {'text': 'PCOS Diagnosing Tool'}

@app.get('/predict')
def predict(CycleRI: str, FSHmIUmL: str, LHmIUmL: str, 
            AMHngmL: str, PulseRateBPM: str, PRGngmL: str, RBSmgdl: str, 
            BP_SystolicmmHg: str, BP_DiastolicmmHg: str, AvgFsizeLmm: str, AvgFsizeRmm: str, 
            Endometriummm: str, Age: str, Hairgrowth: str, SkinDarkening: str):
    
    model = pickle.load(open('C:/Users/krisJ/Desktop/FastAPI Deploy/model-svm.pkl', 'rb'))
    makeprediction = model.predict([[CycleRI, FSHmIUmL, LHmIUmL, 
            AMHngmL, PulseRateBPM, PRGngmL, RBSmgdl, 
            BP_SystolicmmHg, BP_DiastolicmmHg, AvgFsizeLmm, AvgFsizeRmm, 
            Endometriummm, Age, Hairgrowth, SkinDarkening]])

    output = round(makeprediction[0],2)

    return {'You have {}'.format(output)}

if __name__ == '__main__':
    uvicorn.run(app)