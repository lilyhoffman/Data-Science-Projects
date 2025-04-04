import os
import json
import fitz  # PDF processing
import re
from nltk.corpus import stopwords
import nltk

# Ensure stopwords are available
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))  # e.g. 'ours', 'you', 'below'

# Folder paths
pdf_folder = "data/unprocessed_pdfs"
output_json_path = "data/processed_json/ds4300_course_notes.json"

# Final output structure for processed PDFs
final_json_output = {"processed_pdfs": []}


def clean_text(text):
    """Preprocess text by removing unwanted lines, extra whitespace, and fixing hyphenation issues."""
    lines = text.split("\n")
    cleaned_lines = []
    prev_line = ""

    for line in lines:
        line = line.strip()

        # Remove repetitive lines (course titles)
        if line.lower() in [
            "ds 4300 large scale information storage and retrieval",
            "ds 4300",
            "large scale information storage and retrieval"
        ]:
            continue  

        # Fix hyphenated line breaks (e.g. infor-mation -> information)
        if prev_line.endswith("-"):
            line = prev_line[:-1] + line  
        else:
            cleaned_lines.append(prev_line)

        prev_line = line  

    cleaned_lines.append(prev_line)  # Add the last processed line

    # Normalize spaces and remove punctuation
    cleaned_text = " ".join(cleaned_lines)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)  # Normalize multiple spaces
    cleaned_text = re.sub(r"[^\w\s]", "", cleaned_text)  # Remove non-word characters (punctuation)
    cleaned_text = cleaned_text.lower()  # Convert to lowercase

    return cleaned_text.strip()  # Return cleaned text


def chunk_text(text, chunk_size, overlap):
    """Split text into overlapping chunks of specified word count."""
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])  # Create a chunk from the word list

        # Ensure no redundant course title lines in chunks
        if "ds 4300 large scale information storage and retrieval" not in chunk.lower():
            chunks.append(chunk)
        
        # Adjust start to ensure overlap
        start += max(chunk_size - overlap, 1)

    return chunks


def process_pdf(pdf_path):
    """Extracts text from a PDF, preprocesses it, and chunks it into different sizes."""
    try:
        doc = fitz.open(pdf_path)  # Open the PDF file
    except Exception as e:
        print(f"Error opening {pdf_path}: {e}")
        return None

    pdf_name = os.path.basename(pdf_path).replace(".pdf", "")  # Get the PDF file name (without extension)

    # Extract and clean text from each page
    extracted_text = [clean_text(page.get_text("text")) for page in doc if page.get_text("text")]
    full_text = " ".join(extracted_text).strip()

    if not full_text:
        print(f"Skipping {pdf_name} - no text extracted")
        return None

    # Create different chunk sizes and overlaps
    chunk_sizes = [200, 500, 1000]
    overlaps = [0, 50, 100]

    chunked_versions = {}
    for chunk_size in chunk_sizes:
        for overlap in overlaps:
            key = f"{chunk_size}_words_overlap_{overlap}"
            chunked_versions[key] = chunk_text(full_text, chunk_size, overlap)

    return {
        "title": pdf_name,
        "chunked_content": chunked_versions
    }


# Process all PDFs in the folder
for pdf_file in os.listdir(pdf_folder):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        processed_pdf = process_pdf(pdf_path)
        if processed_pdf:
            final_json_output["processed_pdfs"].append(processed_pdf)

# Save final JSON output
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(final_json_output, f, indent=4, ensure_ascii=False)

print(f"Finished processing. JSON saved to: {output_json_path}")
