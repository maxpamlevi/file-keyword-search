# File Content Search (Tkinter)

This small desktop app (Python + Tkinter) searches for a keyword inside multiple file types within a folder (and its subfolders).

---

## English / EN

### Summary
- Simple Tk/ttk GUI to choose a folder, enter a keyword, and view matching files.
- Supported file types: `.txt`, `.docx`, `.doc` (best-effort), `.xlsx`, `.csv`, `.pdf`.
- Uses parallel I/O checks (ThreadPoolExecutor) and runs searches on a background thread so the UI remains responsive.
- Shows an indeterminate progress bar while searching.

### Requirements
- Python 3.8+
- Python packages: `python-docx`, `openpyxl`, `PyPDF2`

Optional (better `.doc` support):
- `antiword` (recommended on macOS/Linux) to extract text from legacy `.doc` files.

### Quick install
Open a terminal (zsh) and install required packages:

```bash
python3 -m pip install --user python-docx openpyxl PyPDF2
```

To improve `.doc` support (on macOS via Homebrew):

```bash
brew install antiword
```

### Run
From project folder (where `app.py` is located):

```bash
python3 app.py
```

### Shortcuts
- Enter in the Keyword field — start search.
- Enter on a selected result — open the file with the system default app (macOS uses `open`).
- Double-click a result — open the file.
- Ctrl+O (Windows/Linux) or ⌘+O (macOS) — choose folder.
- Ctrl+F / ⌘+F — focus the Keyword field.

### Supported file types
- .txt
- .docx (handled with python-docx)
- .doc (best-effort; improved with `antiword`)
- .xlsx
- .csv
- .pdf (PyPDF2)

### Notes & suggestions
- Some PDFs may produce parsing warnings but shouldn't crash the app.
- For very large folders consider adding a Cancel button, streaming results, or using a more robust worker model.
- For robust `.doc` extraction, install `antiword` or use LibreOffice in headless conversion mode.

---

## Tiếng Việt / VI

### Tóm tắt
- Ứng dụng desktop nhỏ (Python + Tkinter) để tìm từ khoá trong nhiều loại file trong một thư mục và thư mục con.
- Hỗ trợ: `.txt`, `.docx`, `.doc` (best-effort), `.xlsx`, `.csv`, `.pdf`.
- Dùng ThreadPoolExecutor để kiểm tra file song song và chạy tìm trên luồng nền để UI không bị đứng.
- Hiển thị progress bar khi đang tìm.

### Yêu cầu
- Python 3.8+
- Các package: `python-docx`, `openpyxl`, `PyPDF2`

Tuỳ chọn (hỗ trợ `.doc` tốt hơn):
- `antiword` (khuyến nghị trên macOS/Linux).

### Cài đặt nhanh
Mở terminal (zsh):

```bash
python3 -m pip install --user python-docx openpyxl PyPDF2
```

Để hỗ trợ `.doc` tốt hơn (macOS/Homebrew):

```bash
brew install antiword
```

### Chạy
Trong thư mục chứa `app.py`:

```bash
python3 app.py
```

### Phím tắt
- Enter trong ô Từ khoá — bắt đầu tìm.
- Enter khi chọn kết quả — mở file bằng ứng dụng mặc định.
- Double-click — mở file.
- Ctrl+O (Windows/Linux) hoặc ⌘+O (macOS) — chọn thư mục.
- Ctrl+F / ⌘+F — focus ô Từ khoá.

### Các loại file được hỗ trợ
- .txt
- .docx (python-docx)
- .doc (nếu cài `antiword` sẽ tốt hơn)
- .xlsx
- .csv
- .pdf (PyPDF2)

### Lưu ý & gợi ý
- Một vài PDF có thể báo cảnh báo khi đọc nhưng không làm ứng dụng crash.
- Nếu thư mục rất lớn, cân nhắc: thêm nút Cancel, hiện kết quả dần, hoặc dùng mô hình worker khác để mở rộng.
- Để cải thiện `.doc`, cài `antiword` hoặc dùng LibreOffice headless để chuyển đổi.

---

If you want, I can also add a `requirements.txt` file, demo screenshots, or a short video/gif showing the UI.


---

# Tìm kiếm nội dung trong file (Tkinter)

Ứng dụng desktop nhỏ bằng Python dùng Tkinter để tìm từ khoá trong nhiều loại file trong một thư mục (và các thư mục con).

## Tóm tắt
- Giao diện đơn giản (Tk/ttk) để chọn thư mục, nhập từ khoá và xem kết quả.
- Hỗ trợ tìm trong: `.txt`, `.docx`, `.doc` (best-effort), `.xlsx`, `.csv`, `.pdf`.
- Tìm nhanh hơn nhờ xử lý song song (ThreadPoolExecutor) và tìm chạy trên luồng nền để UI không bị đứng.
- Hiển thị progress bar khi đang tìm.

## Yêu cầu
- Python 3.8+
- Các thư viện Python: `python-docx`, `openpyxl`, `PyPDF2`

Tuỳ chọn (cải thiện hỗ trợ `.doc`):
- `antiword` (recommended trên macOS/Linux) để trích văn bản từ file `.doc` cổ điển.

## Cài đặt nhanh
Mở terminal (zsh) và cài các thư viện:

```bash
python3 -m pip install --user python-docx openpyxl PyPDF2
```

Nếu muốn hỗ trợ `.doc` tốt hơn (macOS Homebrew):

```bash
brew install antiword
```

## Chạy ứng dụng
Trong thư mục dự án (nơi chứa `app.py`) chạy:

```bash
python3 app.py
```