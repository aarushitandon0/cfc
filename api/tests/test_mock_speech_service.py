from api.services.mock_speech_service import MockSpeechService

service = MockSpeechService()


def test_transcribe_decodes_utf8_bytes():
    assert service.transcribe("दवाई कम है".encode("utf-8"), "hi-IN") == "दवाई कम है"


def test_transcribe_handles_non_text_payload():
    result = service.transcribe(b"\xff\xfe\x00\x01", "hi-IN")
    assert "mock transcript" in result


def test_translate_known_demo_phrase():
    assert service.translate_to_english("दवाई कम है", "hi-IN") == "Medicine stock is low"


def test_translate_unknown_phrase_falls_back_with_marker():
    result = service.translate_to_english("कुछ और बात", "hi-IN")
    assert result.startswith("[mock translation from hi-IN]")
    assert "कुछ और बात" in result


def test_translate_english_passthrough():
    assert service.translate_to_english("All beds full", "en-IN") == "All beds full"
