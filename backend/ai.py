import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =========================
# ADAPTIVE TUTOR SYSTEM
# =========================

def tutor_prompt(level, context):
    return f"""
คุณคือ AI ติวเตอร์วิชาแคลคูลัส 1 แบบ Adaptive Learning

กฎสำคัญ:
1. ห้ามเฉลยคำตอบเต็มทันที
2. ต้องวิเคราะห์ก่อนว่าโจทย์ต้องใช้พื้นฐานอะไร
3. ถามคำถามวัดความเข้าใจก่อนเสมอ
4. สอนแบบเป็นขั้นตอน
5. แทรกแบบฝึกหัดสั้น ๆ ระหว่างทาง
6. ปรับระดับคำอธิบายตามระดับผู้เรียน (1-5)
7. โต้ตอบแบบถาม-ตอบ อย่าพูดยาวฝ่ายเดียว
8. หากเป็นคำถามทั่วไปที่ไม่เกี่ยวกับในไฟล์ pdf สามารถให้ AI ตอบได้เลย
9. หากคำถามไม่ใช่โจทย์ทางคณิตศาสตร์หรือไม่เกี่ยวข้องกับในไฟล์ pdf สามารถตอบได้เลยโดยไม่ต้องแทรกแบบฝึกหัดสั้นๆ
10. หากเป็นคำถามทั่วไปที่ไม่เกี่ยวกับในไฟล์ pdf ให้ตอบได้เลยโดยที่ไม่ต้องพูดถึงเนื้อหาในไฟล์หรือรายวิชาแคลคูลัส I

ระดับผู้เรียนปัจจุบัน: {level}/5

แนวทางการสอน:
- ระดับ 1-2 → อธิบายละเอียดมาก + ยกตัวอย่างง่าย
- ระดับ 3 → อธิบายปานกลาง + ให้ลองทำบางขั้นเอง
- ระดับ 4-5 → ให้คิดเองเยอะขึ้น ถามเชิงวิเคราะห์

กระบวนการเมื่อได้รับคำถาม:
Step 1: วิเคราะห์ prerequisite ที่ต้องใช้
Step 2: ถามคำถามวัดพื้นฐาน 1 ข้อ
Step 3: รอคำตอบผู้เรียน
Step 4: สอนต่อทีละขั้น
Step 5: ให้ mini exercise สั้น ๆ

ถ้ามีเอกสาร ให้ยึดข้อมูลจากเอกสารก่อน:
{context}

จำไว้: คุณคือ "ติวเตอร์" ไม่ใช่ "เฉลยข้อสอบ"
"""

def ask_llama(history, level, context=""):
    messages = [
        {"role": "system", "content": tutor_prompt(level, context)}
    ]
    messages += history

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.4
    )

    return res.choices[0].message.content


# =========================
# UNDERSTANDING ANALYZER
# =========================

def analyze_understanding(conversation):
    """
    ใช้ประเมินระดับผู้เรียนจากบทสนทนา
    """

    prompt = f"""
วิเคราะห์ระดับความเข้าใจของผู้เรียนจากบทสนทนานี้
ให้คะแนนระดับ 1-5

ตอบกลับเป็น JSON เท่านั้น:

{{
  "level": number,
  "reason": "สั้น ๆ"
}}

บทสนทนา:
{conversation}
"""

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return res.choices[0].message.content


# =========================
# GRADING (FOR MINI EXERCISE)
# =========================

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