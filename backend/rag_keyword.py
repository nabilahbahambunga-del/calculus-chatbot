import os
import json
import re

CHUNK_FILE = "chunks.json"


# ---------------------------
# 1. Split text เป็น chunk
# ---------------------------
def split_text(text, chunk_size=800):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks


# ---------------------------
# 2. Save chunk ลงไฟล์
# ---------------------------
def save_chunks(new_chunks):
    if os.path.exists(CHUNK_FILE):
        with open(CHUNK_FILE, "r", encoding="utf-8") as f:
            old_chunks = json.load(f)
    else:
        old_chunks = []

    all_chunks = old_chunks + new_chunks

    with open(CHUNK_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)


# ---------------------------
# 3. โหลด chunk
# ---------------------------
def load_chunks():
    if not os.path.exists(CHUNK_FILE):
        return []

    with open(CHUNK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------
# 4. ค้นหาแบบ keyword
# ---------------------------
def search_keyword(query, top_k=3):
    chunks = load_chunks()
    if not chunks:
        return []

    query_words = set(re.findall(r'\w+', query.lower()))

    scored = []

    for chunk in chunks:
        chunk_words = set(re.findall(r'\w+', chunk.lower()))
        score = len(query_words & chunk_words)

        if score > 0:
            scored.append((score, chunk))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [chunk for _, chunk in scored[:top_k]]