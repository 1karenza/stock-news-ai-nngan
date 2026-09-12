# Nắng · Market Notes

Sổ tay tin doanh nghiệp và định giá trái phiếu, với giao diện vàng mật ong,
nền kem và tiêu đề serif. Repository độc lập: `1karenza/stock-news-ai-nngan`.

## Tab 1 — Stock News
- Quét tin theo mã cổ phiếu.
- Đọc/tóm tắt nội dung bài gốc khi có thể.
- Giữ nút Đọc tin gốc.
- Trích thông tin trái phiếu nếu bài có đề cập.

## Tab 2 — Bond Valuation
- Nhập mã/tên trái phiếu.
- Mệnh giá.
- Coupon rate.
- Thời gian còn lại.
- Tần suất trả coupon.
- Giá thị trường.
- Required yield.

App tính:
- Giá lý thuyết.
- YTM.
- Premium / Par / Discount.
- Macaulay Duration.
- Modified Duration.
- Bảng cash flow và PV từng kỳ.
- Xuất CSV.

Có 3 bộ dữ liệu mẫu để test ngay.

## Chạy
Windows: cài Python 3.12 trở lên, rồi mở `START_HERE_WINDOWS.bat`.
Launcher tạo môi trường `.venv`, cài thư viện và mở app.

Hoặc chạy trong terminal tại folder repo:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Kiểm tra trước khi deploy:

```powershell
.venv\Scripts\python.exe -m unittest discover -p "test_*.py" -v
```

## GitHub và deployment

Repository production: https://github.com/1karenza/stock-news-ai-nngan,
nhánh `main`. Streamlit Cloud dùng file `app.py` tại root repo.
Production: https://stock-news-ai-nngan.streamlit.app/
Kiểm tra `git remote -v`: origin phải là `1karenza/stock-news-ai-nngan`.

Sau khi sửa code, chạy thử bằng `streamlit run app.py` hoặc
`START_HERE_WINDOWS.bat`. Mở terminal tại folder này rồi chạy:

```powershell
git status
git remote -v
git diff
git add app.py news_content.py news_fetch.py assets requirements.txt README.md .gitignore .streamlit/config.toml START_HERE_WINDOWS.bat test_bond_v5.py test_news_fetch.py
git diff --cached
git commit -m "Update dashboard"
git push origin main
```

Nếu thêm file mới, dùng `git add <file>` để đưa file đó vào commit.
Git có thể yêu cầu đăng nhập GitHub trong lần push đầu tiên.
Nếu Git yêu cầu danh tính commit, cấu hình `git config user.name "Tên của bạn"`
và `git config user.email "Email GitHub của bạn"` rồi commit lại.

Streamlit Cloud tự redeploy sau khi push. Kiểm tra production URL sau đó;
nếu chưa cập nhật, dùng menu quản lý app để Reboot app.
Việc lưu file local không tự commit hoặc push.

Nếu GitHub có commit mới, dùng `git pull --rebase origin main` sau khi đã
commit thay đổi local, giải quyết conflict nếu có, rồi push lại. Không force push.

Không commit `.venv`, `.env`, API keys hoặc `.streamlit/secrets.toml`.
API key production được cấu hình trong Streamlit App Settings / Secrets.

## Giao diện Nắng

Style chung nằm trong `assets/editorial.css`; phải commit cả folder `assets`
khi deploy. Theme native của Streamlit nằm trong `.streamlit/config.toml`.
Be Vietnam Pro dùng cho nội dung, Lora dùng cho tiêu đề; tải từ Google Fonts
với font dự phòng khi mất kết nối. Đề mục tiếng Việt ngắn gọn, thanh điều hướng
có gạch nhấn và phần mở đầu thu gọn theo phong cách tạp chí nghiên cứu.
Nền vanilla `#FFF9E9`, bề mặt kem `#FFF3D2`, điểm nhấn vàng mật ong `#F4C95D`.
Giữ cố định Light theme; xanh/đỏ/cam vẫn phân biệt trạng thái tài chính.
Giao diện hỗ trợ màn hình nhỏ, focus bàn phím và `prefers-reduced-motion`.

## V5 — Kết luận trái phiếu

Giữ giá lý thuyết, YTM, duration, dòng tiền và xuất CSV; bổ sung đánh giá
0–100 theo định giá, lợi suất, tín nhiệm, thanh khoản và thông tin bảo đảm.
Thiếu tín nhiệm, thanh khoản hoặc chưa tính được YTM/duration sẽ hiển thị
“CẦN THÊM DỮ LIỆU”. Chênh lệch định giá được tính theo giá lý thuyết.
Kết luận giải thích điểm hỗ trợ và rủi ro, không thay thế thẩm định đầu tư.
OpenAI là tùy chọn; không có API key vẫn dùng tóm tắt từ dữ liệu công khai.

## Đọc nguồn tin

`news_fetch.py` xử lý link Google News và tải bài từ trang báo bằng requests.
Mỗi request có timeout và giới hạn kích thước; nội dung tiếng Việt được phân
tích từ bytes gốc. Lỗi tải không được cache, để nút tải lại có thể thử lại.
Nguồn yêu cầu đăng nhập, chặn truy cập hoặc chưa đọc được chỉ hiển thị thông
tin công khai đã có, kèm trạng thái nguồn; app không tự bổ sung số liệu thiếu.
