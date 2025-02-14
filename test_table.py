import pdfplumber

pdf_path = "table.pdf"

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()  # Extract all text on the page
        tables = page.extract_table()  # Extract table data
        
        if tables:
            # Get the position of the first table (assuming 1 table per page)
            first_table_bbox = page.find_tables()[0].bbox  # (x0, y0, x1, y1)

            # Extract text **above** the table
            caption = []
            for line in text.split("\n"):
                if line.strip():
                    words = page.extract_words()
                    for word in words:
                        if word["bottom"] < first_table_bbox[1]:  # If text is above the table
                            caption.append(line)
                            break
            
            # Print extracted caption
            print("Table Caption:", " ".join(caption).strip())

            # Print extracted table
            print("Table Data:")
            for row in tables:
                print(row)
