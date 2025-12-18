from utils.text_extractor import extract_text_from_pdf, clean_text

resume_text = extract_text_from_pdf("data/sample_resume.pdf")
cleaned_text = clean_text(resume_text)

print(cleaned_text[:500])
