import mimetypes
import os
import tempfile
from io import BytesIO

from app.models.schemas import EvidenceType


def detect_mime_type(content: bytes, filename: str) -> str:
    """Detect MIME type using python-magic, with extension fallback for local dev."""
    try:
        import magic

        return magic.from_buffer(content, mime=True)
    except (ImportError, OSError, AttributeError):
        guessed, _ = mimetypes.guess_type(filename)
        if guessed:
            return guessed
        lower = filename.lower()
        if lower.endswith((".txt", ".md")):
            return "text/plain"
        if lower.endswith(".pdf"):
            return "application/pdf"
        if lower.endswith(".mp3"):
            return "audio/mpeg"
        if lower.endswith(".wav"):
            return "audio/wav"
        if lower.endswith(".docx"):
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        return "application/octet-stream"


def detect_evidence_type(filename: str, content: bytes, mime_type: str) -> EvidenceType:
    """Auto-detect evidence type from filename and content."""
    fname_lower = filename.lower()

    if any(k in fname_lower for k in ["intake", "journalist", "summary"]):
        return EvidenceType.INTAKE_NOTES
    elif any(k in fname_lower for k in ["email", "chain", "correspondence"]):
        return EvidenceType.EMAIL_CHAIN
    elif any(k in fname_lower for k in ["audio", "recording", "mp3", "wav"]):
        return EvidenceType.AUDIO_RECORDING
    elif any(k in fname_lower for k in ["data", "comparison", "memo", "quantitative"]):
        return EvidenceType.DATA_MEMO
    elif any(k in fname_lower for k in ["personal", "notes", "diary"]):
        return EvidenceType.PERSONAL_NOTES
    else:
        return EvidenceType.OTHER


def extract_text_from_file(filename: str, content: bytes, mime_type: str) -> str:
    """Extract text content from various file types."""

    if mime_type.startswith("text/") or filename.endswith((".txt", ".md")):
        return content.decode("utf-8", errors="ignore")

    elif mime_type == "application/pdf" or filename.endswith(".pdf"):
        import PyPDF2

        reader = PyPDF2.PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    elif mime_type in [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ] or filename.endswith(".docx"):
        from docx import Document

        doc = Document(BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs if p.text)

    elif mime_type in ["audio/mpeg", "audio/wav"] or filename.endswith((".mp3", ".wav")):
        from pydub import AudioSegment
        from speech_recognition import AudioFile, Recognizer

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            if filename.endswith(".mp3"):
                audio = AudioSegment.from_mp3(BytesIO(content))
                audio.export(tmp.name, format="wav")
            else:
                tmp.write(content)
            tmp_path = tmp.name

        try:
            recognizer = Recognizer()
            with AudioFile(tmp_path) as source:
                audio_data = recognizer.record(source)
                return recognizer.recognize_google(audio_data)
        except Exception as e:
            return f"[Audio transcription failed: {str(e)}]"
        finally:
            os.unlink(tmp_path)

    else:
        return "[Unsupported file type for text extraction]"
