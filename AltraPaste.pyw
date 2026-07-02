"""
AltraPaste v2 — pembantu salin & tampal pantas untuk Windows
============================================================
AUTO-COPY  (F7) : Pilih/highlight teks di mana-mana app = teks terus DISALIN.
                  Setiap pilihan baru menggantikan salinan sebelumnya.
PASTE MODE (F8) : Klik KANAN di mana-mana medan teks = TAMPAL terus
                  (tiada menu). Shift + klik kanan = menu biasa.

Pratonton clipboard terkini dipaparkan dalam tetingkap kecil.
Pure stdlib (ctypes + tkinter) — tiada pip install. Tutup tetingkap = berhenti.

Nota keselamatan: AUTO-COPY dan PASTE MODE dilangkau secara automatik dalam
tetingkap terminal (cmd / PowerShell / Windows Terminal / mintty / ConEmu)
kerana Ctrl+C di situ membatalkan arahan yang sedang berjalan.
"""
import ctypes
import ctypes.wintypes as wt
import threading
import time
import tkinter as tk

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# ---------------- pemalar Win32 ----------------
WH_MOUSE_LL = 14
WM_LBUTTONDOWN, WM_LBUTTONUP = 0x0201, 0x0202
WM_RBUTTONDOWN, WM_RBUTTONUP = 0x0204, 0x0205
WM_HOTKEY = 0x0312
VK_SHIFT, VK_CONTROL, VK_C, VK_V, VK_F7, VK_F8 = 0x10, 0x11, 0x43, 0x56, 0x76, 0x77
MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0002, 0x0004
KEYEVENTF_KEYUP = 0x0002
LLMHF_INJECTED = 0x0001
CF_UNICODETEXT = 13
GA_ROOT = 2
DRAG_X, DRAG_Y = 30, 15          # ambang seretan (px) untuk dikira "memilih teks"

TERMINAL_CLASSES = {
    "ConsoleWindowClass",             # cmd / PowerShell klasik
    "CASCADIA_HOSTING_WINDOW_CLASS",  # Windows Terminal
    "mintty",                         # Git Bash
    "VirtualConsoleClass",            # ConEmu
}


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("pt", POINT), ("mouseData", wt.DWORD), ("flags", wt.DWORD),
                ("time", wt.DWORD), ("dwExtraInfo", ctypes.c_size_t)]


HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, wt.WPARAM, wt.LPARAM)
user32.SetWindowsHookExW.restype = ctypes.c_void_p
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, ctypes.c_void_p, wt.DWORD]
user32.CallNextHookEx.restype = ctypes.c_ssize_t
user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, wt.WPARAM, wt.LPARAM]
user32.WindowFromPoint.restype = ctypes.c_void_p
user32.WindowFromPoint.argtypes = [POINT]
user32.GetAncestor.restype = ctypes.c_void_p
user32.GetAncestor.argtypes = [ctypes.c_void_p, wt.UINT]
user32.GetClipboardData.restype = ctypes.c_void_p
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]

paste_on = threading.Event(); paste_on.set()
copy_on = threading.Event(); copy_on.set()
_down_pt = POINT(0, 0)
_own_hwnd = None                  # tetingkap AltraPaste sendiri (abaikan)


def window_class_at(pt):
    """Nama kelas tetingkap induk di bawah koordinat skrin pt."""
    hwnd = user32.WindowFromPoint(pt)
    if not hwnd:
        return "", None
    root_h = user32.GetAncestor(hwnd, GA_ROOT) or hwnd
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(ctypes.c_void_p(root_h), buf, 256)
    return buf.value, root_h


def send_ctrl(vk):
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


def read_clipboard():
    for _ in range(6):
        if user32.OpenClipboard(None):
            try:
                h = user32.GetClipboardData(CF_UNICODETEXT)
                if not h:
                    return ""
                p = kernel32.GlobalLock(h)
                if not p:
                    return ""
                try:
                    return ctypes.wstring_at(p)
                finally:
                    kernel32.GlobalUnlock(h)
            finally:
                user32.CloseClipboard()
        time.sleep(0.03)
    return ""


def do_paste():
    """Klik kiri sintetik (fokuskan medan) kemudian Ctrl+V."""
    time.sleep(0.05)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.15)
    send_ctrl(VK_V)


def do_autocopy():
    """Selepas seretan pilihan teks: Ctrl+C, kemudian kemas kini pratonton."""
    before = read_clipboard()
    time.sleep(0.10)              # biar app selesaikan pilihan dahulu
    send_ctrl(VK_C)
    time.sleep(0.15)
    after = read_clipboard()
    if after and after != before:
        root.after(0, lambda: set_preview(after))


def hook_proc(nCode, wParam, lParam):
    global _down_pt
    if nCode >= 0:
        ms = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
        injected = ms.flags & LLMHF_INJECTED

        # ---- PASTE MODE: klik kanan = tampal terus ----
        if paste_on.is_set() and not injected and wParam in (WM_RBUTTONDOWN, WM_RBUTTONUP):
            if not (user32.GetAsyncKeyState(VK_SHIFT) & 0x8000):
                cls, hwnd = window_class_at(ms.pt)
                # terminal ada klik-kanan-tampal sendiri; tetingkap sendiri dilangkau
                if cls not in TERMINAL_CLASSES and hwnd != _own_hwnd:
                    if wParam == WM_RBUTTONDOWN:
                        threading.Thread(target=do_paste, daemon=True).start()
                    return 1      # telan klik kanan (menu tidak keluar)

        # ---- AUTO-COPY: seret-pilih teks = salin terus ----
        if not injected and wParam == WM_LBUTTONDOWN:
            _down_pt = POINT(ms.pt.x, ms.pt.y)
        elif copy_on.is_set() and not injected and wParam == WM_LBUTTONUP:
            if (abs(ms.pt.x - _down_pt.x) >= DRAG_X or
                    abs(ms.pt.y - _down_pt.y) >= DRAG_Y):
                cls, hwnd = window_class_at(ms.pt)
                if cls not in TERMINAL_CLASSES and hwnd != _own_hwnd:
                    threading.Thread(target=do_autocopy, daemon=True).start()

    return user32.CallNextHookEx(None, nCode, wParam, lParam)


_proc_ref = HOOKPROC(hook_proc)   # simpan rujukan supaya tidak di-GC


def hook_thread():
    hook = user32.SetWindowsHookExW(WH_MOUSE_LL, _proc_ref, None, 0)
    if not hook:
        return
    user32.RegisterHotKey(None, 1, 0, VK_F8)   # paste mode
    user32.RegisterHotKey(None, 2, 0, VK_F7)   # auto-copy
    msg = wt.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        if msg.message == WM_HOTKEY:
            root.after(0, toggle_paste if msg.wParam == 1 else toggle_copy)
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))


# ---------------- UI kecil (sentiasa di atas) ----------------
ON_BG, OFF_BG = "#16a34a", "#64748b"

root = tk.Tk()
root.title("AltraPaste")
root.attributes("-topmost", True)
root.resizable(False, False)
root.configure(bg="#0f172a")
root.update_idletasks()
root.geometry(f"+{root.winfo_screenwidth() - 330}+16")

tk.Label(root, text="📋 AltraPaste v2 — GCE Altra Guide", bg="#0f172a", fg="#93c5fd",
         font=("Segoe UI", 10, "bold")).pack(padx=14, pady=(10, 4))

btn_copy = tk.Button(root, font=("Segoe UI", 11, "bold"), fg="white",
                     relief="flat", cursor="hand2", command=lambda: toggle_copy())
btn_copy.pack(padx=14, pady=2, fill="x")

btn_paste = tk.Button(root, font=("Segoe UI", 11, "bold"), fg="white",
                      relief="flat", cursor="hand2", command=lambda: toggle_paste())
btn_paste.pack(padx=14, pady=2, fill="x")

prev_frame = tk.Frame(root, bg="#1e293b")
prev_frame.pack(padx=14, pady=(6, 2), fill="x")
tk.Label(prev_frame, text="CLIPBOARD TERKINI", bg="#1e293b", fg="#60a5fa",
         font=("Segoe UI", 7, "bold")).pack(anchor="w", padx=8, pady=(5, 0))
preview = tk.Label(prev_frame, text="(kosong)", bg="#1e293b", fg="#e2e8f0",
                   font=("Segoe UI", 9), wraplength=260, justify="left", anchor="w")
preview.pack(fill="x", padx=8, pady=(0, 6))

tk.Label(root, text="Pilih teks = salin terus  ·  Klik KANAN = tampal terus\n"
                    "Shift+Kanan = menu biasa  ·  F7/F8 = ON/OFF\n"
                    "Tutup tetingkap ini untuk berhenti",
         bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 8), justify="center"
         ).pack(padx=14, pady=(4, 10))


def set_preview(text):
    t = " ".join(text.split())
    preview.config(text=(t[:120] + "…") if len(t) > 120 else (t or "(kosong)"))


def _style(btn, on, label):
    bg = ON_BG if on else OFF_BG
    btn.config(text=f"{label}: {'ON  ✔' if on else 'OFF'}", bg=bg, activebackground=bg)


def update_ui():
    _style(btn_copy, copy_on.is_set(), "AUTO-COPY (pilih=salin)")
    _style(btn_paste, paste_on.is_set(), "PASTE (klik kanan=tampal)")


def toggle_copy():
    copy_on.clear() if copy_on.is_set() else copy_on.set()
    update_ui()


def toggle_paste():
    paste_on.clear() if paste_on.is_set() else paste_on.set()
    update_ui()


update_ui()
set_preview(read_clipboard())
root.update_idletasks()
_own_hwnd = user32.GetAncestor(ctypes.c_void_p(root.winfo_id()), GA_ROOT)
threading.Thread(target=hook_thread, daemon=True).start()
root.mainloop()
