"""Chat Completions contract tests: mock HTTP only, no credentials or PostgreSQL required."""

from __future__ import annotations

import json
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from api import config, deps, llm, main
from api.store.answers import AnswerStore

EVIDENCE = [{"id": "chunk-1", "document_id": "doc-1", "title": "선내 매뉴얼",
             "text": "검증된 원문 근거 문장이 이곳에 있습니다."}]
STATEMENT = {"text": "검증된 근거를 확인하세요.", "chunkId": "chunk-1", "quote": EVIDENCE[0]["text"]}
VALID_ANSWER = {"insufficient": False, "statements": [STATEMENT]}


def completion(answer=VALID_ANSWER, *, finish_reason="stop", **message_fields):
    return {"choices": [{"finish_reason": finish_reason, "message": {
        "role": "assistant", "content": json.dumps(answer, ensure_ascii=False), **message_fields,
    }}]}


@pytest.fixture(autouse=True)
def clean_model_environment(monkeypatch):
    for name in ("OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_BASE_URL", "OPENAI_RESPONSE_FORMAT"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def model_server(monkeypatch):
    clients = []

    def install(payload=None, *, status=200, raw=None, error=None):
        calls = []

        def handler(request):
            calls.append(request)
            if error:
                raise error("Simulated model failure", request=request)
            if raw is not None:
                return httpx.Response(status, content=raw)
            return httpx.Response(status, json=payload)

        client = httpx.Client(transport=httpx.MockTransport(handler))
        clients.append(client)
        monkeypatch.setattr(llm.httpx, "post", client.post)
        return calls

    yield install
    for client in clients:
        client.close()


@pytest.mark.parametrize("base", [None, "", "https://api.openai.com/v1", "https://api.openai.com/v1/"])
def test_existing_openai_settings_require_key_and_preserve_default(monkeypatch, base):
    if base is not None:
        monkeypatch.setenv("OPENAI_BASE_URL", base)
    monkeypatch.setenv("OPENAI_MODEL", "configured-model")
    assert config.llm_configured() is False
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-secret")
    settings = config.llm_settings()
    assert settings.base_url == "https://api.openai.com/v1"
    assert settings.model == "configured-model"
    assert "test-only-secret" not in repr(settings)


@pytest.mark.parametrize("base", [
    "ftp://localhost/v1", "https://", "not-a-url", "http://localhost:invalid/v1",
    "https://name:password@model.example/v1", "https://model.example/v1?key=x",
    "https://model.example/v1#fragment", "http://local host/v1",
])
def test_invalid_addresses_disable_model_without_network(monkeypatch, base):
    monkeypatch.setenv("OPENAI_BASE_URL", base)
    monkeypatch.setenv("OPENAI_MODEL", "local-model")
    assert config.llm_settings() is None
    assert config.llm_configured() is False


@pytest.mark.parametrize("base,key", [
    ("https://api.openai.com/v1/", "test-only-secret"),
    ("https://gateway.example/custom/v1/", "test-only-secret"),
    ("http://127.0.0.1:11434/v1/", ""),
    ("http://host.docker.internal:11434/v1/", ""),
])
@pytest.mark.parametrize("language,expected", [("ko", "Korean"), ("en", "English")])
def test_chat_completions_request_and_valid_citations(monkeypatch, model_server, base, key, language, expected):
    monkeypatch.setenv("OPENAI_BASE_URL", base)
    monkeypatch.setenv("OPENAI_MODEL", "supplied-model-id")
    monkeypatch.setenv("OPENAI_API_KEY", key)
    calls = model_server(completion())
    assert AnswerStore.grounded_statements("질문", EVIDENCE, language) == [STATEMENT]
    assert len(calls) == 1
    request = calls[0]
    assert str(request.url) == base.rstrip("/") + "/chat/completions"
    assert request.headers.get("Authorization") == ("Bearer " + key if key else None)
    body = json.loads(request.content)
    assert set(body) == {"model", "messages", "stream"}
    assert body["model"] == "supplied-model-id" and body["stream"] is False
    assert expected in body["messages"][0]["content"]
    assert "untrusted data" in body["messages"][0]["content"]
    assert json.loads(body["messages"][1]["content"])["evidence"][0]["chunkId"] == "chunk-1"
    assert request.extensions["timeout"]["read"] == 25


@pytest.mark.parametrize("output_format", ["json_object", "json_schema"])
def test_opt_in_json_formats_use_chat_completions_schema(monkeypatch, model_server, output_format):
    monkeypatch.setenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("OPENAI_MODEL", "local-model")
    monkeypatch.setenv("OPENAI_RESPONSE_FORMAT", output_format)
    calls = model_server(completion())
    AnswerStore.grounded_statements("question", EVIDENCE, "en")
    response_format = json.loads(calls[0].content)["response_format"]
    assert response_format["type"] == output_format
    if output_format == "json_schema":
        schema = response_format["json_schema"]
        assert schema["strict"] is True
        assert set(schema["schema"]["required"]) == {"insufficient", "statements"}


class MemoryWorkspace(AnswerStore):
    """Use the real answer orchestration with in-memory search, audit and writes."""
    def __init__(self, _dsn=""):
        self.db = SimpleNamespace(commit=lambda: None)
        self.evidence = EVIDENCE

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def bootstrap(self):
        pass

    def one(self, query, _params=()):
        if "pg_try_advisory_xact_lock" in query:
            return {"locked": True}
        if "pg_advisory_xact_lock" in query:
            return None
        raise AssertionError(query)

    def search(self, _user, _question, _filter):
        return self.evidence

    def allowed_document_ids(self, _user):
        return ["doc-1"]

    def can_read_document(self, _user, document_id):
        return document_id == "doc-1"

    def run(self, *_args):
        pass

    def audit(self, *_args):
        pass


@pytest.fixture
def api_client(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("OPENAI_MODEL", "local-model")
    monkeypatch.setattr(deps, "Workspace", MemoryWorkspace)
    monkeypatch.setattr(deps, "initialized", False)
    with TestClient(main.app, base_url="http://localhost:5173") as client:
        yield client


def ask(client):
    health = client.get("/api/health").json()
    response = client.post("/api/ask", headers={"X-Haedap-Token": health["csrfToken"]},
                           json={"question": "원문 근거", "task": "documents", "mode": "llm"})
    assert response.status_code == 200
    return health, response.json()


def assert_fallback(result):
    assert result["generation"] == "extractive"
    assert result["warnings"] == ["MODEL_FAILED_EXTRACTIVE_FALLBACK"]
    assert result["statements"][0]["text"] == EVIDENCE[0]["text"]


def test_health_and_real_answer_flow_enable_keyless_server(api_client, model_server):
    calls = model_server(completion())
    health, result = ask(api_client)
    assert health["llmConfigured"] is True
    assert result["generation"] == "llm" and result["warnings"] == []
    assert result["statements"] == [STATEMENT]
    assert len(calls) == 1  # health does not contact the model.


@pytest.mark.parametrize("environment", [
    {"OPENAI_MODEL": ""}, {"OPENAI_BASE_URL": "https://api.openai.com/v1"},
    {"OPENAI_BASE_URL": "https://"}, {"OPENAI_RESPONSE_FORMAT": "unsupported"},
])
def test_health_and_answer_share_disabled_configuration(monkeypatch, api_client, model_server, environment):
    for name, value in environment.items():
        monkeypatch.setenv(name, value)
    calls = model_server(completion())
    health, result = ask(api_client)
    assert health["llmConfigured"] is False
    assert result["generation"] == "extractive"
    assert result["warnings"] == ["MODEL_NOT_CONFIGURED"]
    assert calls == []


@pytest.mark.parametrize("payload", [
    None, [], {}, {"choices": None}, {"choices": []}, {"choices": [None]},
    {"choices": [{"finish_reason": "stop", "message": None}]},
    completion(content=None), completion(content=[]), completion(content=""),
    completion(content="not JSON"), completion(content="```json\n{}\n```"),
    completion(finish_reason="length"), completion(finish_reason="content_filter"),
    completion(finish_reason="tool_calls"), completion(refusal="refused"),
    completion(tool_calls=[{}]), completion(function_call={"name": "unexpected"}),
    completion(answer=[]), completion(answer={"insufficient": "false", "statements": []}),
    completion(answer={"insufficient": False, "statements": []}),
    completion(answer={"insufficient": False, "statements": [None]}),
    completion(answer={"insufficient": False, "statements": [STATEMENT] * 6}),
    completion(answer={"insufficient": True, "statements": [STATEMENT]}),
    completion(answer={"insufficient": False, "statements": [{**STATEMENT, "chunkId": []}]}),
    completion(answer={"insufficient": False, "statements": [{**STATEMENT, "chunkId": "hidden-chunk"}]}),
    completion(answer={"insufficient": False, "statements": [{**STATEMENT, "quote": "원문에 없는 인용 문장입니다."}]}),
    completion(answer={"insufficient": False, "statements": [{**STATEMENT, "quote": "짧음"}]}),
    completion(answer={"insufficient": False, "statements": [{**STATEMENT, "text": " "}]}),
])
def test_malformed_or_untrusted_model_output_falls_back_without_500(api_client, model_server, payload):
    model_server(payload)
    _, result = ask(api_client)
    assert_fallback(result)


@pytest.mark.parametrize("status", [302, 400, 401, 403, 404, 429, 500, 503])
def test_upstream_http_errors_do_not_escape_or_retry(api_client, model_server, status):
    calls = model_server({"error": "private upstream details"}, status=status)
    _, result = ask(api_client)
    assert_fallback(result)
    assert "private upstream details" not in json.dumps(result)
    assert len(calls) == 1


@pytest.mark.parametrize("error", [httpx.ConnectError, httpx.ReadTimeout])
def test_model_network_failures_fall_back(api_client, model_server, error):
    calls = model_server(error=error)
    _, result = ask(api_client)
    assert_fallback(result)
    assert len(calls) == 1


def test_non_json_http_body_falls_back(api_client, model_server):
    model_server(raw=b"<html>not a completion</html>")
    _, result = ask(api_client)
    assert_fallback(result)


def test_insufficient_evidence_is_not_a_failed_model_call(api_client, model_server):
    model_server(completion({"insufficient": True, "statements": []}))
    _, result = ask(api_client)
    assert result["generation"] == "llm" and result["statements"] == []
    assert result["status"] == "insufficient_evidence" and result["warnings"] == []


@pytest.mark.parametrize("mode,has_evidence", [("extractive", True), ("llm", False)])
def test_extractive_or_no_evidence_does_not_contact_model(monkeypatch, model_server, mode, has_evidence):
    monkeypatch.setenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("OPENAI_MODEL", "local-model")
    calls = model_server(completion())
    db = MemoryWorkspace()
    db.evidence = EVIDENCE if has_evidence else []
    result = db.answer({"id": "guest-test"}, {"question": "원문 근거", "task": "documents", "mode": mode})
    assert result["generation"] == "extractive"
    assert calls == []
