import streamlit as st
import pandas as pd
import zipfile
import os
import tempfile
from io import BytesIO

st.set_page_config(page_title="Logo Mapping Tool", layout="wide")

st.title("Logo Placement Mapping Tool")
st.write("Upload a ZIP folder of JPG/PSD files. The app will create an Excel spreadsheet based on folder names and file names.")

uploaded_zip = st.file_uploader("Upload ZIP file", type=["zip"])

if uploaded_zip:
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "uploaded.zip")

        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.read())

        extract_path = os.path.join(temp_dir, "extracted")

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        rows = []

        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.lower().endswith((".jpg", ".jpeg", ".png", ".psd")):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, extract_path)

                    folder_name = os.path.basename(root)
                    file_name = os.path.splitext(file)[0]
                    file_type = os.path.splitext(file)[1].replace(".", "").upper()

                    rows.append({
                        "Category / Folder": folder_name,
                        "File Name": file_name,
                        "File Type": file_type,
                        "Full Path": relative_path,
                        "Logo Placement": folder_name,
                        "Status": "Mapped"
                    })

        if rows:
            df = pd.DataFrame(rows)

            st.subheader("Preview Data")
            st.dataframe(df, use_container_width=True)

            output = BytesIO()

            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Logo Mapping")

            output.seek(0)

            st.download_button(
                label="Download Completed Excel File",
                data=output,
                file_name="logo_mapping_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No image or PSD files found in the uploaded ZIP.")
