import os
import fitz  # PyMuPDF
import io
from PIL import Image, UnidentifiedImageError
import easyocr
import numpy as np
import shutil
from PyPDF2 import PdfWriter

# def save_pdf_with_text(text, output_path):
#     """Saves extracted text to a PDF file."""
#     writer = PdfWriter()
#     # Create a new page
#     writer.add_page()
#     # Create a temporary document to add text
#     temp_doc = fitz.open()
#     page = temp_doc.new_page()
#     # Insert text into the page
#     page.insert_text((72, 72), text)  # Position (72, 72) is 1 inch from the top-left corner
#     temp_doc.save(output_path)
#     temp_doc.close()
def save_pdf_with_text(text, output_path):
    """Saves extracted text to a PDF file."""
    # Create a temporary document using PyMuPDF
    temp_doc = fitz.open()
    page = temp_doc.new_page()  # Create a new page in the temporary document
    page.insert_text((72, 72), text)  # Position (72, 72) is 1 inch from the top-left corner

    # Save the temporary document to a file
    temp_doc.save(output_path)
    temp_doc.close()
def extract_text_from_pdf(pdf_path):
    """Checks if PDF has text, and if not, extracts text from images."""
    has_text = False
    extracted_text = ""

    with fitz.open(pdf_path) as doc:
        print(f"working on {pdf_path}")
        for page in doc:
            text = page.get_text()
            if text:
                pdf_type = "TEXT"
                print(f"{pdf_path} this is text pdf")
                return pdf_type, extracted_text
                # if text.strip():
                #     has_text = True
                #     extracted_text += text + "\n"  # Collect text if found
            else:
                # Extract images if no text is found
                extracted_text = ""
                for img in page.get_images(full=True):
                    xref = img[0]  # Corrected this line
                    base_image = doc.extract_image(xref)
                    image_data = base_image["image"]

                    # Process the image for OCR
                    try:
                        image = Image.open(io.BytesIO(image_data))
                        image.verify()  # Ensure the image is valid
                        image = Image.open(io.BytesIO(image_data))  # Reopen after verification
                    except UnidentifiedImageError:
                        print(f"Unidentified image in PDF: {pdf_path}")
                        continue
                    image_array = np.array(image)

                    # Create an EasyOCR Reader instance
                    reader = easyocr.Reader(['en', 'ur'])  # 'en' specifies the language; add more as needed

                    # Perform OCR on the image
                    text = reader.readtext(image_array, detail=0)  # Set detail=0 to get plain text

                    extracted_text += ' '.join(text)
                    # Print the extracted text
                    print(' '.join(text))
                    pdf_type = "IMAGE"
                    return pdf_type, extracted_text.strip()



def process_pdfs(original_doc):
    abc = os.listdir(original_doc)
    for sub_fol in abc:

        for pdfs in os.listdir(os.path.join(original_doc,sub_fol)):
            if pdfs.endswith(".pdf"):
                pdf_path= os.path.join(original_doc,sub_fol,pdfs)
                pdf_type, ocr_text = extract_text_from_pdf(pdf_path)
                preprocessed_data="preprocessed_data"

                if pdf_type == "TEXT":
                    # Move the PDF to the text folder
                    destination= os.path.join(preprocessed_data,sub_fol)
                    shutil.move(pdf_path, destination)

                elif pdf_type == "IMAGE" and ocr_text:
                    output_pdf_path = os.path.join(preprocessed_data,sub_fol, f"OCR_{pdfs}")
                    save_pdf_with_text(ocr_text, output_pdf_path)

process_pdfs("original_judgments")
