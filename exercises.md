# Phiếu Phản Ánh — K4 Level 3A, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay dòng trả lời mẫu bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Đỗ Quốc An Mã học viên: 2A202602892
---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> Nếu quên set AGENT_API_KEY trên cloud mà ứng dụng vẫn dùng khóa mặc định "changeme", service sẽ khởi động và người ngoài có thể đoán khóa để gọi API. Khi agent_api_key không có mặc định, deployment báo ValidationError ngay lúc khởi động. Tôi phát hiện lỗi trong log trước khi service nhận traffic và phát sinh chi phí.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

> Một dòng log JSON tôi thu được là: `{"event": "ask_completed", "level": "info", "timestamp": "2026-09-28T09:57:54.857819+00:00", "user_id": "cp5-test", "tokens_in": 1, "tokens_out": 35, "cost_usd": 2.115e-05}`. Từ dòng log này, tôi có thể lọc và đếm số sự kiện `ask_completed` theo `user_id` hoặc theo khoảng thời gian. Tôi cũng có thể tổng hợp `tokens_in`, `tokens_out` và `cost_usd` để theo dõi chi phí hoặc tạo cảnh báo. Dòng `print("đã trả lời xong")` không chứa các trường có cấu trúc để làm hai việc đó.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | 1728 MB |
| Multi-stage | 271 MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

> Phần chênh lệch khoảng 1457 MB chủ yếu do bản một stage dùng image `python:3.11` đầy đủ và giữ toàn bộ nội dung phục vụ quá trình build trong image cuối. Bản multi-stage dùng `python:3.11-slim`; stage builder chỉ cài dependency rồi chép kết quả từ `/install` sang runtime, vì vậy các thành phần build và phần dư không cần thiết không nằm trong image chạy thật.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> Khi tôi chỉ sửa `app/main.py`, các layer của stage builder như `COPY requirements.txt` và `RUN pip install` vẫn được lấy từ cache vì `requirements.txt` không đổi. Các layer runtime trước `COPY app ./app` cũng được dùng lại; từ `COPY app ./app` trở đi bị ảnh hưởng và `RUN chown` phải chạy lại. Nếu đặt `COPY . .` trước `RUN pip install`, mỗi thay đổi nhỏ trong source code đều làm layer `COPY` đổi, khiến layer cài toàn bộ thư viện và các layer sau nó phải chạy lại nên quá trình build lâu hơn nhiều.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> Nếu code Python có lỗ hổng thực thi lệnh từ xa, kẻ tấn công có thể chạy lệnh với quyền của process trong container. Khi process chạy bằng root, họ có quyền root bên trong container; nếu container còn được cấp capability mạnh, mount Docker socket hoặc container runtime có lỗ hổng, họ có thể thoát container và giành quyền cao trên host. Lệnh `USER appuser` cắt chuỗi này ngay sau bước chiếm process: mã độc chỉ chạy với UID 10001 và bị hạn chế quyền đọc, ghi cũng như thao tác hệ thống. Đây là biện pháp giảm thiểu thiệt hại, dù vẫn phải cấu hình container an toàn để chống container escape.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

> Người dùng có thể gửi tối đa 20 request trong 2 giây liên tiếp. Họ gửi 10 request ngay trước khi phút cũ kết thúc, ví dụ lúc `10:00:59`, rồi gửi tiếp 10 request ngay sau khi bộ đếm reset, ví dụ lúc `10:01:00`. Mỗi phút đồng hồ vẫn chỉ ghi nhận 10 request nhưng thực tế 20 request đã đi qua trong khoảng 2 giây. Sliding window 60 giây loại bỏ khe hở tại ranh giới này.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

> Rate limit giới hạn số request trong cửa sổ 60 giây, còn cost guard giới hạn tổng chi phí của từng user trong cả tháng. Trường hợp rate limit cho qua nhưng cost guard phải chặn là request đầu tiên trong phút mới của một user đã tiêu hết ngân sách tháng. Trường hợp ngược lại là user vẫn còn ngân sách nhưng gửi request thứ 11 trong vòng 60 giây khi hạn mức là 10; cost guard vẫn cho phép về mặt chi phí nhưng rate limit phải trả HTTP 429.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> Nếu gộp `/health` và `/ready` rồi cho endpoint đó kiểm tra Redis, khi Redis mất kết nối thì cả 3 container đều trả lỗi cho probe. Orchestrator đánh dấu chúng không khỏe, loại chúng khỏi traffic và nếu probe đó được dùng làm liveness thì lần lượt restart cả 3 container. Các container khởi động lại khi Redis vẫn chưa phục hồi nên tiếp tục fail probe và bị restart, tạo thành vòng lặp restart dù process FastAPI không hỏng. Khi tách hai endpoint, `/ready` trả 503 để ngừng nhận traffic, còn `/health` vẫn trả 200 để container không bị restart vô ích và có thể sẵn sàng lại ngay khi Redis phục hồi.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> Khi dùng Redis chung, tôi thấy `history_length` tăng đều theo các lần gọi, ví dụ `0`, `2`, `4`, vì mỗi request thêm một message của user và một message của assistant, bất kể request được chuyển đến container nào. Nếu lưu lịch sử trong dict Python, mỗi container có một dict riêng nên số liệu phụ thuộc container nhận request, có thể dao động như `0`, `0`, `2`, `0`, `2`, `4` thay vì tăng liên tục; lịch sử còn mất hoàn toàn khi container bị restart.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> Lỗi tôi gặp khi deploy Railway là `/health` trả HTTP 200 nhưng `/ready` và request `/ask` có API key đều trả `500 Internal Server Error`; Deploy Logs ghi `Exception in ASGI application`. Tôi kiểm tra các biến của hai service và phát hiện `REDIS_URL` của `day12-agent` đang tham chiếu `${{day12-redis.DATABASE_URL}}`, trong khi service Redis chỉ cung cấp biến `REDIS_URL`. Tôi sửa tham chiếu thành `${{day12-redis.REDIS_URL}}` và để Railway redeploy. Sau đó `/ready` trả `{"status":"ready","redis":true}`, `/ask` hoạt động và các test CP5 gọi service công khai đã vượt qua.
