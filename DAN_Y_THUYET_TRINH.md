# 📋 DÀN Ý THUYẾT TRÌNH DEMO
## Hệ thống Quản lý Tài chính Cá nhân Thông minh

---

## 🎯 PHẦN 1: GIỚI THIỆU TỔNG QUAN (5 phút)

### 1.1. Vấn đề thực tế
- **Vấn đề**: Người dùng gặp khó khăn trong việc quản lý tài chính cá nhân
  - Không theo dõi được thu chi một cách hệ thống
  - Khó kiểm soát ngân sách hàng tháng
  - Thiếu công cụ phân tích và dự đoán xu hướng chi tiêu
  - Không có cảnh báo tự động về tình trạng tài chính

### 1.2. Giải pháp đề xuất
- **Hệ thống Quản lý Tài chính Cá nhân Thông minh** tích hợp:
  - ✅ Quản lý giao dịch và ví tiền
  - ✅ Theo dõi ngân sách với cảnh báo tự động
  - ✅ Dashboard trực quan với BI (Business Intelligence)
  - ✅ AI Chatbot hỗ trợ truy vấn bằng ngôn ngữ tự nhiên
  - ✅ Tự động hóa cảnh báo và nhắc nhở

### 1.3. Đối tượng sử dụng
- Cá nhân muốn quản lý tài chính hiệu quả
- Gia đình cần theo dõi chi tiêu chung
- Người dùng muốn phân tích xu hướng tài chính

---

## 🏗️ PHẦN 2: KIẾN TRÚC HỆ THỐNG (5 phút)

### 2.1. Tech Stack
```
Frontend:     React 18 + Vite + Tailwind CSS
Backend:      FastAPI (Python) + SQLAlchemy
Database:     PostgreSQL 15
BI Tool:      Apache Superset
Automation:   n8n
AI Chatbot:   Dify Cloud (Gemini/GPT)
DevOps:       Docker Compose
```

### 2.2. Kiến trúc tổng thể
```
┌─────────────────┐
│   Frontend      │ React UI (Port 3000)
│   (React)       │
└────────┬────────┘
         │ REST API
┌────────▼────────┐
│   Backend       │ FastAPI (Port 8000)
│   (FastAPI)     │
└────────┬────────┘
         │
┌────────▼────────┐     ┌─────────────────┐
│   PostgreSQL    │◄────│  Apache         │
│   (Database)    │     │  Superset       │
└─────────────────┘     └─────────────────┘
         │
         │
┌────────▼────────┐     ┌─────────────────┐
│   n8n           │     │   Dify AI       │
│   (Automation)  │     │   (Chatbot)     │
└─────────────────┘     └─────────────────┘
```

### 2.3. Các service chính
- **Frontend**: Giao diện người dùng tiếng Việt
- **Backend API**: Xử lý logic nghiệp vụ, authentication
- **PostgreSQL**: Lưu trữ dữ liệu tài chính
- **Superset**: Phân tích dữ liệu và tạo dashboards BI
- **n8n**: Tự động hóa workflows (cảnh báo, nhắc nhở)
- **Dify**: AI Chatbot hỗ trợ truy vấn tài chính

---

## 💡 PHẦN 3: DEMO CÁC TÍNH NĂNG CHÍNH (15 phút)

### 3.1. Đăng nhập / Đăng ký ⭐
**DEMO:**
- Truy cập: `http://localhost:3000`
- Đăng nhập với tài khoản demo: `demo@finance.app` / `123456`
- **Điểm nổi bật**:
  - Xác thực JWT
  - Bảo mật mật khẩu với hash
  - Session management

### 3.2. Dashboard Tổng quan ⭐⭐⭐
**DEMO:**
- Hiển thị các KPI chính:
  - 💰 Tổng thu nhập tháng này
  - 💸 Tổng chi tiêu tháng này
  - 📊 Số dư hiện tại
  - 🎯 Tình trạng ngân sách

- **Biểu đồ trực quan**:
  - Line chart: Xu hướng thu chi theo thời gian
  - Pie chart: Phân bổ chi tiêu theo danh mục
  - Bar chart: So sánh ngân sách vs thực tế

**Câu nói demo:**
> "Dashboard này cung cấp cái nhìn tổng quan về tình hình tài chính, giúp người dùng nhanh chóng nắm bắt các chỉ số quan trọng."

### 3.3. Quản lý Giao dịch ⭐⭐
**DEMO:**
- **Thêm giao dịch mới**:
  - Thu nhập: Lương tháng 12
  - Chi tiêu: Mua sắm, Ăn uống, Đi lại
- **Lọc và tìm kiếm**:
  - Theo khoảng thời gian
  - Theo danh mục
  - Theo loại (Thu/Chi)
- **Xem lịch sử**: Bảng danh sách giao dịch với phân trang

**Câu nói demo:**
> "Hệ thống tự động cập nhật số dư ví khi thêm giao dịch, đảm bảo tính nhất quán của dữ liệu."

### 3.4. Quản lý Ví tiền ⭐
**DEMO:**
- Tạo nhiều ví: Tiền mặt, Ngân hàng, Ví điện tử
- Xem số dư từng ví
- Cập nhật thông tin ví
- **Đặc biệt**: Số dư tự động cập nhật theo giao dịch

### 3.5. Quản lý Ngân sách ⭐⭐
**DEMO:**
- **Đặt ngân sách theo danh mục**:
  - Ăn uống: 2,000,000 VND/tháng
  - Mua sắm: 1,500,000 VND/tháng
  - Giải trí: 1,000,000 VND/tháng

- **Theo dõi tình trạng**:
  - Thanh progress bar hiển thị % đã sử dụng
  - Màu sắc cảnh báo (xanh → vàng → đỏ)
  - Cảnh báo khi gần vượt ngân sách

**Câu nói demo:**
> "Hệ thống giúp người dùng kiểm soát chi tiêu hiệu quả với cảnh báo tự động khi gần vượt ngân sách."

### 3.6. Quản lý Danh mục ⭐
**DEMO:**
- Danh mục mặc định: Ăn uống, Mua sắm, Đi lại, Giải trí, Y tế
- Tạo danh mục tùy chỉnh: "Học phí", "Điện nước"
- Gán icon và màu sắc cho từng danh mục

---

## 🤖 PHẦN 4: AI CHATBOT - ĐIỂM NỔI BẬT (8 phút) ⭐⭐⭐⭐⭐

### 4.1. Giới thiệu
- **Tích hợp Dify Cloud** với model Gemini/GPT
- Hỗ trợ truy vấn bằng **tiếng Việt**
- Tự động truy vấn database để trả lời chính xác

### 4.2. DEMO Chatbot
**Mở Chatbot (icon chat ở góc dưới bên phải)**

**Câu hỏi demo tuần tự:**

1. **"Tổng chi tiêu tháng này là bao nhiêu?"**
   - Chatbot gọi API → Query database → Trả về số liệu
   - Format: "Tổng chi tiêu tháng này là 5,500,000 VND"

2. **"Thu nhập tháng này của tôi?"**
   - Hiển thị tổng thu nhập

3. **"Chi tiêu theo danh mục"**
   - Trả về breakdown theo danh mục với emoji

4. **"Kiểm tra ngân sách tháng này"**
   - Báo cáo tình trạng từng ngân sách

5. **"Số dư trong ví là bao nhiêu?"**
   - Liệt kê số dư các ví

6. **"Giao dịch gần đây"**
   - Hiển thị 5-10 giao dịch mới nhất

### 4.3. Cách hoạt động (nếu có thời gian)
```
User hỏi (Tiếng Việt)
    ↓
Frontend → Dify API
    ↓
Dify AI xử lý → Gọi HTTP Tool → Backend
    ↓
Backend query PostgreSQL
    ↓
Dify format câu trả lời → Trả về User
```

**Câu nói demo:**
> "Chatbot này sử dụng AI để hiểu ngôn ngữ tự nhiên, không cần nhớ câu lệnh phức tạp. Chỉ cần hỏi như đang nói chuyện với trợ lý."

---

## 📊 PHẦN 5: BI DASHBOARDS - SUPERSET (5 phút) ⭐⭐⭐⭐

### 5.1. Giới thiệu
- **Apache Superset**: Công cụ BI mã nguồn mở mạnh mẽ
- Phân tích dữ liệu nâng cao với nhiều loại biểu đồ
- Views được tối ưu cho hiệu suất

### 5.2. DEMO Superset
**Truy cập: `http://localhost:8088` (admin/admin)**

**Các Dashboard:**

1. **KPI Summary Dashboard**
   - Cards: Tổng thu, Tổng chi, Số dư, Tỷ lệ tiết kiệm
   - **Câu nói**: "Các chỉ số KPI quan trọng được tổng hợp từ database views"

2. **Monthly Cashflow Trend**
   - Line chart: Xu hướng thu chi 6-12 tháng
   - **Câu nói**: "Phân tích xu hướng giúp dự đoán tình hình tài chính"

3. **Category Breakdown**
   - Pie chart: Tỷ lệ chi tiêu theo danh mục
   - Table: Chi tiết từng danh mục

4. **Budget vs Actual**
   - Bar chart so sánh: Ngân sách đặt vs Chi tiêu thực tế
   - **Câu nói**: "Giúp đánh giá hiệu quả quản lý ngân sách"

5. **Savings Rate Gauge**
   - Gauge chart: Tỷ lệ tiết kiệm (%)
   - **Câu nói**: "Mục tiêu tiết kiệm được thể hiện trực quan"

### 5.3. Database Views
- `v_kpi_summary`: Tổng hợp KPI
- `v_monthly_cashflow`: Dòng tiền hàng tháng
- `v_category_breakdown`: Phân tích theo danh mục
- `v_budget_vs_actual`: So sánh ngân sách
- `v_savings_rate`: Tỷ lệ tiết kiệm

**Câu nói demo:**
> "Superset giúp chuyển đổi dữ liệu thô thành insights có giá trị, hỗ trợ ra quyết định tài chính tốt hơn."

---

## ⚡ PHẦN 6: TỰ ĐỘNG HÓA - n8n (5 phút) ⭐⭐⭐

### 6.1. Giới thiệu
- **n8n**: Công cụ automation workflow
- Tự động hóa các tác vụ lặp lại
- Cảnh báo và nhắc nhở thông minh

### 6.2. DEMO Workflows
**Truy cập: `http://localhost:5678` (admin/admin)**

#### Workflow 1: Monthly Bill Reminder
**Mô tả:**
- Trigger: Ngày 1 hàng tháng (Cron)
- Kiểm tra hóa đơn sắp đến hạn
- Gửi email nhắc nhở thanh toán

**DEMO:**
- Xem workflow trong n8n
- Giải thích các node: Cron → Query DB → Email
- Kiểm tra email trong MailHog: `http://localhost:8025`

#### Workflow 2: Budget Overrun Alert
**Mô tả:**
- Trigger: Hàng ngày 9:00 AM
- Kiểm tra ngân sách vượt quá 80%
- Gửi cảnh báo qua email

**DEMO:**
- Xem logic workflow
- Test bằng cách chạy workflow thủ công
- Hiển thị email cảnh báo

**Câu nói demo:**
> "Automation giúp người dùng không bỏ lỡ hóa đơn và luôn kiểm soát được tình trạng ngân sách."

---

## 🔐 PHẦN 7: BẢO MẬT & API (3 phút)

### 7.1. Authentication
- JWT (JSON Web Token)
- Mật khẩu được hash với bcrypt
- Protected routes trong frontend

### 7.2. API Documentation
**Truy cập: `http://localhost:8000/docs` (Swagger UI)**

- Hiển thị tất cả endpoints
- Test API trực tiếp từ Swagger
- **Câu nói**: "API được document đầy đủ, dễ dàng tích hợp với các ứng dụng khác"

### 7.3. Database Security
- Prepared statements (SQLAlchemy)
- Input validation (Pydantic)
- User isolation (mỗi user chỉ xem dữ liệu của mình)

---

## 📈 PHẦN 8: KẾT QUẢ & HƯỚNG PHÁT TRIỂN (4 phút)

### 8.1. Kết quả đạt được
✅ **Chức năng Core**:
- Quản lý giao dịch, ví, ngân sách
- Dashboard trực quan

✅ **Business Intelligence**:
- Tích hợp Superset
- Phân tích dữ liệu nâng cao
- BI Views được tối ưu

✅ **AI & Automation**:
- AI Chatbot với Dify
- Workflow tự động với n8n
- Cảnh báo thông minh

✅ **DevOps**:
- Docker Compose
- Dễ deploy và scale

### 8.2. Điểm mạnh
- 🎯 **Giao diện thân thiện**: Tiếng Việt, dễ sử dụng
- 🤖 **AI hỗ trợ**: Chatbot trả lời tự nhiên
- 📊 **Phân tích sâu**: BI dashboards chuyên nghiệp
- ⚡ **Tự động hóa**: Tiết kiệm thời gian quản lý

### 8.3. Hướng phát triển
- 📱 **Mobile App**: iOS/Android
- 🔗 **Tích hợp ngân hàng**: Auto import giao dịch
- 📈 **Dự đoán xu hướng**: Machine Learning
- 💬 **Thông báo real-time**: WebSocket
- 🌐 **Multi-currency**: Hỗ trợ nhiều loại tiền tệ
- 👥 **Chia sẻ ngân sách**: Quản lý tài chính gia đình

---

## ❓ PHẦN 9: Q&A (5 phút)

### Câu hỏi thường gặp:

**Q: Hệ thống có hỗ trợ nhiều người dùng không?**
A: Có, mỗi user có dữ liệu riêng biệt, được bảo mật bằng authentication.

**Q: Dữ liệu được lưu trữ ở đâu?**
A: PostgreSQL database, có thể backup và restore dễ dàng.

**Q: Chi phí vận hành?**
A: Có thể chạy trên máy local hoặc cloud. Dify có gói miễn phí, n8n và Superset là mã nguồn mở.

**Q: Có hỗ trợ import dữ liệu từ Excel không?**
A: Hiện tại chưa, nhưng có thể phát triển thêm.

**Q: AI Chatbot có chính xác không?**
A: Chatbot sử dụng model Gemini/GPT, kết hợp với query database nên độ chính xác cao.

---

## 📝 PHẦN 10: TỔNG KẾT (2 phút)

### Nhắc lại các điểm chính:
1. ✅ Hệ thống quản lý tài chính toàn diện
2. ✅ Tích hợp BI, AI, và Automation
3. ✅ Giao diện thân thiện, dễ sử dụng
4. ✅ Công nghệ hiện đại, dễ mở rộng

### Kết luận:
> "Hệ thống Quản lý Tài chính Cá nhân Thông minh không chỉ là một ứng dụng quản lý tài chính, mà là một giải pháp tích hợp BI, AI và Automation, giúp người dùng đưa ra quyết định tài chính thông minh hơn."

---

## 🎬 LƯU Ý KHI THUYẾT TRÌNH

### ⏰ Phân bổ thời gian (tổng ~45 phút):
- Phần 1-2: Giới thiệu + Kiến trúc (10 phút)
- Phần 3: Demo tính năng chính (15 phút) ⭐ **QUAN TRỌNG NHẤT**
- Phần 4: AI Chatbot (8 phút) ⭐ **ĐIỂM NỔI BẬT**
- Phần 5: BI Dashboards (5 phút)
- Phần 6: Automation (5 phút)
- Phần 7-8: API + Kết quả (7 phút)
- Phần 9-10: Q&A + Tổng kết (7 phút)

### 💡 Tips thuyết trình:
1. **Chuẩn bị trước**:
   - Test tất cả tính năng trước khi demo
   - Chuẩn bị dữ liệu demo phong phú
   - Backup database

2. **Khi demo**:
   - Nói rõ ràng, không vội vàng
   - Highlight các tính năng nổi bật
   - Giải thích cách hoạt động của từng phần
   - Xử lý lỗi một cách tự nhiên nếu có

3. **Tương tác**:
   - Đặt câu hỏi cho khán giả
   - Mời mọi người thử demo (nếu có thể)
   - Trả lời Q&A tự tin

4. **Điểm nhấn**:
   - AI Chatbot: Tính năng độc đáo nhất
   - BI Dashboards: Thể hiện kỹ năng phân tích
   - Automation: Giá trị thực tế

### 🛠️ Checklist trước khi thuyết trình:
- [ ] Tất cả services đã chạy (docker-compose up)
- [ ] Frontend accessible: http://localhost:3000
- [ ] Backend API: http://localhost:8000/docs
- [ ] Superset: http://localhost:8088
- [ ] n8n: http://localhost:5678
- [ ] Tài khoản demo hoạt động: demo@finance.app / 123456
- [ ] Dữ liệu demo đã được seed
- [ ] Chatbot đã cấu hình (nếu có Dify)
- [ ] Đã test tất cả workflows trong n8n
- [ ] Backup slides/script (nếu có)

---

**Chúc bạn thuyết trình thành công! 🎉**
