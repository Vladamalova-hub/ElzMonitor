from app.keywords import KEYWORDS, find_keyword_hits, normalize_text


def test_keywords_detect_variants_in_text():
    text = "В Елизово и Елизовском районе ЕМО готовит новости про северные коряки и Сосновку."
    hits = find_keyword_hits(text)

    assert "елизово" in hits
    assert "елизовский" in hits
    assert "емо" in hits
    assert "северные коряки" in hits
    assert "сосновка" in hits


def test_keyword_normalization_handles_case_and_punctuation():
    text = "Елизово! Елизовский, ЕМО, ..."
    normalized = normalize_text(text)

    assert "елизово" in normalized
    assert "елизовский" in normalized
    assert "емо" in normalized
    assert "крутобереговый" in normalize_text("Крутобереговый")
    assert "северные коряки" in normalize_text("Северные Коряки")
    assert "елизов" in normalize_text("Елизовского района")


def test_keyword_list_contains_known_terms():
    assert "елизово" in KEYWORDS
    assert "елизовский" in KEYWORDS
    assert "сосновка" in KEYWORDS
    assert "северные коряки" in KEYWORDS
    assert "емо" in KEYWORDS


def test_keywords_match_derivatives_like_elizovsky_case():
    text = "В Елизовском районе и в Елизово обсуждают проект ЕМО."
    hits = find_keyword_hits(text)

    assert "елизово" in hits
    assert "елизовский" in hits
    assert "емо" in hits
