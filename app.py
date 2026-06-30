import streamlit as st
import tempfile
import hashlib
import os
from pathlib import Path
from datetime import datetime

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="JSON Upload Center",
    page_icon="📂",
    layout="wide"
)

# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>

.stApp{
background:#f5f7fb;
}

.main-title{
font-size:42px;
font-weight:700;
text-align:center;
color:#1e3a8a;
margin-bottom:0px;
}

.sub{
text-align:center;
color:gray;
margin-bottom:30px;
}

.upload-box{

padding:25px;

border-radius:20px;

background:white;

box-shadow:0px 4px 20px rgba(0,0,0,.08);

}

.metric-card{

background:white;

padding:20px;

border-radius:15px;

box-shadow:0px 4px 10px rgba(0,0,0,.08);

}

.footer{

text-align:center;

color:gray;

padding-top:30px;

}

</style>
""", unsafe_allow_html=True)

# -------------------------
# TITLE
# -------------------------

st.markdown(
    "<div class='main-title'>📂 Professional JSON Upload Portal</div>",
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='sub'>Upload JSON / JSONL files up to <b>1 GB</b></div>",
    unsafe_allow_html=True,
)

# -------------------------
# SIDEBAR
# -------------------------

with st.sidebar:

    st.header("⚙ System Information")

    st.success("✔ JSON")

    st.success("✔ JSONL")

    st.info("Maximum Supported Size")

    st.metric("", "1 GB")

    st.divider()

    st.write("### Features")

    st.write("✔ Large File Upload")

    st.write("✔ Secure Upload")

    st.write("✔ Hash Verification")

    st.write("✔ Ready for Processing")

# -------------------------
# UPLOADER
# -------------------------

st.markdown("<div class='upload-box'>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Candidate File",
    type=["json", "jsonl"],
    help="Maximum size : 1 GB"
)

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# PROCESS
# -------------------------

if uploaded_file:

    size_mb = uploaded_file.size / (1024 * 1024)

    size_gb = uploaded_file.size / (1024 * 1024 * 1024)

    # Save file without loading into RAM
    temp_dir = tempfile.gettempdir()

    save_path = os.path.join(temp_dir, uploaded_file.name)

    progress = st.progress(0)

    with open(save_path, "wb") as f:

        chunk_size = 1024 * 1024

        while True:

            chunk = uploaded_file.read(chunk_size)

            if not chunk:
                break

            f.write(chunk)

    progress.progress(100)

    # Hash
    hash_md5 = hashlib.md5()

    with open(save_path, "rb") as f:

        for chunk in iter(lambda: f.read(1024 * 1024), b""):

            hash_md5.update(chunk)

    file_hash = hash_md5.hexdigest()

    st.success("✅ Upload Successful")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("File Name", uploaded_file.name)

    with col2:
        st.metric("Size", f"{size_mb:.2f} MB")

    with col3:
        st.metric("Extension", Path(uploaded_file.name).suffix)

    st.divider()

    st.write("### File Details")

    st.write("**Saved Path**")

    st.code(save_path)

    st.write("**MD5 Hash**")

    st.code(file_hash)

    st.write("**Upload Time**")

    st.info(datetime.now().strftime("%d %B %Y %H:%M:%S"))

    st.divider()

    if st.button("🚀 Continue Processing", use_container_width=True):

        st.success("File is ready for the next processing step.")

# -------------------------
# FOOTER
# -------------------------

st.markdown(
"""
<div class='footer'>
Professional JSON Upload System • Streamlit
</div>
""",
unsafe_allow_html=True)
