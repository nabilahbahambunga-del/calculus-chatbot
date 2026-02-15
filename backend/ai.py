import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------- Tutor ----------
def tutor_prompt(level, context):
    return f"""
คุณคือผู้ช่วยสอนแคลคูลัส 1
สอนแบบติวเตอร์ อธิบายเป็นขั้นตอน
อย่าเฉลยทันที ให้แนวทางก่อน
สอนตามระดับความเข้าใจของผู้ใช้ โดยอิงจากในไฟล์เอกสารเป็นหลัก
ระดับผู้เรียน: {level}/5

ถ้ามีเอกสาร ใช้ข้อมูลด้านล่าง:
{context}
"""

def ask_llama(history, level, context=""):
    messages = [{"role": "system", "content": tutor_prompt(level, context)}]
    messages += history

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.3
    )
    return res.choices[0].message.content


# ---------- Grading ----------
def grade_answer(question, answer):
    prompt = f"""
คุณคือผู้ตรวจคำตอบวิชาแคลคูลัส

ให้คะแนนคำตอบนักศึกษาจาก 0-10
ตอบกลับเป็น JSON เท่านั้นในรูปแบบนี้:

{{
  "score": number,
  "correct": true/false
}}

คำถาม: {question}
คำตอบนักศึกษา: {answer}
"""

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return res.choices[0].message.content
