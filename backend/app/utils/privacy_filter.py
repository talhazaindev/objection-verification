import re
from typing import Optional

_analyzer = None
_anonymizer = None
_presidio_available: Optional[bool] = None


def _init_presidio():
    global _analyzer, _anonymizer, _presidio_available
    if _presidio_available is not None:
        return
    try:
        from presidio_analyzer import AnalyzerEngine
        from presidio_analyzer.nlp_engine import NlpEngineProvider
        from presidio_anonymizer import AnonymizerEngine

        nlp_engine = NlpEngineProvider(
            nlp_configuration={
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
            }
        ).create_engine()
        _analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
        _anonymizer = AnonymizerEngine()
        _presidio_available = True
    except Exception:
        _presidio_available = False


def sanitize_text(text: str) -> str:
    """Remove PII using Presidio NER when available, regex fallback otherwise."""
    if not text:
        return text

    _init_presidio()
    if _presidio_available and _analyzer and _anonymizer:
        try:
            results = _analyzer.analyze(
                text=text,
                language="en",
                entities=[
                    "EMAIL_ADDRESS",
                    "PHONE_NUMBER",
                    "US_SSN",
                    "CREDIT_CARD",
                    "PERSON",
                    "LOCATION",
                    "DATE_TIME",
                    "IBAN_CODE",
                ],
                score_threshold=0.4,
            )
            if results:
                return _anonymizer.anonymize(text=text, analyzer_results=results).text
        except Exception:
            pass

    return _sanitize_regex(text)


def _sanitize_regex(text: str) -> str:
    """Regex fallback when Presidio is unavailable."""
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "[EMAIL_REDACTED]",
        text,
    )
    text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE_REDACTED]", text)
    text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN_REDACTED]", text)
    text = re.sub(
        r"\b(?:\d{4}[- ]?){3}\d{4}\b",
        "[CARD_REDACTED]",
        text,
    )
    return text
