# SocketProgramming Demo

Project này đã được cập nhật theo 3 phần chính:

## 1. Serve static file

- Server nhận HTTP request từ client.
- Parse đường dẫn file từ request.
- Tìm file trong thư mục `public`.
- Nếu có file thì trả về nội dung file, nếu không có thì trả `404 Not Found`.

## 2. Viết client

- Client dùng `argparse` để nhận tham số từ command line.
- Cách gọi:

```bash
python client.py server_host server_port filename
```

- Client gửi request lấy file và lưu file tải về ở máy local.

## 3. Sử dụng multithread

- Server dùng `ThreadPoolExecutor` để tạo thread pool đơn giản.
- Main thread nhận kết nối mới.
- Mỗi request được đưa vào worker thread để xử lý song song.