import pickle
import streamlit as st

model = pickle.load(open('C:/Users/krisJ/Desktop/FastAPI Deploy/model-svm.pkl', 'rb'))

def main():
    st.title('PCOS Diagnosing Tool')

    #input variables
    CycleRI = st.text_input('Cycle(R/I)')
    FSHmIUmL = st.text_input('FSH(mIU/mL)')
    LHmIUmL = st.text_input('LH(mIU/mL)')
    AMHngmL = st.text_input('AMH(ng/mL)')
    PulseRateBPM = st.text_input('Pulse rate(bpm)')
    PRGngmL = st.text_input('PRG(ng/mL)')
    RBSmgdl = st.text_input('RBS(mg/dl)')
    BP_SystolicmmHg = st.text_input('BP _Systolic (mmHg)')
    BP_DiastolicmmHg = st.text_input('BP _Diastolic (mmHg)')
    AvgFsizeLmm = st.text_input('Avg. F size (L) (mm)')
    AvgFsizeRmm = st.text_input('Avg. F size (R) (mm)')
    Endometriummm = st.text_input('Endometrium (mm)')
    Age = st.text_input('Age (yrs)')
    Hairgrowth = st.text_input('hair growth(Y/N)')
    SkinDarkening = st.text_input('Skin darkening (Y/N)')

    #prediction code
    if st.button('Predict'):
        makeprediction = model.predict([[CycleRI, FSHmIUmL, LHmIUmL, 
            AMHngmL, PulseRateBPM, PRGngmL, RBSmgdl, 
            BP_SystolicmmHg, BP_DiastolicmmHg, AvgFsizeLmm, AvgFsizeRmm, 
            Endometriummm, Age, Hairgrowth, SkinDarkening]])

        output = round(makeprediction[0],2)
        if output == 1.0:
            st.success('You have PCOS')
        else:
            st.success('You have no PCOS')
    
if __name__=='__main__':
        main()