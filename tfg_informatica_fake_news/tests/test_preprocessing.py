from preprocessing import clean_text, detect_language, preprocess_record, tokenize_text


def test_clean_text_normalizes_urls_mentions_and_spaces() -> None:
    cleaned = clean_text("Hola   @Canal mira https://example.com  #Bulo")
    assert cleaned == "hola usuario mira url bulo"


def test_tokenize_text_returns_stable_tokens() -> None:
    tokens = tokenize_text("rumor falso sobre vacunas y hospitales")
    assert tokens == ["rumor", "falso", "sobre", "vacunas", "y", "hospitales"]


def test_detect_language_handles_spanish_and_empty() -> None:
    assert detect_language("este rumor es falso y se difunde muy rapido") == "es"
    assert detect_language("   ") == "unknown"


def test_preprocess_record_returns_expected_shape() -> None:
    payload = preprocess_record(
        {
            "message_id": 101,
            "channel": "verificacion",
            "text": "Fact-check urgente sobre una noticia falsa",
        }
    )
    assert payload.message_id == 101
    assert payload.channel == "verificacion"
    assert "fact" in payload.tokens
    assert payload.normalized_text.startswith("fact")
