# BÁO CÁO KẾT QUẢ BÀI LAB — DAY 26: MCP TOOLS INTEGRATION

**Học viên:** Vũ Ngọc Thiện - 2A202601793
**Chủ đề:** Model Context Protocol (MCP) & Function Calling Integration  

---

## 1. TỔNG QUAN VÀ SO SÁNH KIẾN THỨC CỐT LÕI

### 1.1. Function Calling vs Model Context Protocol (MCP)

| Tiêu chí | Function Calling thuần | Model Context Protocol (MCP) |
|---|---|---|
| **Bản chất** | Tính năng của mô hình LLM (*Model Capability*) | Giao thức truyền thông mở chuẩn hóa (*Protocol*) |
| **Định nghĩa Tool** | Viết schema thủ công trong từng app (bằng code Python/JSON) | Server tự công bố (*self-describing*) qua decorators `@mcp.tool()` |
| **Khám phá Tool** | Hard-code danh sách tool lúc gọi prompt | Dynamic discovery tại runtime thông qua `list_tools()` |
| **Môi trường thực thi** | App client tự chạy hàm Python | MCP Server độc lập thực thi, client chỉ điều phối |
| **Khả năng tái sử dụng** | Kém (phải copy code và schema sang từng dự án) | Cao (viết 1 server, mọi AI Client/ADK/Claude dùng chung) |
| **Tầng giao tiếp** | Nội bộ trong app | Hỗ trợ cả **stdio** (local) và **Streamable HTTP/SSE** (remote/cloud) |

### 1.2. Mối quan hệ giữa Function Calling và MCP
> **MCP không thay thế Function Calling mà sử dụng Function Calling làm nền tảng bên dưới.**  
> LLM sử dụng cơ chế Function Calling để quyết định gọi tool nào, sau đó MCP Client đóng vai trò cầu nối gửi request thực thi sang MCP Server qua giao thức mạng chuẩn.

---

## 2. KẾT QUẢ TRIỂN KHAI CÁC MODULE

### Module 01: Function Calling thuần (`01-function-calling`)
- **Mô tả:** Khai báo thủ công schema `get_weather` với `types.FunctionDeclaration`, điều phối vòng lặp `while resp.function_calls` và tự thực thi hàm mock.
- **Trạng thái:** Hoàn thiện và hỗ trợ nạp biến môi trường tự động.

### Module 02: MCP Cơ bản qua stdio (`02-mcp-basics`)
- **Mô tả:** Khởi tạo FastMCP Server `weather_server.py` và Client `weather_client.py` kết nối tự động qua luồng `stdio_client`.
- **Kết quả kiểm thử:**
  - Khám phá thành công tool: `get_weather: Lấy thời tiết hiện tại của một thành phố.`
  - Gọi tool thành công với Hanoi, Danang, Haiphong.
  - **Trạng thái:**  `PASSED (Exit code: 0)`

### Module 03: MCP trong Production (`03-production`)
Bao gồm 3 trụ cột kỹ thuật cho hệ thống thực tế:
1. **Authentication (`auth_server.py` & `auth_client.py`):**
   - Xác thực client qua HTTP Bearer Token với `TokenVerifier` và `AuthSettings`.
2. **Tool Registry & Discovery (`registry.json` & `registry_client.py`):**
   - Agent tra cứu danh mục tool tập trung theo `tag` (ví dụ: `weather`) và `keyword` (ví dụ: `forecast`), tự động chọn bản match tốt nhất (`get_weather_v2 v2.0.0`) và kết nối runtime.
   - **Trạng thái:**  `PASSED (Exit code: 0)`
3. **Versioning & Backward Compatibility (`versioned_server.py` & `versioned_client.py`):**
   - Chạy song song tool v1 (legacy) và tool v2 (bổ sung forecast, đơn vị đo), đồng thời công bố metadata qua resource URI `server://info`.
   - **Trạng thái:**  `PASSED (Exit code: 0)`

---

## 3. BÀI THỰC HÀNH CHÍNH (LAB 04: WEATHER AGENT VỚI GOOGLE ADK & REMOTE MCP SERVER)

### 3.1. Kiến trúc hệ thống
```
┌─────────────────────────┐      Streamable HTTP        ┌─────────────────────────┐       REST API      ┌─────────────────────────┐
│     Google ADK Agent    │ ──────────────────────────> │    FastMCP Server       │ ──────────────────> │      WeatherAPI.com     │
│ (mcp-client: port 8000) │ <── list_tools / call ────  │ (mcp-server: port 8085) │                     │   (Live Weather Data)   │
└─────────────────────────┘                             └─────────────────────────┘                     └─────────────────────────┘
```

### 3.2. Kiểm thử FastMCP Server & WeatherAPI thực tế
- **API Key WeatherAPI:** Đã cấu hình và kiểm thử thành công.
- **Kết quả dữ liệu thật thu được từ server:**
  - **Địa điểm:** Hanoi, Vietnam
  - **Nhiệt độ:** 34.4°C (Feels like: 41.9°C), Tình trạng: Sunny, Độ ẩm: 57%, Gió: 6.8 km/h.
  - **Trạng thái:**  `PASSED (Dữ liệu trả về chuẩn xác theo thời gian thực)`

### 3.3. Kết quả Verification (`verify_setup.py`)
- Environment Config: ✅ `Passed`
- Dependencies Check: ✅ `Passed (Google ADK, FastMCP, MCP, httpx, dotenv)`
- Agent Structure: ✅ `Passed`
- MCP Server Connectivity: ✅ `Passed (Reachable at http://localhost:8085/mcp)`
- Agent Import: ✅ `Passed (Model: gemini-3.5-flash-lite)`

---

## 4. HƯỚNG DẪN CHẠY VÀ DEMO TƯƠNG TÁC

1. **Khởi động MCP Server (Terminal 1):**
   ```powershell
   cd 04-lab/mcp-server
   python weather.py
   ```
2. **Khởi động Giao diện Web ADK (Terminal 2):**
   ```powershell
   cd 04-lab/mcp-client
   adk web
   ```
3. **Mở trình duyệt:** Truy cập `http://localhost:8000`, chọn `weather_agent` và chat hỏi thời tiết!

---

## 5. HÌNH ẢNH MINH CHỨNG NGHIỆM THU (DEMO ARTIFACTS)

### 5.1. Giao diện Chat Web ADK với Weather Agent
![Web ADK Chat Demo](Screenshot%202026-08-28%20165139.png)

### 5.2. Luồng thực thi Function Calling qua FastMCP Server
![Tool Execution Details](Screenshot%202026-08-28%20165149.png)

> **Nhận xét:** Thể hiện đầy đủ luồng: User hỏi ngôn ngữ tự nhiên → Gemini phân tích và kích hoạt `McpToolset` qua Streamable HTTP tới FastMCP Server (Port 8085) → Server lấy dữ liệu thời tiết thực tế từ WeatherAPI → Tổng hợp câu trả lời chi tiết kèm lời khuyên thực tế cho người dùng.


