import streamlit as st
from utils.storage import JOBS_FILE, load_jobs
print('路徑:', JOBS_FILE)
print('筆數:', len(load_jobs()))
st.write('路徑:', str(JOBS_FILE))
st.write('筆數:', len(load_jobs()))
