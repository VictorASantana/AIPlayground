import fitz

def extract_text_from_pdf(pdf_file):
  doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
  text = "\n".join([page.get_text() for page in doc])
  return text

def extract_text_from_txt(txt_file):
  return txt_file.read().decode("utf-8")