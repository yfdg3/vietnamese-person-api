# Vietnamese Person API

REST API tạo **thông tin người Việt Nam giả lập** để dùng trong kiểm thử, demo và phát triển phần mềm.

> Dữ liệu do API sinh ra là dữ liệu giả, không đại diện cho người thật.

## Thông tin trả về

- Giới tính bằng tiếng Anh và tiếng Việt
- Ngày, tháng, năm sinh
- Tuổi
- Tên đầy đủ tiếng Việt
- Tên đầy đủ tiếng Anh
- Họ
- Tên lót, có thể là `null`
- Tên chính
- Tên riêng tiếng Anh
- UUID
- Cờ `is_synthetic: true`

## Chạy bằng Python

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Mở Swagger UI tại:

```text
http://localhost:8000/docs
```

## Chạy bằng Docker

```bash
docker compose up --build
```

## Endpoint

### `GET /api/person`

Tham số:

| Tham số | Kiểu | Mô tả |
|---|---|---|
| `gender` | `male`, `female`, `other` | Không bắt buộc |
| `min_age` | số nguyên | Tuổi nhỏ nhất, mặc định 18 |
| `max_age` | số nguyên | Tuổi lớn nhất, mặc định 80 |
| `seed` | chuỗi | Cùng seed trả về cùng kết quả |

Ví dụ:

```bash
curl "http://localhost:8000/api/person?gender=female&min_age=20&max_age=30&seed=demo"
```

Phản hồi mẫu:

```json
{
  "id": "061a9e55-9990-5e58-90bb-cfbde9b25443",
  "is_synthetic": true,
  "gender": "female",
  "gender_vi": "Nữ",
  "name": {
    "vietnamese_full_name": "Nguyễn Thị Linh",
    "english_full_name": "Linda Nguyen",
    "family_name": "Nguyễn",
    "middle_name": "Thị",
    "given_name": "Linh",
    "english_given_name": "Linda"
  },
  "birth": {
    "date": "2001-08-17",
    "day": 17,
    "month": 8,
    "year": 2001,
    "age": 24
  }
}
```

## Kiểm thử

```bash
pip install -r requirements-dev.txt
pytest
```

## API khác

- `GET /` — thông tin API
- `GET /health` — kiểm tra trạng thái
- `GET /docs` — Swagger UI
- `GET /redoc` — ReDoc
