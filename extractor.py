import fitz  # PyMuPDF
import os
import json
import re
from collections import Counter

INPUT_DIR = "appA/input"
OUTPUT_DIR = "appA/output"

def extract_text_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    all_blocks = []

    for page_number, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block['type'] != 0:
                continue  # Skip non-text blocks

            for line in block['lines']:
                line_text = ""
                fonts = []
                for span in line['spans']:
                    text = span['text'].strip()
                    if text:
                        line_text += text + " "
                        fonts.append({
                            "size": round(span["size"], 1),
                            "font": span["font"],
                            "flags": span["flags"]
                        })

                if line_text.strip():
                    all_blocks.append({
                        "text": line_text.strip(),
                        "fonts": fonts,
                        "page": page_number
                    })

    return all_blocks

def get_font_size_hierarchy(blocks):
    sizes = [span["size"] for block in blocks for span in block["fonts"]]
    common_sizes = Counter(sizes).most_common()

    if not common_sizes:
        return {}

    sorted_sizes = sorted([s[0] for s in common_sizes], reverse=True)
    size_map = {}
    if len(sorted_sizes) >= 1:
        size_map[sorted_sizes[0]] = "TITLE"
    if len(sorted_sizes) >= 2:
        size_map[sorted_sizes[1]] = "H1"
    if len(sorted_sizes) >= 3:
        size_map[sorted_sizes[2]] = "H2"
    if len(sorted_sizes) >= 4:
        size_map[sorted_sizes[3]] = "H3"

    return size_map

def classify_heading_level(text):
    text = text.strip()
    match = re.match(r"^(\d+(\.\d+)*)([\s\.:\\-]+)?[A-Za-z]", text)
    if match:
        num_part = match.group(1)
        dot_count = num_part.count(".")
        if dot_count == 0:
            return "H1"
        elif dot_count == 1:
            return "H2"
        else:
            return "H3"
    return None

def is_probable_heading(text, size, fontname, is_bold=False):
    text = text.strip()

    if len(text) < 4 or text.isdigit():
        return False

    # Reject common date formats like "18 JUNE 2013" or "6 NOV 2013"
    date_pattern = r"^\d{1,2}\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+\d{4}$"
    if re.match(date_pattern, text.upper()):
        return False

    rejection_keywords = [
        "name", "designation", "service", "pay", "whether", "permanent", "temporary",
        "amount", "required", "block", "home town", "husband", "wife", "age",
        "date", "fare", "advance", "signature", "persons", "relationship", "declare"
    ]
    if any(word in text.lower() for word in rejection_keywords):
        return False

    if len(text.split()) > 20:
        return False

    if text[0].islower():
        return False

    if not is_bold and size < 10:
        return False

    return True

def extract_headings(blocks):
    result = {
        "title": None,
        "outline": []
    }

    size_map = get_font_size_hierarchy(blocks)
    seen = set()

    # Combine multiple TITLE lines as title
    for block in blocks:
        avg_size = round(sum(f["size"] for f in block["fonts"]) / len(block["fonts"]), 1)
        tag = size_map.get(avg_size)
        if tag == "TITLE":
            if result["title"] is None:
                result["title"] = block["text"]
            else:
                result["title"] += " " + block["text"]

    for block in blocks:
        if not block["fonts"]:
            continue

        text = block["text"]
        page = block["page"]
        font = block["fonts"][0]["font"]
        size = round(sum(f["size"] for f in block["fonts"]) / len(block["fonts"]), 1)
        flags = block["fonts"][0]["flags"]
        is_bold = bool(flags & 2)

        if not is_probable_heading(text, size, font, is_bold):
            continue

        # Prefer numbering logic if available
        level = classify_heading_level(text)
        if not level and size == next((s for s, t in size_map.items() if t == "H1"), None) and is_bold:
            level = "H1"
        elif not level and size == next((s for s, t in size_map.items() if t == "H2"), None):
            level = "H2"
        elif not level and size == next((s for s, t in size_map.items() if t == "H3"), None):
            level = "H3"

        if level in ["H1", "H2", "H3"]:
            key = f"{text.lower()}@{page}"
            if key not in seen:
                seen.add(key)
                result["outline"].append({
                    "level": level,
                    "text": text,
                    "page": page
                })

    if not result["title"] and blocks:
        result["title"] = blocks[0]["text"]

    return result

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(INPUT_DIR, filename)
            blocks = extract_text_blocks(pdf_path)

            raw_output = filename.replace(".pdf", "_raw.json")
            with open(os.path.join(OUTPUT_DIR, raw_output), "w") as f:
                json.dump(blocks, f, indent=2)

            structured = extract_headings(blocks)
            structured_output = filename.replace(".pdf", "_structured.json")
            with open(os.path.join(OUTPUT_DIR, structured_output), "w") as f:
                json.dump(structured, f, indent=2)

            print(f"[✓] Processed {filename}")

if __name__ == "__main__":
    main()
