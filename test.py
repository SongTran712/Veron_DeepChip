import fitz  # PyMuPDF

# Open the PDF file
doc = fitz.open("code.pdf")

# Define the page range (PyMuPDF uses 0-based indexing, so pages 4 and 5 are at indices 3 and 4)
with open("output.txt", "w", encoding="utf-8") as f:
    for page_num in range(3, 5):  # Read pages 4 and 5
        page = doc[page_num]  # Access specific page
        text_instances = page.get_text("dict")  # Extract structured text data
        for block in text_instances.get("blocks", []):  # Safely get blocks
            for line in block.get("lines", []):
                line_text = " ".join(span["text"] for span in line["spans"])  # Merge spans
                
                # Use the first span's font for the entire line
                line_font = line["spans"][0]["font"] if line["spans"] else "Unknown"
                
                f.write(f"Page {page_num + 1}:\n")
                f.write(f"  Line Text: {line_text}\n")
                f.write(f"  Line Font: {line_font}\n")
                f.write("-" * 40 + "\n")

print("Output written to output.txt")
