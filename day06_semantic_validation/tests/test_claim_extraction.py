from day06_semantic_validation.claims import extract_claims


def test_single_factual_sentence_creates_one_claim():
    answer = "Refunds are processed within 5–7 business days."

    claims = extract_claims(answer)

    assert len(claims) == 1
    assert claims[0].text == "Refunds are processed within 5–7 business days."


def test_multiple_factual_sentences_create_multiple_claims():
    answer = (
        "Refunds are processed within 5–7 business days. "
        "The policy was updated in 2022."
    )

    claims = extract_claims(answer)

    assert len(claims) == 2
    assert claims[0].text.startswith("Refunds")
    assert claims[1].text.startswith("The policy")


def test_non_factual_sentences_are_ignored():
    answer = "I think refunds are reasonable."

    claims = extract_claims(answer)

    assert claims == []


def test_mixed_factual_and_non_factual_sentences():
    answer = (
        "I believe refunds are fair. "
        "Refunds are processed within 5–7 business days."
    )

    claims = extract_claims(answer)

    assert len(claims) == 1
    assert "5–7 business days" in claims[0].text


def test_empty_answer_produces_no_claims():
    claims = extract_claims("")
    assert claims == []