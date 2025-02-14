import pdfplumber

def extract_text_lines_and_tables(pdf_path, page_number):
    content = {"Text_Lines": [], "Tables": []}

    with pdfplumber.open(pdf_path) as pdf:
        if page_number >= len(pdf.pages):
            return "Invalid Page Number"

        page = pdf.pages[page_number]

        # Extract text lines with positions
        text_lines = []
        for word in page.extract_words():
            text_lines.append({
                "text": word["text"],
                "x0": word["x0"],
                "top": word["top"],
                "x1": word["x1"],
                "bottom": word["bottom"]
            })

        tables_with_positions = []
        for table in page.find_tables():
            bbox = table.bbox  # (x0, top, x1, bottom)
            table_data = table.extract()
            tables_with_positions.append({"bbox": bbox, "data": table_data})

        content["Text_Lines"] = text_lines
        content["Tables"] = tables_with_positions

    return content

def is_table_between_text(table_bbox, text_lines):
    table_top, table_bottom = table_bbox[1], table_bbox[3]

    for i in range(len(text_lines) - 1):
        text_top, text_bottom = text_lines[i]["bottom"], text_lines[i+1]["top"]

        if text_top <= table_top and text_bottom >= table_bottom:
            return (text_lines[i]["text"], text_lines[i+1]["text"])  # Lines enclosing the table
    return None

pdf_path = "./code.pdf"
page_number = 4

result = extract_text_lines_and_tables(pdf_path, page_number)

print(result["Text_Lines"])