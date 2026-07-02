"""
AltraPaste — pembantu GCE Altra Guide
Bila Paste Mode ON: klik KANAN di mana-mana tetingkap Windows = TAMPAL terus
(tiada menu, tiada pilih "Paste"). Shift + klik kanan = menu biasa.
F8 = toggle ON/OFF.  Pure stdlib (ctypes + tkinter) — tiada pip install.
"""
import ctypes
import ctypes.wintypes as wt
import threading
import time
import tkinter as tk

user32 = ctypes.windll.user32

WH_MOUSE_LL = 14
WM_RBUTTONDOWN, WM_RBUTTONUP = 0x0204, 0x0205
WM_HOTKEY = 0x0312
VK_SHIFT, VK_CONTROL, VK_V, VK_F8 = 0x10, 0x11, 0x56, 0x77
MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0002, 0x0004
KEYEVENTF_KEYUP = 0x0002

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, wt.WPARAM, wt.LPARAM)
user32.SetWindowsHookExW.restype = ctypes.c_void_p
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, ctypes.c_void_p, wt.DWORD]
user32.CallNextHookEx.restype = ctypes.c_ssize_t
user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, wt.WPARAM, wt.LPARAM]

enabled = threading.Event()          # Paste Mode state
enabled.set()                        # mula dalam keadaan ON


def do_paste():
    """Klik kiri sintetik (fokuskan medan di bawah kursor) kemudian Ctrl+V."""
    time.sleep(0.05)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.15)
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_V, 0, 0, 0)
    user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


def hook_proc(nCode, wParam, lParam):
    if nCode >= 0 and enabled.is_set() and wParam in (WM_RBUTTONDOWN, WM_RBUTTONUP):
        # Shift + klik kanan = benarkan menu konteks biasa
        if not (user32.GetAsyncKeyState(VK_SHIFT) & 0x8000):
            if wParam == WM_RBUTTONDOWN:
                threading.Thread(target=do_paste, daemon=True).start()
            return 1  # telan event klik kanan (menu tidak keluar)
    return user32.CallNextHookEx(None, nCode, wParam, lParam)


_proc_ref = HOOKPROC(hook_proc)  # simpan rujukan supaya tidak di-GC


def hook_thread():
    hook = user32.SetWindowsHookExW(WH_MOUSE_LL, _proc_ref, None, 0)
    if not hook:
        return
    user32.RegisterHotKey(None, 1, 0, VK_F8)
    msg = wt.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        if msg.message == WM_HOTKEY:
            root.after(0, toggle)
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))


# ---------------- UI kecil (sentiasa di atas) ----------------
ON_BG, OFF_BG = "#16a34a", "#64748b"

root = tk.Tk()
root.title("AltraPaste")
root.attributes("-topmost", True)
root.resizable(False, False)
root.configure(bg="#0f172a")
# letak di penjuru kanan atas skrin
root.update_idletasks()
root.geometry(f"+{root.winfo_screenwidth() - 300}+16")

tk.Label(root, text="📋 AltraPaste — GCE Altra Guide", bg="#0f172a", fg="#93c5fd",
         font=("Segoe UI", 10, "bold")).pack(padx=14, pady=(10, 2))

status = tk.Button(root, text="", font=("Segoe UI", 13, "bold"), fg="white",
                   relief="flat", cursor="hand2", command=lambda: toggle())
status.pack(padx=14, pady=4, fill="x")

tk.Label(root, text="Klik KANAN = tampal terus  ·  Shift+Kanan = menu biasa\n"
                    "F8 = ON/OFF  ·  Tutup tetingkap ini untuk berhenti",
         bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 8), justify="center"
         ).pack(padx=14, pady=(2, 10))


def update_ui():
    if enabled.is_set():
        status.config(text="PASTE MODE: ON  ✔", bg=ON_BG, activebackground=ON_BG)
    else:
        status.config(text="PASTE MODE: OFF", bg=OFF_BG, activebackground=OFF_BG)


def toggle():
    if enabled.is_set():
        enabled.clear()
    else:
        enabled.set()
    update_ui()


update_ui()
threading.Thread(target=hook_thread, daemon=True).start()
root.mainloop()
