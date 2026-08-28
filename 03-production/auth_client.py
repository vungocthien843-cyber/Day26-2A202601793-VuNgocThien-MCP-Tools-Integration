"""MCP Client có Authentication — kết nối tới auth_server.py qua HTTP.

Client truyền bearer token thông qua httpx.AsyncClient. MCP SDK tự gắn
token vào mọi request HTTP (POST, GET, DELETE) tới server.

Cách chạy (cần auth_server.py đang chạy ở terminal khác):
    cd 03-production
    python auth_server.py            # terminal 1
    python auth_client.py            # terminal 2
"""

from __future__ import annotations

import asyncio
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import httpx

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

SERVER_URL = "http://localhost:8000/mcp"
VALID_TOKEN = "dev-token-abc123"
WRONG_TOKEN = "wrong-token-999"


async def test_with_token(token: str | None, label: str) -> None:
    print(f"\n--- Test: {label} ---")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    http_client = httpx.AsyncClient(headers=headers, timeout=5.0)

    try:
        async with http_client:
            async with streamable_http_client(SERVER_URL, http_client=http_client) as (
                read,
                write,
            ):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    print(f"✅ Kết nối thành công! Tools: {[t.name for t in tools.tools]}")
                    result = await session.call_tool("get_weather", {"city": "Hanoi"})
                    print(f"✅ Gọi tool thành công: {result.content[0].text}")
    except Exception as e:
        print(f"❌ Bị từ chối (như mong đợi): {type(e).__name__} - {e}")


async def main() -> None:
    print("==================================================")
    print("TEST BÀI TRUNG BÌNH: AUTHENTICATION QUA STREAMABLE HTTP")
    print("==================================================")
    # 1. Token hợp lệ
    await test_with_token(VALID_TOKEN, "1. Token HỢP LỆ (dev-token-abc123)")
    # 2. Thiếu token
    await test_with_token(None, "2. THIẾU TOKEN (Không truyền Authorization header)")
    # 3. Token sai
    await test_with_token(WRONG_TOKEN, "3. TOKEN SAI (wrong-token-999)")


if __name__ == "__main__":
    asyncio.run(main())
