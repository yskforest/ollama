#!/usr/bin/env python3
"""
Ollama API リバースプロキシ（think パラメータ自動注入）

GitHub Copilot Chat など、リクエスト時に Ollama の `think` オプションを
指定できないクライアント向けに、/api/chat および /api/generate の
JSON ペイロードへ `think` を自動付与して本体の Ollama へ中継する。
"""

import http.client
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

UPSTREAM_URL = os.environ.get("OLLAMA_UPSTREAM_URL", "http://ollama:11434")
LISTEN_HOST = os.environ.get("PROXY_HOST", "0.0.0.0")
LISTEN_PORT = int(os.environ.get("PROXY_PORT", "11435"))
THINK_MODE_RAW = os.environ.get("THINK_MODE", "false").strip()
# カンマ区切りで対象モデルを指定（空の場合は全モデルに適用）
TARGET_MODELS = {
    m.strip() for m in os.environ.get("TARGET_MODELS", "").split(",") if m.strip()
}

_parsed_upstream = urlparse(UPSTREAM_URL)
UPSTREAM_HOST = _parsed_upstream.hostname or "ollama"
UPSTREAM_PORT = _parsed_upstream.port or 11434

INJECT_PATHS = {"/api/chat", "/api/generate"}
HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
}


def parse_think_value(raw: str):
    """環境変数の文字列を Ollama API の think 値（bool または str）へ変換する。"""
    lowered = raw.lower()
    if lowered == "false":
        return False
    if lowered == "true":
        return True
    return raw


THINK_VALUE = parse_think_value(THINK_MODE_RAW)


class OllamaProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        print(f"[proxy] {self.address_string()} - {format % args}", flush=True)

    def _maybe_inject_think(self, path: str, body: bytes) -> bytes:
        clean_path = urlparse(path).path
        if clean_path not in INJECT_PATHS or not body:
            return body
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return body

        if not isinstance(payload, dict):
            return body

        model_name = payload.get("model", "")
        if TARGET_MODELS and model_name not in TARGET_MODELS:
            return body

        # クライアントが明示指定していない場合のみデフォルトの think 値を付与する
        payload.setdefault("think", THINK_VALUE)
        return json.dumps(payload, ensure_ascii=False).encode("utf-8")

    def _forward(self):
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        req_body = self.rfile.read(content_length) if content_length > 0 else b""
        req_body = self._maybe_inject_think(self.path, req_body)

        forward_headers = {
            k: v
            for k, v in self.headers.items()
            if k.lower() not in HOP_BY_HOP_HEADERS and k.lower() != "content-length"
        }
        if req_body:
            forward_headers["Content-Length"] = str(len(req_body))

        conn = http.client.HTTPConnection(UPSTREAM_HOST, UPSTREAM_PORT, timeout=900)
        headers_sent = False
        try:
            conn.request(self.command, self.path, body=req_body or None, headers=forward_headers)
            resp = conn.getresponse()

            self.send_response(resp.status, resp.reason)
            is_chunked = False
            has_content_length = False

            for k, v in resp.getheaders():
                lk = k.lower()
                if lk == "transfer-encoding" and "chunked" in v.lower():
                    is_chunked = True
                    continue
                if lk in HOP_BY_HOP_HEADERS:
                    continue
                if lk == "content-length":
                    has_content_length = True
                self.send_header(k, v)

            no_body = self.command == "HEAD" or resp.status in (204, 304) or 100 <= resp.status < 200

            if no_body:
                self.end_headers()
                headers_sent = True
                resp.read()
            elif is_chunked or not has_content_length:
                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()
                headers_sent = True
                while True:
                    # read1() でバッファリングを最小化し、到着したチャンクを即座に転送する
                    chunk = resp.read1(8192)
                    if not chunk:
                        break
                    self.wfile.write(f"{len(chunk):x}\r\n".encode("ascii"))
                    self.wfile.write(chunk)
                    self.wfile.write(b"\r\n")
                    self.wfile.flush()
                self.wfile.write(b"0\r\n\r\n")
                self.wfile.flush()
            else:
                self.end_headers()
                headers_sent = True
                data = resp.read()
                if data:
                    self.wfile.write(data)
                self.wfile.flush()
        except Exception as exc:
            if not headers_sent:
                self.send_error(502, f"Upstream Ollama error: {exc}")
            else:
                self.log_message("stream interrupted: %s", exc)
        finally:
            conn.close()

    def do_GET(self):
        self._forward()

    def do_HEAD(self):
        self._forward()

    def do_POST(self):
        self._forward()

    def do_PUT(self):
        self._forward()

    def do_DELETE(self):
        self._forward()

    def do_OPTIONS(self):
        self._forward()


def main():
    print(
        f"[proxy] Listening on {LISTEN_HOST}:{LISTEN_PORT} -> {UPSTREAM_URL} (THINK_MODE={THINK_VALUE!r})",
        flush=True,
    )
    server = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), OllamaProxyHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
