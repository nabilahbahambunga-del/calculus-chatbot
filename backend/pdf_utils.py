import pdfplumber

def pdf_to_text(path: str, max_pages: int = 100):
    """
    อ่าน PDF แบบปลอดภัย จำกัดจำนวนหน้า
    กัน RAM พัง และกัน None error
    """

    text_parts = []

    with pdfplumber.open(path) as pdf:

        total_pages = len(pdf.pages)

        # จำกัดจำนวนหน้า (กันไฟล์โหดเกิน)
        pages_to_read = min(total_pages, max_pages)

        for i in range(pages_to_read):
            page = pdf.pages[i]
            page_text = page.extract_text()

            if page_text:  # กัน None
                text_parts.append(page_text)

    return "\n".join(text_parts)