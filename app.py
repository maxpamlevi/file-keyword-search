import os
import docx
import openpyxl
import PyPDF2
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import concurrent.futures
import csv
import shutil
import subprocess
import sys

# ==== Các hàm tìm kiếm ====
def search_in_txt(path, keyword):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return keyword.lower() in f.read().lower()
    except:
        return False

def search_in_docx(path, keyword):
    try:
        doc = docx.Document(path)
        for para in doc.paragraphs:
            if keyword.lower() in para.text.lower():
                return True
    except:
        return False
    return False

def search_in_xlsx(path, keyword):
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                for cell in row:
                    if cell and keyword.lower() in str(cell).lower():
                        return True
    except:
        return False
    return False

def search_in_csv(path, keyword):
    try:
        with open(path, newline='', encoding='utf-8', errors='ignore') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                for cell in row:
                    if cell and keyword.lower() in str(cell).lower():
                        return True
    except:
        return False
    return False

def search_in_doc(path, keyword):
    # Try to use `antiword` if available (common on mac via brew). Fallback: return False.
    antiword = shutil.which('antiword')
    if antiword:
        try:
            output = subprocess.check_output([antiword, path], stderr=subprocess.DEVNULL)
            text = output.decode('utf-8', errors='ignore')
            if keyword.lower() in text.lower():
                return True
        except:
            return False
    else:
        # fallback: try a naive binary->text decode (may not work for all .doc)
        try:
            with open(path, 'rb') as f:
                raw = f.read()
                text = raw.decode('utf-8', errors='ignore')
                if keyword.lower() in text.lower():
                    return True
        except:
            return False
    return False

def search_in_pdf(path, keyword):
    try:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if text and keyword.lower() in text.lower():
                    return True
    except:
        return False
    return False

def search_files(folder, keyword, on_match=None, cancel_event=None):
    """
    Walk folder recursively and check files concurrently.
    If on_match is provided, call on_match(path) as matches are found.
    If cancel_event is provided (threading.Event), stop early when set.
    Returns list of matches only if on_match is None.
    """
    # Collect paths first (to get a stable list)
    paths = []
    for root, _, files in os.walk(folder):
        for file in files:
            paths.append(os.path.join(root, file))

    matches = []

    def check_path(path):
        lower = path.lower()
        try:
            if lower.endswith('.txt') and search_in_txt(path, keyword):
                return path
            if lower.endswith('.docx') and search_in_docx(path, keyword):
                return path
            if lower.endswith('.doc') and search_in_doc(path, keyword):
                return path
            if lower.endswith('.xlsx') and search_in_xlsx(path, keyword):
                return path
            if lower.endswith('.csv') and search_in_csv(path, keyword):
                return path
            if lower.endswith('.pdf') and search_in_pdf(path, keyword):
                return path
        except Exception:
            return None
        return None

    # Use a modest number of workers
    max_workers = min(32, (os.cpu_count() or 4) * 5)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(check_path, p): p for p in paths}
        try:
            for fut in concurrent.futures.as_completed(futures):
                if cancel_event and cancel_event.is_set():
                    break
                res = fut.result()
                if res:
                    if on_match:
                        try:
                            on_match(res)
                        except Exception:
                            pass
                    else:
                        matches.append(res)
        except Exception:
            pass

    return matches

# ==== GUI ====
def choose_folder(event=None):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_var.set(folder_selected)

_search_thread = None
_search_lock = threading.Lock()
_cancel_event = None

def run_search(event=None):
    folder = folder_var.get().strip()
    keyword = keyword_var.get().strip()

    if not folder or not keyword:
        messagebox.showwarning("Warning", "Please select a folder and enter a keyword")
        return

    def _worker():
        # stream matches using on_match callback
        matched_count = 0

        def on_match(path):
            nonlocal matched_count
            matched_count += 1

            def _insert():
                tag = 'even' if matched_count % 2 == 0 else 'odd'
                tree.insert('', tk.END, values=(path,), tags=(tag,))
                status_var.set(f"{t('status_done_n', n=matched_count)}")

            root.after(0, _insert)

        try:
            # clear existing
            root.after(0, lambda: [tree.delete(i) for i in tree.get_children()])
            search_files(folder, keyword, on_match=on_match, cancel_event=_cancel_event)
        except Exception:
            pass

        def _on_done():
            if matched_count == 0:
                tree.insert('', tk.END, values=(t('no_files'),), tags=('odd',))
                status_var.set(t('status_done_0'))
            else:
                status_var.set(t('status_done_n', n=matched_count))
            search_btn.config(state='normal')
            cancel_btn.config(state='disabled')
            stop_progress()

        root.after(0, _on_done)

    # Prevent overlapping searches; show UI progress instead of messagebox
    with _search_lock:
        global _search_thread, _cancel_event
        if _search_thread and _search_thread.is_alive():
            start_progress()
            status_var.set(t('another_search'))
            return
        search_btn.config(state='disabled')
        cancel_btn.config(state='normal')
        # create cancel event
        _cancel_event = threading.Event()
        start_progress()
        _search_thread = threading.Thread(target=_worker, daemon=True)
        _search_thread.start()

# ==== Tạo cửa sổ chính ====
root = tk.Tk()
root.title("🔍 File Content Search")
root.geometry("800x560")

# Use ttk for nicer widgets and modern styling
style = ttk.Style(root)
try:
    # prefer a modern-looking theme when available
    style.theme_use('clam')
except:
    pass

# Modern Win11-like colors and fonts (best-effort with Tkinter)
ACCENT = '#0a84ff'  # blue accent similar to Win11
BG = '#F3F6FB'
CARD = '#FFFFFF'
TEXT = '#111827'
muted = '#6B7280'
FONT_HEADER = ('Segoe UI', 11)
FONT_NORMAL = ('Segoe UI', 10)

root.configure(bg=BG)
style.configure('.', background=BG, foreground=TEXT, font=FONT_NORMAL)
style.configure('Card.TFrame', background=CARD, relief='flat')
style.configure('Accent.TButton', background=ACCENT, foreground='white')
style.map('Accent.TButton', background=[('active', '#0a6ff0')])
style.configure('TEntry', padding=6)
style.configure('Treeview', font=FONT_NORMAL, rowheight=28, background=CARD, fieldbackground=CARD, bordercolor=BG)
style.configure('Treeview.Heading', font=FONT_HEADER, background=BG)

# Treeview row tags for striping
TREE_EVEN = '#FFFFFF'
TREE_ODD = '#F7F9FC'
style.map('Treeview', background=[('selected', ACCENT)])

# Biến lưu đường dẫn, keyword và ngôn ngữ
folder_var = tk.StringVar()
keyword_var = tk.StringVar()

# Language support: default 'en'
lang_var = tk.StringVar(value='en')  # 'en' or 'vi'

TRANSLATIONS = {
    'en': {
        'title': '🔍 File Content Search',
        'folder_label': 'Folder:',
        'choose_btn': 'Choose folder (⌘/Ctrl+O)',
        'keyword_label': 'Keyword:',
        'search_btn': '🔍 Search (Enter)',
        'results_label': 'Results:',
        'status_ready': 'Ready',
        'status_searching': 'Searching...',
        'status_done_n': 'Done: {n} results',
        'status_done_0': 'Done: 0 results',
        'no_files': '❌ No files found containing the keyword.',
        'warning_title': 'Warning',
        'warning_select': 'Please select a folder and enter a keyword',
        'another_search': 'Another search is already running — please wait...',
        'error_open_title': 'Error',
        'error_open': 'Cannot open file: {e}',
        'lang_display_en': 'English',
        'lang_display_vi': 'Tiếng Việt'
    },
    'vi': {
        'title': '🔍 Tìm kiếm nội dung file',
        'folder_label': 'Thư mục tìm kiếm:',
        'choose_btn': 'Chọn thư mục (⌘/Ctrl+O)',
        'keyword_label': 'Từ khoá:',
        'search_btn': '🔍 Tìm kiếm (Enter)',
        'results_label': 'Kết quả:',
        'status_ready': 'Sẵn sàng',
        'status_searching': 'Đang tìm kiếm...',
        'status_done_n': 'Hoàn tất: {n} kết quả',
        'status_done_0': 'Hoàn tất: 0 kết quả',
        'no_files': '❌ Không tìm thấy file nào chứa từ khoá.',
        'warning_title': 'Cảnh báo',
        'warning_select': 'Vui lòng chọn thư mục và nhập từ khoá',
        'another_search': 'Đang có tiến trình tìm kiếm khác — vui lòng chờ...',
        'error_open_title': 'Lỗi',
        'error_open': 'Không thể mở file: {e}',
        'lang_display_en': 'English',
        'lang_display_vi': 'Tiếng Việt'
    }
}

def t(key, **kwargs):
    code = lang_var.get()
    text = TRANSLATIONS.get(code, TRANSLATIONS['en']).get(key, '')
    try:
        return text.format(**kwargs)
    except Exception:
        return text

status_var = tk.StringVar(value=t('status_ready'))

# Top frame for inputs
top = ttk.Frame(root, padding=(10, 10))
top.pack(fill='x')

folder_label = ttk.Label(top, text=t('folder_label'))
folder_label.grid(row=0, column=0, sticky='w')
folder_entry = ttk.Entry(top, textvariable=folder_var)
folder_entry.grid(row=0, column=1, sticky='ew', padx=6)
choose_btn = ttk.Button(top, text=t('choose_btn'), command=choose_folder)
choose_btn.grid(row=0, column=2, sticky='e')

# language selector is placed in the bottom status area

keyword_label = ttk.Label(top, text=t('keyword_label'))
keyword_label.grid(row=1, column=0, sticky='w', pady=(8,0))
keyword_entry = ttk.Entry(top, textvariable=keyword_var)
keyword_entry.grid(row=1, column=1, sticky='ew', padx=6, pady=(8,0))
search_btn = ttk.Button(top, text=t('search_btn'), command=run_search)
search_btn.grid(row=1, column=2, sticky='e', pady=(8,0))

# Cancel button (disabled by default)
cancel_btn = ttk.Button(top, text='Cancel', command=lambda: cancel_search())
cancel_btn.grid(row=1, column=3, sticky='e', padx=(8,0), pady=(8,0))
cancel_btn.config(state='disabled')

top.columnconfigure(1, weight=1)

# Results frame
mid = ttk.Frame(root, padding=(10, 0, 10, 10))
mid.pack(fill='both', expand=True)

ttk.Label(mid, text="Results:").pack(anchor='w')
listbox_frame = ttk.Frame(mid, style='Card.TFrame', padding=10)
listbox_frame.pack(fill='both', expand=True)

# Use Treeview for nicer, modern result list
cols = ('path',)
tree = ttk.Treeview(listbox_frame, columns=cols, show='headings', selectmode='browse')
tree.heading('path', text='File path')
tree.column('path', anchor='w')
tree.pack(fill='both', expand=True, side='left')

vsb = ttk.Scrollbar(listbox_frame, orient='vertical', command=tree.yview)
tree.configure(yscrollcommand=vsb.set)
vsb.pack(side='right', fill='y')

# Configure tree tags for striping
tree.tag_configure('odd', background=TREE_ODD)
tree.tag_configure('even', background=TREE_EVEN)

# Bottom frame containing status and language selector
bottom_frame = ttk.Frame(root)
bottom_frame.pack(fill='x', side='bottom')

status = ttk.Label(bottom_frame, textvariable=status_var, relief='sunken', anchor='w', padding=(5,2))
status.pack(side='left', fill='x', expand=True)

# Language selector placed at bottom-right
lang_display_var = tk.StringVar()
def _on_lang_select(display):
    # map display string to code and refresh
    code = TRANSLATIONS['en']['lang_display_en']
    if display == TRANSLATIONS['en']['lang_display_en']:
        lang_var.set('en')
    else:
        lang_var.set('vi')
    refresh_ui_texts()

lang_menu = tk.OptionMenu(bottom_frame, lang_display_var, TRANSLATIONS['en']['lang_display_en'], TRANSLATIONS['en']['lang_display_vi'], command=_on_lang_select)
lang_menu.config(width=12)
lang_menu.pack(side='right', padx=8, pady=4)
lang_display_var.set(TRANSLATIONS['en']['lang_display_en'])

# Progress bar (hidden until search starts)
progress = ttk.Progressbar(root, mode='indeterminate')
progress.pack(fill='x', side='bottom')
progress.pack_forget()


def start_progress():
    # show and start the indeterminate progress bar
    try:
        progress.pack(fill='x', side='bottom')
        progress.start(10)
        status_var.set('Searching...')
        root.update_idletasks()
    except Exception:
        pass


def stop_progress():
    try:
        progress.stop()
        progress.pack_forget()
    except Exception:
        pass


def cancel_search():
    global _cancel_event
    if _cancel_event:
        _cancel_event.set()
    cancel_btn.config(state='disabled')
    status_var.set('Cancelled')

# Hàm mở file khi nhấp đúp
def open_file(path):
    """Open a file with the system default application in a cross-platform way.

    Attempts platform-native APIs first, then falls back to common shell commands.
    """
    try:
        if os.name == 'nt':
            # Prefer native API on Windows
            return os.startfile(path)
    except Exception:
        # os.startfile might not be available in some environments; fall through
        pass

    # macOS
    if sys.platform == 'darwin':
        try:
            subprocess.Popen(['open', path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            pass

    # Windows fallback using cmd 'start' (internal command)
    if os.name == 'nt':
        try:
            # Use the shell to run the internal 'start' command. The empty title "" is required.
            subprocess.Popen(f'start "" "{path}"', shell=True)
            return True
        except Exception:
            pass

    # Linux/other: try xdg-open then gio
    for opener in ("xdg-open", "gio", "gnome-open"):
        try:
            subprocess.Popen([opener, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            continue

    # If nothing worked, raise an exception to inform caller
    raise OSError('No suitable opener found for this platform')

def open_selected_file(event=None):
    # If double-click provided an event, try to select the row under the pointer first
    if event is not None and hasattr(event, 'y'):
        row = tree.identify_row(event.y)
        if row:
            tree.selection_set(row)

    sel = tree.selection()
    if not sel:
        return
    file_path = tree.item(sel[0], 'values')[0]
    if file_path.startswith("❌"):
        return
    try:
        open_file(file_path)
    except Exception as e:
        # Show a friendly error if opening fails
        try:
            messagebox.showerror(t('error_open_title'), t('error_open', e=e))
        except Exception:
            # In case messagebox itself fails for some reason, print to stderr
            print('Failed to open file:', file_path, 'error:', e)

# Bind double-click and Enter on result list
tree.bind('<Double-1>', open_selected_file)
tree.bind('<Return>', open_selected_file)

# Keyboard shortcuts
def _is_mac():
    return root.tk.call('tk', 'windowingsystem') == 'aqua'

mod = 'Command' if _is_mac() else 'Control'

# Enter in keyword entry triggers search
# (bindings created later after widgets exist)
keyword_entry.bind('<Return>', run_search)
# Ctrl/Cmd+O -> choose folder
root.bind_all(f'<{mod}-o>', choose_folder)
# Ctrl/Cmd+f -> focus keyword
def focus_keyword(event=None):
    keyword_entry.focus_set()
    return 'break'

root.bind_all(f'<{mod}-f>', focus_keyword)

# Make Enter anywhere also trigger search when focus is on root (but avoid when in listbox)
def global_return(event):
    widget = event.widget
    if widget is tree:
        return None
    return run_search()

root.bind_all('<Return>', global_return)


def refresh_ui_texts():
    # Update window title and widget texts based on selected language
    root.title(t('title'))
    folder_label.config(text=t('folder_label'))
    choose_btn.config(text=t('choose_btn'))
    keyword_label.config(text=t('keyword_label'))
    search_btn.config(text=t('search_btn'))
    # results label — find the label widget (first child of mid)
    # We created a label earlier using ttk.Label(mid, text=...)
    # For simplicity, recreate the text by searching for a matching widget.
    for child in mid.winfo_children():
        if isinstance(child, ttk.Label):
            child.config(text=t('results_label'))
            break
    # update status text
    status_var.set(t('status_ready'))
    # update language display
    display = TRANSLATIONS[lang_var.get()]['lang_display_en'] if lang_var.get() == 'en' else TRANSLATIONS[lang_var.get()]['lang_display_vi']
    lang_display_var.set(display)

# initialize UI texts
refresh_ui_texts()

# Chạy app
root.mainloop()
