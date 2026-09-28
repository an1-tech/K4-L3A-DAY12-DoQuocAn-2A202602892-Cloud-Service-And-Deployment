# Thông Tin Deploy — Checkpoint 5

> Điền file này sau khi deploy xong. `pytest tests/test_cp5.py` đọc file này
> để tìm địa chỉ service của bạn và gọi thử.
>
> **Chỉ ghi TÊN biến môi trường, tuyệt đối không dán giá trị API key vào đây.**
> Repo này công khai — dán khóa vào là mất khóa.

## Thông Tin Học Viên

| Mục | Nội dung |
|-----|----------|
| Họ và tên | Đỗ Quốc An |
| Mã học viên | 2A202602892 |
| Repo | https://github.com/an1-tech/K4-L3A-DAY12-DoQuocAn-2A202602892-CloudServicesAndDeployment |

## Service

| Mục | Nội dung |
|-----|----------|
| Public URL | https://day12-agent-production-534d.up.railway.app |
| Platform | Railway |
| Ngày deploy | 28/09/2026 |

## Biến Môi Trường Đã Set Trên Cloud

Ghi tên biến và **nguồn giá trị**, không ghi giá trị:

| Biến | Đã set | Ghi chú |
|------|--------|---------|
| `PORT` | ✅ | Railway tự gán |
| `AGENT_API_KEY` | ✅ | đặt trong Railway Variables, không nằm trong repo |
| `REDIS_URL` | ✅ | reference tới `day12-redis.REDIS_URL` |
| `RATE_LIMIT_PER_MINUTE` | ✅ | 10 |
| `MONTHLY_BUDGET_USD` | ✅ | 10.0 |
| `LOG_LEVEL` | ✅ | INFO |

## Lệnh Kiểm Tra

```powershell
$baseUrl = "https://day12-agent-production-534d.up.railway.app"

Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
Invoke-RestMethod -Uri "$baseUrl/ready" -Method Get
```

Kiểm tra `/ask` không có API key:

```powershell
$body = @{
    question = "Hello"
} | ConvertTo-Json -Compress

try {
    Invoke-RestMethod `
        -Uri "$baseUrl/ask" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
} catch {
    Write-Host "HTTP status:" ([int]$_.Exception.Response.StatusCode)
}
```

Kiểm tra `/ask` có API key hợp lệ:

```powershell
$headers = @{
    "X-API-Key" = $apiKey
    "X-User-Id" = "cp5-test"
}

Invoke-RestMethod `
    -Uri "$baseUrl/ask" `
    -Method Post `
    -ContentType "application/json" `
    -Headers $headers `
    -Body $body
```

## Kết Quả Chạy Thật

```text
GET /health
HTTP 200
{"status":"ok","service":"day12-agent","version":"1.0.0"}

GET /ready
HTTP 200
{"status":"ready","redis":true}

POST /ask không có API key
HTTP 401
{"detail":"invalid or missing API key"}

POST /ask với API key hợp lệ
HTTP 200
user_id=cp5-test
history_length=0
answer present=true
cost_usd=0.00002265
```

## Ảnh Chụp Màn Hình

- `screenshots/dashboard.png` — Railway dashboard với agent và Redis đang Online.
- `screenshots/health.png` — kết quả gọi endpoint `/health`.
---

