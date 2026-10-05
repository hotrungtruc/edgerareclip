# EdgeRareClip

EdgeRareClip là nền tảng phát hiện bất thường trên thiết bị biên (edge), hướng tới các bài toán thị giác máy tính trong công nghiệp. Hệ thống đưa suy luận đến gần camera và thiết bị sản xuất, giảm độ trễ, giảm lưu lượng dữ liệu truyền về trung tâm và vẫn duy trì khả năng giám sát tập trung.

> **Trạng thái:** repository hiện đang ở giai đoạn khởi tạo kiến trúc. Các module đã có skeleton và hợp đồng tích hợp ban đầu; model TensorRT, business logic, database schema và dashboard sẽ được triển khai theo từng milestone.

## Mục tiêu kỹ thuật

- Suy luận anomaly theo thời gian gần thực trên Jetson Nano bằng TensorRT.
- Ước lượng độ hiếm (rarity-aware) và cập nhật memory bank trực tuyến.
- Gửi sự kiện qua MQTT, đệm cục bộ khi mất mạng và đồng bộ lại khi kết nối phục hồi.
- Cung cấp API FastAPI cho anomaly, device health, feedback và metrics.
- Hiển thị anomaly feed, heatmap, tình trạng thiết bị và chỉ số vận hành trên dashboard React.
- Chuẩn hóa model dữ liệu, cấu hình, logging và metrics trong package `shared/`.

## Kiến trúc tổng quan

```text
Camera -> Edge capture/preprocess -> TensorRT inference -> Postprocess
						      |
				  Local SQLite buffer <- MQTT -> Backend
									|
				      PostgreSQL <- Services/API <- WebSocket
									|
								React Dashboard
```

### Các thành phần

| Thành phần | Vai trò | Công nghệ chính |
| --- | --- | --- |
| `edge/` | Capture, tiền xử lý, suy luận và health heartbeat trên Jetson | Python, OpenCV/GStreamer, TensorRT, MQTT |
| `backend/` | API, xử lý nghiệp vụ, lưu trữ anomaly và quản lý fleet | FastAPI, SQLAlchemy async, PostgreSQL |
| `frontend/` | Dashboard giám sát và cấu hình | React, TypeScript, Vite, Zustand |
| `shared/` | Pydantic models, config, logging, metrics và utilities dùng chung | Python |
| `infra/` | MQTT broker, Prometheus, Grafana và script triển khai | Docker, Prometheus, Grafana |

## Cấu trúc repository

- `shared/`: package Python dùng chung giữa edge và backend.
- `edge/`: pipeline chạy trên Jetson Nano; model engine nằm trong `edge/models/`.
- `backend/`: FastAPI server, MQTT subscriber, services và migrations.
- `frontend/`: dashboard React.
- `infra/`: cấu hình quan sát hệ thống và triển khai.
- `docs/`: [kiến trúc](docs/architecture.md), [API](docs/api_reference.md) và [hướng dẫn triển khai](docs/deployment_guide.md).

## Yêu cầu môi trường

- Python 3.11 trở lên.
- Node.js 22 trở lên và npm.
- Docker Desktop hoặc Docker Engine với Compose.
- Jetson Nano chạy L4T phù hợp với phiên bản TensorRT của các engine.
- PostgreSQL và MQTT broker khi chạy đầy đủ hệ thống.

## Bắt đầu nhanh

### 1. Cấu hình biến môi trường

```powershell
Copy-Item .env.example .env
```

Điền các giá trị phù hợp trong `.env`, đặc biệt là `DATABASE_URL`, thông tin MQTT và `API_KEY`. Không commit `.env` hoặc secrets vào repository.

### 2. Chạy backend và database

```powershell
docker compose up --build
```

Backend mặc định lắng nghe tại `http://localhost:8000`. Swagger UI có tại `/docs` khi ứng dụng FastAPI đã được triển khai đầy đủ.

### 3. Chạy frontend trong development

```powershell
Set-Location frontend
npm install
npm run dev
```

### 4. Chạy kiểm tra Python

Từ thư mục gốc repository:

```powershell
python -m compileall shared edge backend
python -m pytest
```

Các lệnh tiện ích tương đương được khai báo trong `Makefile` (`make test`, `make backend`, `make frontend`) trên môi trường có GNU Make.

## Triển khai edge

1. Chuẩn bị ONNX model và build TensorRT engine tương thích với Jetson bằng `edge/scripts/build_engine.py`.
2. Đặt engine vào `edge/models/` và cập nhật đường dẫn trong `edge/config/edge_config.yaml`.
3. Kiểm tra camera, MQTT broker, kích thước frame và FPS trong file cấu hình.
4. Đo latency, memory và power bằng `edge/scripts/benchmark_edge.py`.
5. Dùng `infra/scripts/setup_jetson.sh` để chuẩn bị máy và `infra/scripts/deploy_edge.sh` để triển khai phiên bản edge.

Engine TensorRT phụ thuộc phần cứng và phiên bản CUDA/TensorRT; các file `.engine` trong repository chỉ là placeholder, không phải model production.

## Nguyên tắc vận hành

- **Edge-first:** chỉ gửi event và metadata cần thiết; không mặc định truyền toàn bộ video.
- **Resilient:** dùng local buffer khi mất kết nối và không làm dừng pipeline capture/inference.
- **Observable:** expose metrics cho Prometheus, ghi structured logs và theo dõi health heartbeat của device.
- **Secure by default:** dùng API key/JWT ở backend, giới hạn quyền truy cập MQTT và quản lý secrets ngoài source code.
- **Reproducible:** cố định phiên bản runtime/model trong môi trường triển khai và kiểm thử riêng cho edge, backend, frontend.

## CI/CD

GitHub Actions trong `.github/workflows/` hiện bao gồm:

- `edge_build.yml`: kiểm tra source edge.
- `backend_test.yml`: kiểm tra source backend.
- `frontend_test.yml`: cài dependency và build frontend.

## Tài liệu và đóng góp

Đọc thêm trong thư mục [`docs/`](docs/). Khi bổ sung một feature, nên cập nhật đồng thời contract trong `shared/`, test tương ứng, cấu hình mẫu và tài liệu vận hành.

## License

Phát hành theo [MIT License](LICENSE).
