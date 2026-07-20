import streamlit as st

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Streamlit Example App")

st.sidebar.title("Settings")
st.sidebar.markdown("Please enter your username")
username = st.sidebar.text_input("Enter Username", value="Admin")
role = st.sidebar.selectbox("Role", ["Student", "Instructor", "Admin"])

st.title(f"Welcome, {username}! ({role})")

st.divider()

st.header("Scene Object Manager")

if "scene_objects" not in st.session_state:
    st.session_state.scene_objects = []
if "next_id" not in st.session_state:
    st.session_state.next_id = 1

st.header("Add a new object")
name = st.text_input("Name")
x = st.number_input("X", value=0.0)
y = st.number_input("Y", value=0.0)
z = st.number_input("Z", value=0.0)

if st.button("Add Object"):
    if not name:
        st.warning("Name is required.")
    else:
        st.session_state.scene_objects.append({
            "id": st.session_state.next_id,
            "name": name,
            "position": [x, y, z],
        })
        st.session_state.next_id += 1

st.header("Current objects")
search = st.text_input("Filter by name")

if not st.session_state.scene_objects:
    st.info("No objects yet.")
for obj in st.session_state.scene_objects:
    if search and search.lower() not in obj['name'].lower():
        continue
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(f"**#{obj['id']} {obj['name']}** — position {obj['position']}")
    with col2:
        if st.button("Delete", key=f"delete_{obj['id']}"):
            st.session_state.scene_objects = [
                o for o in st.session_state.scene_objects if o["id"] != obj["id"]
            ]
            st.rerun()

left_obj_col, right_obj_col = st.columns([3, 1])
with left_obj_col:
    st.metric("Total objects", len(st.session_state.scene_objects))
with right_obj_col:
    if st.button("Clear All Objects"):
        st.session_state.scene_objects = []
        st.rerun()

st.divider()

st.header("Streamlit Chatbot Example")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Type your message..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    reply = f"Echo: {user_input}"          # Later: replace with a real LLM call
    with st.chat_message("assistant"):
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})

st.divider()

st.header("Streamlit File Uploader Example")
uploaded_file = st.file_uploader("Upload file", type=["pdf", "txt"])

if uploaded_file:                       # None until the user uploads
    st.success("File uploaded!")
    st.write(f"The file name is: {uploaded_file.name}")

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        st.pdf(uploaded_file)
    elif uploaded_file.type == "text/plain":
        text = uploaded_file.read().decode("utf-8")
        st.write("File content:")
        st.text_area("File Content", text, height=300)

st.divider()

st.header("Streamlit Messages Example")
st.markdown("*Italics Messages*")

st.success("This is a success message")
st.error("This is an error message")
st.info("This is an info message")
st.warning("This is a warning message")