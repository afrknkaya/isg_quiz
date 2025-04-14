import fitz  # PyMuPDF
import streamlit as st
import re
import time

def parse_questions(pdf_path):
    doc = fitz.open(pdf_path)
    content = ""
    for page in doc:
        content += page.get_text("text", sort=True)

    pattern = r"(\d+[.)]\s*.+?)(?=\s*\d+[.)]|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    parsed = []
    for match in matches:
        lines = [line.strip() for line in match.split('\n') if line.strip()]
        if not lines:
            continue
        
        question_text = []
        options = []
        question_number = re.sub(r"\D", "", lines[0].split()[0])
        
        for line in lines:
            if re.match(r"^[a-d][.)]", line, re.IGNORECASE):
                options.append(line)
            else:
                question_text.append(line)
        
        parsed.append({
            "question": " ".join(question_text),
            "options": options,
            "number": question_number
        })
    
    return parsed

def parse_correct_answers(pdf_path):
    doc = fitz.open(pdf_path)
    content = ""
    for page in doc:
        content += page.get_text("text", sort=True)

    pattern = r"(\d+[.)]\s*)(.+?)(?=\n\d+[.)]|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    correct_answers = {}
    for match in matches:
        question_number = re.sub(r"\D", "", match[0])
        answer_text = match[1].strip()
        
        correct_option = re.search(r"\b([a-d])[.)]", answer_text, re.IGNORECASE)
        if correct_option:
            correct_answers[question_number] = correct_option.group(1).lower()
    
    return correct_answers

def main():
    st.title("İSG Sınav Uygulaması")
    
    questions = parse_questions("sorular_ve_siklar.pdf")
    correct_answers = parse_correct_answers("dogru_cevaplar.pdf")

    if "index" not in st.session_state:
        st.session_state.index = 0
    if "answered" not in st.session_state:
        st.session_state.answered = False

    question_count = len(questions)
    
    # YENİ: Soru atlama mekanizması
    col_jump1, col_jump2, col_jump3 = st.columns([2,1,2])
    with col_jump1:
        jump_number = st.number_input("Gitmek İstediğiniz Soru Numarası:", 
                                    min_value=1, 
                                    max_value=question_count, 
                                    value=st.session_state.index+1)
    with col_jump2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Atla"):
            new_index = jump_number - 1
            if 0 <= new_index < question_count:
                st.session_state.index = new_index
                st.session_state.answered = False
                st.rerun()

    # Navigasyon butonları
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⟵ Geri") and st.session_state.index > 0:
            st.session_state.index -= 1
            st.session_state.answered = False
            st.rerun()
    with col3:
        if st.button("İleri ⟶") and st.session_state.index < question_count - 1:
            st.session_state.index += 1
            st.session_state.answered = False
            st.rerun()

    # Mevcut soruyu göster
    soru = questions[st.session_state.index]
    st.subheader(f"{soru['number']}. Soru")
    st.markdown(f"**{soru['question']}**")

    selected_option = st.radio(
        "Şıkları seçin:",
        soru['options'],
        key=f"q{st.session_state.index}",
        index=None
    )

    # Cevap kontrolü
    if selected_option and not st.session_state.answered:
        selected_letter = selected_option[0].lower()
        correct = correct_answers.get(soru['number'], None)

        if correct and selected_letter == correct:
            st.success("✅ Doğru cevap!")
            st.session_state.answered = True
            time.sleep(0.5)
            if st.session_state.index < question_count - 1:
                st.session_state.index += 1
                st.session_state.answered = False
                st.rerun()

    # İlerleme çubuğu
    progress = st.progress((st.session_state.index + 1)/question_count)
    st.caption(f"**İlerleme: {st.session_state.index + 1}/{question_count}**")

if __name__ == "__main__":
    main()
