#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : linghypshen@gmail.com
@File    : test_builtin_tool_handler.py
"""
import mimetypes
import os

import pytest
import yaml

from pkg.response import HttpCode

PROVIDERS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..",
    "internal", "core", "tools", "builtin_tools", "providers",
)


def _load_providers() -> list[dict]:
    with open(os.path.join(PROVIDERS_DIR, "providers.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


def _icon_path(provider: dict) -> str:
    return os.path.join(PROVIDERS_DIR, provider["name"], "_asset", provider["icon"])


class TestBuiltinToolHandler:
    """Test class for the built-in tool handler"""

    def test_get_categories(self, client):
        """Test retrieving all category information"""
        resp = client.get("/builtin-tools/categories")
        assert resp.status_code == 200
        assert resp.json.get("code") == HttpCode.SUCCESS
        assert len(resp.json.get("data")) > 0

    def test_get_builtin_tools(self, client):
        """Test retrieving all built-in tools"""
        resp = client.get("/builtin-tools")
        assert resp.status_code == 200
        assert resp.json.get("code") == HttpCode.SUCCESS
        assert len(resp.json.get("data")) > 0

    @pytest.mark.parametrize(
        "provider_name, tool_name",
        [
            ("google", "google_serper"),
            ("ling", "ling_llmops"),
        ]
    )
    def test_get_provider_tool(self, provider_name, tool_name, client):
        """Test API for retrieving specific tool information"""
        resp = client.get(f"/builtin-tools/{provider_name}/tools/{tool_name}")
        assert resp.status_code == 200
        if provider_name == "google":
            assert resp.json.get("code") == HttpCode.SUCCESS
            assert resp.json.get("data").get("name") == tool_name
        elif provider_name == "ling":
            assert resp.json.get("code") == HttpCode.NOT_FOUND

    @pytest.mark.parametrize("provider", _load_providers(), ids=lambda p: p["name"])
    def test_get_provider_icon(self, provider, app):
        """
        Every provider in providers.yaml serves its own icon file with the right MIME type.
        Icons load through <img> tags, which send no bearer token, so the request is anonymous.
        """
        with app.test_client() as anonymous:
            resp = anonymous.get(f"/builtin-tools/{provider['name']}/icon")
        assert resp.status_code == 200
        with open(_icon_path(provider), "rb") as f:
            assert resp.data == f.read()
        assert resp.mimetype == mimetypes.guess_type(provider["icon"])[0]

    def test_get_provider_icon_unknown_provider(self, client):
        """An unknown provider returns a not-found response instead of an image"""
        resp = client.get("/builtin-tools/ling/icon")
        assert resp.status_code == 200
        assert resp.json.get("code") == HttpCode.NOT_FOUND
