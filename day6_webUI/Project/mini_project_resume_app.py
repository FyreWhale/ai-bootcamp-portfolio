import streamlit as st

st.sidebar.title("Your Info")
name = st.sidebar.text_input("Name", "John Doe")

st.title("Simple Resume App")

if "upload_count" not in st.session_state:
    st.session_state.upload_count = 0
if "last_file_id" not in st.session_state:
    st.session_state.last_file_id = None

resume = st.file_uploader("Upload your resume", type=["pdf", "txt"])
if resume:
    if resume.file_id != st.session_state.last_file_id:
        st.session_state.upload_count += 1
        st.session_state.last_file_id = resume.file_id
    st.success(f"Hello {name}, we received: {resume.name}")

    st.write("File content:")
    if resume.type == "application/pdf":
        st.pdf(resume)
    elif resume.type == "text/plain":
        text = resume.read().decode("utf-8")
        st.text_area("File Content", text, height=300)

st.metric("Times uploaded this session", st.session_state.upload_count)