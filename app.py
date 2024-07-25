from flask import Flask, request, render_template_string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from fpdf import FPDF
import os

app = Flask(__name__)

# Replace with your email address and app password
EMAIL_ADDRESS = 'haulisyahran@gmail.com'
EMAIL_PASSWORD = 'fnfh otqz kajp pshe'  # Use the app password here

# Class to create the PDF template
class PDF(FPDF):
    def header(self):
        # Logo
        ##self.image('telkomsel_logo.png', 10, 8, 33)  # Add your logo path
        self.set_font('Arial', 'B', 12)
        self.cell(80)
        self.cell(30, 10, 'Kontrak Berlangganan', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(80)
        self.cell(30, 10, 'Subscription Contract', 0, 1, 'C')
        self.cell(80)
        self.cell(30, 10, 'Nomor : 25/LG.05/EM-04/JTG-DIY', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_entry(self, label, value):
        self.set_font('Arial', 'B', 10)
        self.cell(50, 10, f'{label}', 0, 0)
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f': {value}', 0, 1)

# Function to create a PDF from form data
# Function to create a PDF from form data
def create_pdf(data, pdf_path):
    pdf = PDF()
    pdf.add_page()

    # Add content to the PDF
    pdf.chapter_title('Kontrak Berlangganan ini dibuat dan diadakan antara TELKOMSEL dengan Hanif pada waktu sebagaimana disebutkan di bagian bawah Kontrak Berlangganan ("tanggal penandatanganan").')

    pdf.chapter_body('Jenis Permohonan:')
    if 'jenis_permintaan' in data:
        for item in data['jenis_permintaan']:
            pdf.add_entry('', item)

    pdf.chapter_body('Tipe Pelanggan:')
    if 'tipe_pelanggan' in data:
        for item in data['tipe_pelanggan']:
            pdf.add_entry('', item)
    pdf.add_entry('No.PKS/WOSPK/MOU/BAK', data.get('no_corporate', [''])[0])

    pdf.add_entry('Nomor Telkomsel Halo (Baru/Tambahan)', data.get('nomor_halo_baru', [''])[0])
    pdf.add_entry('Nomor Telkomsel Halo Utama (jika ada)', data.get('nomor_halo_utama', [''])[0])
    pdf.add_entry('Nomor Prabayar', data.get('nomor_prabayar', [''])[0])
    pdf.add_entry('Nama Perusahaan', data.get('nama_perusahaan', [''])[0])
    pdf.add_entry('Nama Pelanggan / Nama Kontak Perusahaan', data.get('nama_pelanggan', [''])[0])
    pdf.add_entry('No. Induk Kependudukan', data.get('no_nik', [''])[0])
    pdf.add_entry('No. Kartu Keluarga', data.get('no_kk', [''])[0])
    pdf.add_entry('Tempat, Tanggal Lahir', data.get('tempat_tanggal_lahir', [''])[0])

    pdf.chapter_body('Kartu Identitas (Untuk WNA):')
    if 'kartu_identitas' in data:
        for item in data['kartu_identitas']:
            pdf.add_entry('', item)

    pdf.add_entry('No. Paspor/KITAP/KITAS', data.get('no_paspor', [''])[0])
    pdf.add_entry('Masa Berlaku Paspor/KITAP/KITAS', data.get('masa_berlaku', [''])[0])
    pdf.add_entry('Kewarganegaraan', data.get('kewarganegaraan', [''])[0])

    pdf.chapter_body('Alamat (Jika Berbeda dengan data dukcapil):')
    if 'alamat_berbeda' in data:
        for item in data['alamat_berbeda']:
            pdf.add_entry('', item)

    pdf.add_entry('Kode Pos', data.get('kode_pos', [''])[0])
    pdf.add_entry('Kota', data.get('kota', [''])[0])
    pdf.add_entry('Provinsi', data.get('provinsi', [''])[0])
    pdf.add_entry('Alamat Email e-Bill', data.get('email', [''])[0])
    pdf.add_entry('No. Telepon (Kantor/Rumah)', data.get('telepon', [''])[0])
    pdf.add_entry('Ext', data.get('ext', [''])[0])

    pdf.output(pdf_path)

# Function to send email with PDF attachment
def send_email(subject, body, to_email, pdf_path):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    # Attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # Open the PDF file in binary mode
    with open(pdf_path, "rb") as attachment:
        part = MIMEApplication(attachment.read(), Name=os.path.basename(pdf_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
        msg.attach(part)

    try:
        print("Trying to connect to the SMTP server...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            print("Logging in...")
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            print("Sending email...")
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/')
def form():
    return render_template_string(open('form.html').read())

@app.route('/submit', methods=['POST'])
def submit():
    # Get form data
    data = request.form.to_dict(flat=False)

    # Create a PDF file from the form data
    pdf_path = "form_data.pdf"
    create_pdf(data, pdf_path)

    # Send the email with the PDF attachment
    body = "Please find the attached PDF containing the form submission data."
    send_email('Form Submission', body, 'rezaathari99@gmail.com', pdf_path)

    # Optionally, remove the PDF file after sending the email
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    return 'Form submitted and email sent successfully!'

if __name__ == '__main__':
    app.run(debug=True)
