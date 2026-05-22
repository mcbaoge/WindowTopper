import ctypes
from ctypes import wintypes
from dataclasses import dataclass, field
from typing import List, Optional

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_SHOWWINDOW = 0x0040
WS_EX_TOPMOST = 0x00000008
GWL_EXSTYLE = -20

ENUM_CALLBACK = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


@dataclass
class WindowInfo:
    hwnd: int
    title: str
    class_name: str
    is_visible: bool
    is_topmost: bool
    parent_hwnd: Optional[int] = None
    children: List['WindowInfo'] = field(default_factory=list)
    depth: int = 0
    process_id: int = 0
    process_name: str = ''


def get_window_text(hwnd):
    length = user32.GetWindowTextLengthW(hwnd) + 1
    buffer = ctypes.create_unicode_buffer(length)
    user32.GetWindowTextW(hwnd, buffer, length)
    return buffer.value


def get_class_name(hwnd):
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buffer, 256)
    return buffer.value


def get_window_long(hwnd, index):
    return user32.GetWindowLongW(hwnd, index)


def is_window_topmost(hwnd):
    ex_style = get_window_long(hwnd, GWL_EXSTYLE)
    return (ex_style & WS_EX_TOPMOST) != 0


def get_process_id(hwnd):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def get_process_name(pid):
    handle = kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
    if not handle:
        return ''
    try:
        buffer = ctypes.create_unicode_buffer(260)
        size = wintypes.DWORD(260)
        if kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
            return buffer.value.rsplit('\\', 1)[-1]
        return ''
    finally:
        kernel32.CloseHandle(handle)


def enum_child_windows(parent_hwnd, depth=1):
    children = []
    hwnd_child = user32.GetWindow(parent_hwnd, 5)
    while hwnd_child:
        title = get_window_text(hwnd_child)
        class_name = get_class_name(hwnd_child)
        is_visible = user32.IsWindowVisible(hwnd_child)
        if title or (is_visible and class_name not in ('', 'Shell_InputPane', 'ApplicationManager_DesktopShellWindow')):
            pid = get_process_id(hwnd_child)
            info = WindowInfo(
                hwnd=hwnd_child,
                title=title,
                class_name=class_name,
                is_visible=is_visible,
                is_topmost=is_window_topmost(hwnd_child),
                parent_hwnd=parent_hwnd,
                depth=depth,
                process_id=pid,
                process_name=get_process_name(pid),
            )
            info.children = enum_child_windows(hwnd_child, depth + 1)
            children.append(info)
        hwnd_child = user32.GetWindow(hwnd_child, 2)
    return children


def enum_windows():
    windows = []

    def callback(hwnd, lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        title = get_window_text(hwnd)
        class_name = get_class_name(hwnd)
        parent = user32.GetParent(hwnd)
        if parent:
            return True

        if not title:
            return True

        if class_name in ('Windows.UI.Core.CoreWindow', 'ApplicationFrameWindow',
                          'Shell_TrayWnd', 'Shell_SecondaryTrayWnd'):
            pass

        pid = get_process_id(hwnd)
        info = WindowInfo(
            hwnd=hwnd,
            title=title,
            class_name=class_name,
            is_visible=True,
            is_topmost=is_window_topmost(hwnd),
            parent_hwnd=None,
            depth=0,
            process_id=pid,
            process_name=get_process_name(pid),
        )
        info.children = enum_child_windows(hwnd, 1)
        windows.append(info)
        return True

    proto = ENUM_CALLBACK(callback)
    user32.EnumWindows(proto, 0)
    return windows


user32.SetWindowPos.argtypes = [
    wintypes.HWND, wintypes.HWND,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_uint,
]
user32.SetWindowPos.restype = wintypes.BOOL


SWP_NOACTIVATE = 0x0010
SWP_DEFERERASE = 0x2000
SWP_ASYNCWINDOWPOS = 0x4000


def set_window_topmost(hwnd, topmost=True):
    hwnd_insert = wintypes.HWND(HWND_TOPMOST if topmost else HWND_NOTOPMOST)
    hwnd = wintypes.HWND(hwnd)
    flags = SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_DEFERERASE
    user32.SetWindowPos(hwnd, hwnd_insert, 0, 0, 0, 0, flags)
    return is_window_topmost(hwnd)


def get_foreground_window():
    return user32.GetForegroundWindow()


class POINT(ctypes.Structure):
    _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ('pt', POINT),
        ('mouseData', ctypes.c_uint),
        ('flags', ctypes.c_uint),
        ('time', ctypes.c_uint),
        ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong)),
    ]


WH_MOUSE_LL = 14
WM_LBUTTONDOWN = 0x201

HOOKPROC = ctypes.WINFUNCTYPE(wintypes.LPARAM, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, ctypes.c_uint]
user32.SetWindowsHookExW.restype = wintypes.HHOOK
user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
user32.CallNextHookEx.restype = wintypes.LPARAM
user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL
user32.WindowFromPoint.argtypes = [POINT]
user32.WindowFromPoint.restype = wintypes.HWND


class WindowPicker:
    def __init__(self, own_hwnd, on_pick):
        self._own_hwnd = own_hwnd
        self._on_pick = on_pick
        self._hook = None
        self._proc = None

    def start(self):
        if self._hook:
            return
        self._proc = HOOKPROC(self._hook_proc)
        self._hook = user32.SetWindowsHookExW(WH_MOUSE_LL, self._proc, None, 0)
        return self._hook is not None

    def stop(self):
        if self._hook:
            user32.UnhookWindowsHookEx(self._hook)
            self._hook = None
            self._proc = None

    @property
    def is_active(self):
        return self._hook is not None

    def _hook_proc(self, nCode, wParam, lParam):
        if nCode >= 0 and wParam == WM_LBUTTONDOWN:
            struct = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
            pt = struct.pt
            hwnd = user32.WindowFromPoint(pt)
            if hwnd and hwnd != self._own_hwnd:
                self._on_pick(hwnd)
                self.stop()
                return 1
        return user32.CallNextHookEx(self._hook, nCode, wParam, lParam)
