import os
import json
import fitz  
import re
from nltk.corpus import stopwords

# stopwords are available
import nltk
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

# folder paths
pdf_folder = "data/unprocessed_pdfs"
output_json_path = "data/processed_json/ds4300_course_notes.json"

# pdf -> json
final_json_output = {"processed_pdfs": []}

def clean_text(text):
    """preprocess text by removing unwanted lines, extra whitespace, and fixing hyphenation issues."""
    lines = text.split("\n")
    cleaned_lines = []
    prev_line = ""

    for line in lines:
        line = line.strip()

        # remove repetitive lines
        if line.lower() in [
            "ds 4300 large scale information storage and retrieval",
            "ds 4300",
            "large scale information storage and retrieval"
        ]:
            continue  

        # fix hyphenation
        if prev_line.endswith("-"):
            line = prev_line[:-1] + line  
        else:
            cleaned_lines.append(prev_line)

        prev_line = line  

    cleaned_lines.append(prev_line) 

    # normalize spaces & remove punctuation
    cleaned_text = " ".join(cleaned_lines)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text) 
    cleaned_text = re.sub(r"[^\w\s]", "", cleaned_text)   
    cleaned_text = cleaned_text.lower()

    return cleaned_text.strip()

def chunk_text(text, chunk_size, overlap):
    """split text into overlapping chunks of specified word count."""
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])  

        # ensure no redundant course title lines in chunks
        if "ds 4300 large scale information storage and retrieval" not in chunk.lower():
            chunks.append(chunk)
        
        # adjust start to ensure overlap
        start += max(chunk_size - overlap, 1)

    return chunks

def process_pdf(pdf_path):
    """extracts text from a pdf, preprocesses it, and chunks it."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"error opening {pdf_path}: {e}")
        return None

    pdf_name = os.path.basename(pdf_path).replace(".pdf", "")

    # extract and clean text
    extracted_text = [clean_text(page.get_text("text")) for page in doc if page.get_text("text")]
    full_text = " ".join(extracted_text).strip()

    if not full_text:
        print(f"skipping {pdf_name} - no text extracted")
        return None

    # create different chunk sizes
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

# process all pdfs in the folder
for pdf_file in os.listdir(pdf_folder):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, pdf_file)
        processed_pdf = process_pdf(pdf_path)
        if processed_pdf:
            final_json_output["processed_pdfs"].append(processed_pdf)

# save final json
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(final_json_output, f, indent=4, ensure_ascii=False)

print(f"finished processing. json saved to: {output_json_path}")
