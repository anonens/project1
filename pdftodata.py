import tabula
import pandas as pd

def get_score_from_row(row, score_type="max"):
    """
    Берілген жолдан (row) ұпайды іздейді.
    Ұпай түрі: "max" - максималды ұпай, "earned" - жинаған ұпай
    """
    score_cols = {
        "max": ["Максималды ұпай", "Максималдыұпай"],
        "earned": ["Жинаған ұпай", "Жинағанұпай", "ұпай"]
    }

    for col in score_cols[score_type]:
        if col in row and pd.notna(row[col]):
            return row[col]
    return None

def pdf_to_DataFrame(pdf_path):
    """
    PDF ішіндегі кестелерден пән, тақырып және ұпайларды шығарады.
    Кестелерді оқып, толыққанды мәліметтер тізімін (list of dicts) қайтарады.
    """
    # PDF-тен барлық кестелерді оқимыз
    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, stream=True)
    results = []

    # Пән атауларының мүмкін тізімі
    possible_subjects = [
        "Қазақстан тарихы", "Оқу сауаттылығы", "Математикалық сауаттылық",
        "Математика", "Информатика", "Физика", "Химия", "Биология",
        "География", "Ағылшын тілі", "Дүниежүзі тарихы",
        "Орыс тілі", "Орыс әдебиеті", "Қазақ тілі", "Қазақ әдебиеті"
    ]

    for table in tables:
        if table.empty:
            continue

        # Баған атауларын тазалаймыз
        table.columns = [str(col).strip() for col in table.columns]

        # Пән атауын анықтау
        subject_name = "Анықталмаған"
        for col in table.columns:
            for subj in possible_subjects:
                if subj in col:
                    subject_name = subj
                    break
            if subject_name != "Анықталмаған":
                break

        current_topic = ""  # Жинақталып жатқан тақырып

        # Кестенің әрбір жолын өңдеу
        for _, row in table.iterrows():
            # Жолдан тақырыптық мәтіндерді жинау (ұпай емес)
            topic_candidates = [
                str(cell).strip() for cell in row
                if isinstance(cell, str)
                and not any(x in cell for x in ["ұпай", "%", "саны", "Жинаған", "Максималды"])
            ]
            topic_text = " ".join(topic_candidates).strip()

            # Ұпайларды алу
            max_score = get_score_from_row(row, "max")
            earned_score = get_score_from_row(row, "earned")

            # Егер ұпай жоқ болса — тақырып жалғасып жатыр
            if pd.isna(max_score) and pd.isna(earned_score):
                current_topic += " " + topic_text
                continue

            # Егер ұпай табылса — жинақталған тақырыппен бірге жазамыз
            full_topic = current_topic.strip() + " " + topic_text if current_topic else topic_text
            current_topic = ""  # Тақырыпты жаңарту

            if pd.notna(max_score) and pd.notna(earned_score):
                try:
                    results.append({
                        "Пән": subject_name,
                        "Тақырып": full_topic.strip(),
                        "Максималды ұпай": int(float(max_score)),
                        "Жинаған ұпай": int(float(earned_score))
                    })
                except Exception:
                    pass  # Қате болған жағдайда өткізіп жібереміз

    return results
