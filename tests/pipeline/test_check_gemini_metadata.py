"""Fake keys and mocked GETs only; never opens the real .env or a network socket."""

from io import BytesIO
import json
from urllib.error import HTTPError

import pytest

from pipeline import check_gemini_metadata as check


@pytest.mark.parametrize("text", [
    "gemini_api_key=TEST-ONLY-KEY\n", 'GEMINI_API_KEY="TEST-ONLY-KEY" # local\n',
    "export gemini_api_key='TEST-ONLY-KEY'\n", "gemini_api_key=TEST-ONLY-KEY # local\n",
    "unrelated=do-not-evaluate\ngemini_api_key=TEST-ONLY-KEY\n",
])
def test_load_user_named_key_without_shell_expansion(tmp_path, text):
    path = tmp_path / "configuration.txt"
    path.write_text(text, encoding="utf-8-sig")
    assert check.load_key(path) == "TEST-ONLY-KEY"


def test_key_is_an_opaque_literal_not_a_guessed_provider_alphabet(tmp_path):
    path = tmp_path / "configuration.txt"
    path.write_text("gemini_api_key=TEST.ONLY+OPAQUE/VALUE=\n", encoding="utf-8")
    assert check.load_key(path) == "TEST.ONLY+OPAQUE/VALUE="


@pytest.mark.parametrize("text", [
    "unrelated=TEST-ONLY\n", "gemini_api_key=\n", "gemini_api_key=$(get-something)\n",
    'gemini_api_key="unterminated\n', 'gemini_api_key="a" trailing\n',
    "gemini_api_key=a\nGEMINI_API_KEY=b\n", "gemini_api_key='line\\nvalue'\n",
])
def test_configuration_errors_do_not_echo_values(tmp_path, text):
    path = tmp_path / "configuration.txt"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError) as caught:
        check.load_key(path)
    assert text.strip() not in str(caught.value)


class FakeOpener:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def open(self, request, timeout):
        self.requests.append(request)
        assert timeout == 15
        assert request.method == "GET" and request.data is None
        assert request.full_url.startswith(check.HOST)
        assert "TEST-ONLY-KEY" not in request.full_url and "?" not in request.full_url
        assert request.get_header("X-goog-api-key") == "TEST-ONLY-KEY"
        payload = next(self.responses)
        if isinstance(payload, Exception):
            raise payload
        response = BytesIO(payload)
        response.status = 200
        return response


def metadata(model):
    return json.dumps({"name": "models/" + model, "supportedGenerationMethods": ["generateContent"],
                       "untrusted_extra": "TEST-ONLY-KEY C:/private"}).encode()


def test_metadata_probe_only_emits_allowlisted_information():
    opener = FakeOpener([metadata(m) for m in check.MODELS])
    results = check.probe("TEST-ONLY-KEY", opener)
    assert len(opener.requests) == 2
    assert all(r["status"] == "metadata_available" and r["supports_generate_content"] for r in results)
    assert "TEST-ONLY-KEY" not in json.dumps(results)
    assert "private" not in json.dumps(results)
    with pytest.raises(ValueError):
        check.inspect_model("TEST-ONLY-KEY", "other-model", opener)


@pytest.mark.parametrize("code", [401, 403, 429])
def test_access_or_quota_errors_stop_without_retry_or_raw_error(code):
    error = HTTPError("https://example.invalid/TEST-ONLY-KEY", code, "PRIVATE", {}, BytesIO(b"PRIVATE"))
    opener = FakeOpener([error])
    results = check.probe("TEST-ONLY-KEY", opener)
    assert len(opener.requests) == 1
    assert results[0]["http_status"] == code
    assert "PRIVATE" not in json.dumps(results) and "TEST-ONLY-KEY" not in json.dumps(results)


@pytest.mark.parametrize("payload", [b"not JSON", b"{}", b"[]", b"x" * (check.MAX_BYTES + 1),
    b'{"name":"models/gemini-3.8-flash","supportedGenerationMethods":null}',
    b'{"name":"models/gemini-3.8-flash","name":"other"}',
    RuntimeError("PRIVATE TEST-ONLY-KEY")], ids=["bad-json", "empty", "array", "oversized", "null-methods", "duplicate-key", "transport-error"])
def test_bad_or_failed_metadata_is_never_success(payload):
    result = check.inspect_model("TEST-ONLY-KEY", check.MODELS[0], FakeOpener([payload]))
    assert result["status"] != "metadata_available"
    assert "PRIVATE" not in json.dumps(result) and "TEST-ONLY-KEY" not in json.dumps(result)


def test_redirects_are_refused():
    assert check._NoRedirect().redirect_request(None, None, 302, "", {}, "https://other.invalid") is None


def test_cli_local_configuration_uses_no_network_and_hides_key(monkeypatch, capsys):
    monkeypatch.setattr(check, "load_key", lambda path: "TEST-ONLY-KEY")
    monkeypatch.setattr(check, "probe", lambda key: pytest.fail("Local check must not call network"))
    assert check.main([]) == 0
    output = capsys.readouterr().out
    assert "TEST-ONLY-KEY" not in output and "UNVERIFIED" in output


def test_cli_cannot_echo_private_load_failure(monkeypatch, capsys):
    def fail(path):
        raise RuntimeError("PRIVATE TEST-ONLY-KEY")
    monkeypatch.setattr(check, "load_key", fail)
    assert check.main([]) == 1
    output = capsys.readouterr().out
    assert "PRIVATE" not in output and "TEST-ONLY-KEY" not in output
