import streamlit as st
import pandas as pd
import requests
import oracledb
import getpass
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import PyPDF2
from reportlab.platypus import Table, TableStyle

def generate_pdf(filename, vendor, third_col_value, cost_centre_pdf, internal_pdf, assignment, text, amount):
    # Generate PDF
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Define data for the table
    data = [
        ["Vendor:", vendor],
        ["GL Account No:", third_col_value],
        ["Cost Centre No:", cost_centre_pdf],
        ["Internal Order No:", internal_pdf],
        ["Assignment:", assignment],
        ["Text:", text],
        ["Amount:", amount]
    ]
    
    table = Table(data, colWidths=[150, 250], rowHeights=30)  # Adjust column widths and row heights as needed
    
    # Define style for table
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0))]) 
    

    table.setStyle(style)
    
    # Center the table on the page
    table.wrapOn(c, 0, 0)
    table.drawOn(c, 100, 500)  # Adjust the x, y coordinates to position the table with 10 mm margin from the top
    
    c.save()
    return filename

def generate_pdfx(filename, vendor, third_col_value, cost_centre_pdf, internal_pdf, assignment, text, amount):
    # Generate PDF
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, f"Vendor: {vendor}")
    c.drawString(100, 730, f"GL Account No: {third_col_value}")
    c.drawString(100, 710, f"Cost Centre No: {cost_centre_pdf}")
    c.drawString(100, 690, f"Internal Order No: {internal_pdf}")
    c.drawString(100, 670, f"Assignment: {assignment}")
    c.drawString(100, 650, f"Text: {text}")
    c.drawString(100, 630, f"Amount: {amount}")
    c.save()
    return filename


# Function to read CSV file from GitHub repository
def read_csv_data(df):
    return df

def connection(user, dsn):
    #pw = st.text_input(f"Enter the password for {user}:")
    #wallet_pw = st.text_input("Enter the wallet password for the database:")

    #pw = getpass.getpass(f"Enter the password for {user}:")
    #wallet_pw = getpass.getpass("Enter the wallet password for the database:")

    pw = "Masfinance123"
    wallet_pw = "Masfinance123"

    con = oracledb.connect(user=user, password=pw, dsn=dsn,
                        config_dir = r"Wallet_finance/Wallet_Finance",
                        wallet_location = r"Wallet_finance/Wallet_Finance",
                        wallet_password = wallet_pw)
    
    return con

def table2df(connection, tablename):
    cursor = connection.cursor()

    # Define the SQL query
    sql_query = f"SELECT * FROM {tablename}"

    # Execute the query
    cursor.execute(sql_query)

    # Fetch all rows
    rows = cursor.fetchall()

    # Close cursor and connection
    cursor.close()
    connection.close()

    # Convert the fetched data to a pandas DataFrame
    df = pd.DataFrame(rows)

    return df


def merge_pdfs(pdf_filenames):
    merger = PyPDF2.PdfMerger()
    for filename in pdf_filenames:
        merger.append(filename)
    merged_filename = "merged_document.pdf"
    with open(merged_filename, "wb") as output_pdf:
        merger.write(output_pdf)
    return merged_filename

def main():
    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)
    
    #Resources
    col1, col2 = st.columns([1, 4])

    # Add the image to the first column
    with col1:
        st.image(r"Resources/twinerymas_logo.jpg", width=100)  # Adjust width as needed

    # Add the header text to the second column
    with col2:
        st.markdown("<h1 style='text-align: left;'>Twinery - Innovations 2.0</h1>", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center;'>MAS Finance Department : PDF Merger</h2>", unsafe_allow_html=True)

    user = "ADMIN"
    dsn = "finance_high"

    # Connection Establishment
    con = connection(user, dsn)

    # Converting the Table into Pandas
    df_gl = table2df(con, "GL_LIST")

    # Connection Establishment
    con = connection(user, dsn)
    
    # Converting the Table into Pandas
    df_cost = table2df(con, "COST_CENTRE_LIST")

    vendor = st.text_input('Vendor Name:')
    
    try:
        gl_codes = df_gl.iloc[:, 0].astype(str) + ' : ' + df_gl.iloc[:, 1].astype(str)
        gl_no = st.selectbox('GL Description', gl_codes)
        
        selected_values = gl_no.split(':')
        selected_gl_account1 = selected_values[0].strip()
        selected_gl_account2 = selected_values[1].strip()
        
        # Select the row based on the values in the first and second columns
        row = df_gl[(df_gl.iloc[:, 0] == selected_gl_account1) & (df_gl.iloc[:, 1] == selected_gl_account2)]

        # Rename columns for display
        row_display = row.rename(columns={0: 'SAP B1 - A/C Name', 1: 'G/L Acct Long Text', 2: 'G/L Account'})

        st.write('GL List Table Content:', row_display)
        
        if not row.empty:
            # Get the row number of the selected row
            row_number = row.index[0]  # Assuming there's only one matching row
            
            # Display the value of the third column of the selected row
            third_col_value = df_gl.iloc[row_number, 2]  # Assuming the third column is at index 2
            st.write('GL Account No:', third_col_value)
            
        else:
            st.write('No data found for the selected GL Account.')
            
    except Exception as e:
        st.error(f'Error reading GL Table from Oracle: {e}')

    try: 
        cost_codes = df_cost.iloc[:,1].astype(str)
        cost_no = st.selectbox('Cost Center', cost_codes)

        row_cost = df_cost[(df_cost.iloc[:, 1] == cost_no)]

        # Rename columns for display
        row_display_cost = row_cost.rename(columns={0: 'Cost Center', 1: 'Tier - 3', 2: 'Internal Order'})

        st.write('Cost Centre Table Content:', row_display_cost)

        if not row_display_cost.empty:
            # Get the row number of the selected row
            row_number_cost = row_display_cost.index[0]  # Assuming there's only one matching row
            
            # Display the value of the third column of the selected row
            cost_centre_pdf = df_cost.iloc[row_number_cost, 0]  
            st.write('Cost Centre No:', cost_centre_pdf)

            internal_pdf = df_cost.iloc[row_number_cost, 2] 
            st.write('Internal Order No:', internal_pdf)
            
        else:
            st.write('No data found for the selected Cost Centre.')

    except Exception as f:
        st.error(f'Error reading Cost Centre from Oracle: {f}')


    assignment = st.text_input('Assignment:')
    text = st.text_input('Text:')
    amount = st.text_input('Amount:')
    
    pdf_filename = st.text_input('Enter PDF Filename (without extension):')

    if st.button("Generate PDF"):
        if not pdf_filename:
            st.warning("Please enter a filename for the PDF.")
        else:
            pdf_filename = f"{pdf_filename}.pdf"
            generated_filename = generate_pdf(pdf_filename, vendor, third_col_value, cost_centre_pdf, internal_pdf, assignment, text, amount)
            st.success(f"PDF generated successfully: [{pdf_filename}]")
            st.download_button(
                label="Click to Download",
                data=open(generated_filename, "rb").read(),
                file_name=generated_filename,
                mime="application/pdf",
            )
            # Save generated PDF as file1.pdf
            with open("file1.pdf", "wb") as f1:
                f1.write(open(generated_filename, "rb").read())

    uploaded_to_document = st.file_uploader("Upload TO Document", type="pdf")

     # Check if additional PDFs are uploaded
    if uploaded_to_document:
        with open("file2.pdf", "wb") as f2:
            f2.write(uploaded_to_document.getvalue())

    uploaded_approval_document = st.file_uploader("Upload Approval Document", type="pdf")

    if uploaded_approval_document:
        with open("file3.pdf", "wb") as f3:
            f3.write(uploaded_approval_document.getvalue())
    
    mergefilename = st.text_input('Rename the Merge file (without Extension):')

    pdf_filenames = ["file1.pdf", "file2.pdf", "file3.pdf"]

    if st.button("Merge PDFs"):
        if not pdf_filename:
            st.warning("Error has occured in the system !!!.")
        else:
            mergefilename = f"{mergefilename}.pdf"
            merged_doc = merge_pdfs(pdf_filenames)
            st.success(f"PDF Merged successfully: [{mergefilename}]")
            st.download_button(
                label="Click to Download the Merged Document",
                data=open(merged_doc, "rb").read(),
                file_name=mergefilename,
                mime="application/pdf",
            ) 
    


if __name__ == '__main__':
    main()
