# Local Workspace MCP & REST Server for GPT (with Ngrok & Ponytail)

Hệ thống Local Server tích hợp **Model Context Protocol (MCP)** và **OpenAPI REST API**, kết nối trực tiếp vào thư mục làm việc cục bộ trên máy tính của bạn, mở tunnel ra internet bảo mật qua **Ngrok (HTTPS)** và nhúng triết lý **Ponytail** (Lazy Senior Developer) giúp **ChatGPT** hoặc **Claude** lập trình, đọc/ghi tệp, tìm kiếm và thực thi lệnh hoàn chỉnh.

---

## 🌟 Tính năng nổi bật

1. **Kết nối trực tiếp vào thư mục (Workspace)**:
   - Liệt kê cây thư mục (list_directory).
   - Đọc nội dung tệp với hỗ trợ cắt dòng (ead_file).
   - Tạo mới hoặc ghi đè tệp (write_file).
   - Chỉnh sửa/thay thế đoạn mã chính xác (edit_file).
   - Xóa tệp hoặc thư mục an toàn (delete_file).
   - Tìm kiếm nội dung grep và tìm tên tệp (search_files).
   - Thực thi lệnh PowerShell terminal trực tiếp (execute_command) - có thể bật/tắt an toàn.
   - Kiểm tra thông tin môi trường và dung lượng ổ đĩa (get_workspace_info).

2. **Tích hợp toàn diện dietrichgebert/ponytail**:
   - Nhúng triết lý *"The best code is the code never written"* (YAGNI, ưu tiên thư viện chuẩn, code ngắn nhất, tránh over-engineering).
   - Tích hợp công cụ ponytail_instructions và kiểm toán code ponytail_audit.
   - Cung cấp MCP Prompt ponytail để GPT ngay lập tức vào vai Lazy Senior Dev.
   - Bao gồm toàn bộ mã nguồn, npm packages và bộ skill gốc của Ponytail trong thư mục ponytail/.

3. **Hỗ trợ 2 phương thức kết nối linh hoạt cho GPT**:
   - **ChatGPT Developer Mode (MCP Connector)**: Kết nối qua giao thức MCP chuẩn tại endpoint /sse hoặc /mcp.
   - **Custom GPT (GPT Actions)**: Nhập trực tiếp schema OpenAPI tại /openapi.json để Custom GPT trên ChatGPT Web gọi các API REST.

4. **Tích hợp Ngrok 1-Click**:
   - Tự động mở tunnel HTTPS ra ngoài internet khi khởi chạy.
   - Hiển thị đầy đủ các đường dẫn cấu hình trực quan ngay trên màn hình console.

---

## 📁 Cấu trúc thư mục

`
adventurous-faraday/
├── ponytail/               # Mã nguồn repo Ponytail nguyên bản (đã cài đặt npm packages)
│   ├── ponytail-mcp/       # MCP server Node.js gốc của Ponytail
│   ├── skills/             # Các skill Ponytail (ponytail, review, audit, debt...)
│   └── hooks/              # Logic tạo instructions theo mode
├── mcp_server/
│   ├── __init__.py
│   ├── config.py           # Quản lý cấu hình từ file .env
│   ├── workspace_tools.py  # Các hàm thao tác tệp & chạy lệnh PowerShell an toàn
│   ├── ponytail_tools.py   # Bộ công cụ Ponytail (instructions, audit, prompt)
│   ├── server.py           # FastAPI + MCP server (hỗ trợ SSE, Streamable HTTP, REST)
│   └── tunnel.py           # Quản lý ngrok tunnel tự động qua pyngrok
├── .env                    # File cấu hình thực tế (tạo từ .env.example)
├── .env.example            # Mẫu cấu hình
├── requirements.txt        # Thư viện Python cần thiết
├── run.py                  # Điểm khởi động chính của server
├── run.bat                 # Script chạy nhanh trên Windows (CMD)
├── run.ps1                 # Script chạy trên Windows PowerShell
└── README.md               # Hướng dẫn chi tiết này
`

---

## 🚀 Hướng dẫn cài đặt & Khởi động nhanh

### Bước 1: Cấu hình file .env
Mở file .env và điền các thông tin sau:
`env
# 1. Thư mục mà bạn muốn GPT thao tác (mặc định là thư mục hiện tại)
WORKSPACE_DIR=c:/Users/admin/Documents/antigravity/adventurous-faraday

# 2. Điền Ngrok Authtoken (Lấy miễn phí tại: https://dashboard.ngrok.com/get-started/your-authtoken)
NGROK_AUTHTOKEN=your_ngrok_token_here

# 3. Cổng chạy server
PORT=8000

# 4. Cho phép chạy lệnh PowerShell (true/false)
ENABLE_COMMAND_EXECUTION=true

# 5. Chế độ Ponytail: lite | full | ultra
PONYTAIL_MODE=full
`

> **Lưu ý về Ngrok Authtoken**: Bạn chỉ cần đăng ký tài khoản miễn phí tại [ngrok.com](https://ngrok.com) và sao chép Authtoken dán vào biến NGROK_AUTHTOKEN.

### Bước 2: Khởi động Server
Bạn có thể khởi động theo một trong các cách sau:

- **Cách 1 (Khuyên dùng trên Windows)**: Nhấp đúp vào file un.bat
- **Cách 2 (PowerShell)**:
  `powershell
  .\run.ps1
  `
- **Cách 3 (Dòng lệnh Python)**:
  `ash
  python run.py
  `
  *(Nếu muốn chạy nội bộ không bật ngrok, thêm tham số: python run.py --no-ngrok)*

Sau khi khởi chạy thành công, console sẽ hiển thị bảng thông tin:
`	ext
========================================================================
   LOCAL MCP & REST SERVER FOR GPT WITH NGROK & PONYTAIL
========================================================================
 Thu muc lam viec (Workspace): C:\Users\admin\Documents\antigravity\adventurous-faraday
 Che do Ponytail (Intensity) : full
 Cong noi bo (Local Port)   : 8000
 Quyen chay PowerShell      : BAT (Enabled)
------------------------------------------------------------------------
 Public Ngrok Base URL: https://abc123.ngrok-free.app

 [1] CAU HINH CHATGPT DEVELOPER MODE (MCP CONNECTOR):
     - MCP Endpoint (SSE):  https://abc123.ngrok-free.app/sse
     - MCP Streamable HTTP: https://abc123.ngrok-free.app/mcp

 [2] CAU HINH CUSTOM GPT (ACTIONS / OPENAPI):
     - OpenAPI Schema URL:  https://abc123.ngrok-free.app/openapi.json
     - API Docs (Swagger):  https://abc123.ngrok-free.app/docs
     - Health Check:        https://abc123.ngrok-free.app/health
========================================================================
`

---

## 🤖 Hướng dẫn kết nối với GPT

### Cách 1: Kết nối qua ChatGPT Developer Mode (MCP Connector)
*(Dành cho tài khoản ChatGPT Plus / Pro / Team có bật Developer Mode)*
1. Mở **ChatGPT** trên trình duyệt, vào **Settings** -> **Security & login** (hoặc **Connectors**).
2. Bật tính năng **Developer mode**.
3. Chọn **Add Connector** (hoặc biểu tượng +).
4. Nhập URL MCP: https://<dia-chi-ngrok>.ngrok-free.app/sse (hoặc /mcp).
5. Đặt tên connector (ví dụ: Local Workspace Ponytail).
6. Trong cuộc trò chuyện mới, kích hoạt connector này. Bây giờ ChatGPT có thể gọi trực tiếp các tool list_directory, ead_file, write_file, execute_command, ponytail_instructions...

---

### Cách 2: Kết nối qua Custom GPT (GPT Actions / OpenAPI)
*(Dành cho bất kỳ ai muốn tạo 1 con Custom GPT riêng phục vụ dự án)*
1. Truy cập **ChatGPT** -> **Explore GPTs** -> chọn **Create** (Tạo GPT mới).
2. Chuyển sang tab **Configure**:
   - **Name**: Local Senior Dev Assistant
   - **Description**: Hỗ trợ lập trình trực tiếp vào thư mục máy tính với tư duy Ponytail
   - **Instructions**: Dán đoạn prompt sau vào:
     `	ext
     You are a Senior Software Developer assisting with a local codebase.
     You adopt the "Ponytail" mindset: the best code is the code never written. 
     Follow the decision ladder: YAGNI -> Reuse existing code -> Standard library first -> Smallest correct change.
     You have access to local workspace tools via Actions. Always list or read existing files before writing code.
     Keep responses concise and prioritize minimal, robust, working code.
     `
3. Kéo xuống mục **Actions** -> Chọn **Create new action**.
4. Ở ô **Schema**, nhấp vào nút **Import from URL** và dán:
   https://<dia-chi-ngrok>.ngrok-free.app/openapi.json
5. ChatGPT sẽ tự động đọc schema và nhận diện toàn bộ 11 endpoints thao tác tệp và chạy terminal!
6. Bấm **Save** / **Update**. Bạn đã có thể chat và yêu cầu GPT đọc code, tạo file, chỉnh sửa mã và chạy test ngay trên máy của bạn!

---

## 🔒 Cơ chế bảo mật

1. **Chống Path Traversal (Bảo vệ ngoài thư mục)**:
   Mọi đường dẫn tệp tin đều được hàm esolve_safe_path kiểm tra bắt buộc phải nằm bên trong thư mục WORKSPACE_DIR. Mọi nỗ lực truy cập ../../ ra ngoài ổ đĩa hệ thống sẽ bị từ chối ngay lập tức.
2. **Quyền chạy lệnh PowerShell**:
   Mặc định cho phép chạy lệnh. Nếu bạn muốn vô hiệu hóa tính năng chạy terminal vì lý do an toàn, chỉ cần đổi ENABLE_COMMAND_EXECUTION=false trong file .env.
3. **API Key bảo vệ Ngrok (Tùy chọn)**:
   Nếu bạn muốn ngăn người lạ gọi vào tunnel ngrok, hãy điền API_KEY=mat_khau_cua_ban trong .env. Khi đó các request phải có header X-API-Key hoặc Authorization: Bearer <token>.

---

## 🐴 Về triết lý Ponytail

Dự án này tích hợp triết lý **Ponytail** (dietrichgebert/ponytail):
- **Thang quyết định (Decision Ladder)**:
  1. *Có thực sự cần xây dựng tính năng này không? (YAGNI)*
  2. *Mã nguồn hiện tại đã có chưa? Hãy tái sử dụng, không viết lại.*
  3. *Thư viện chuẩn (Standard Library) có hỗ trợ không? Hãy dùng nó.*
  4. *Tính năng nền tảng (Native platform) có sẵn không? Dùng nó.*
  5. *Thư viện đã cài sẵn có giải quyết được không? Dùng nó.*
  6. *Có thể viết trong 1 dòng không? Hãy làm 1 dòng.*
  7. *Chỉ khi không còn cách nào khác: viết lượng mã tối thiểu để hoạt động.*
- **Các cấp độ (Modes)**:
  - lite: Giữ nguyên tính năng, giảm bớt boilerplate và trừu tượng hóa không cần thiết.
  - ull: Cân bằng giữa tối giản và chất lượng sản phẩm (Khuyên dùng).
  - ultra: Cực kỳ tối giản, chỉ viết code cốt lõi tuyệt đối.
