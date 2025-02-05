import tkinter as tk
from tkinter import ttk, messagebox
import pywinctl
import win32gui
import win32con
import ctypes
import sys
import subprocess
import psutil  # 用于获取进程名称


class WindowManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("窗口置顶工具 (管理员权限)")

        self.windows = []  # 存储(标题, 句柄, 是否置顶)的列表

        # 创建列表框和滚动条
        self.listbox_frame = ttk.Frame(self.root)
        self.listbox_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(self.listbox_frame, width=80, height=25)
        self.scrollbar = ttk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.scrollbar.set)

        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定双击事件
        self.listbox.bind('<Double-Button-1>', self.on_double_click)

        # 按钮区域
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=5, fill=tk.X)

        self.refresh_btn = ttk.Button(self.button_frame, text="刷新列表", command=self.refresh_windows)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        self.topmost_btn = ttk.Button(self.button_frame, text="置顶窗口", command=self.set_topmost)
        self.topmost_btn.pack(side=tk.LEFT, padx=5)

        self.untopmost_btn = ttk.Button(self.button_frame, text="取消置顶", command=self.remove_topmost)
        self.untopmost_btn.pack(side=tk.LEFT, padx=5)

        # 说明区域
        self.instructions = tk.Label(
            self.root,
            text="操作方法：\n"
                 "1. 双击窗口名称 → 聚焦窗口\n"
                 "2. 选中窗口后点击“置顶窗口” → 使窗口置顶\n"
                 "3. 选中窗口后点击“取消置顶” → 取消窗口置顶\n"
                 "4. 自动检测当前焦点窗口，并用红色高亮\n"
                 "5. 任务栏上可见的窗口才会显示\n"
                 "6. 刷新列表会保持滚动位置和选中项\n\n"
                 "Made by mcbaoge © 2025",  # 官方风格的制作信息
            justify="left",  # 左对齐
            anchor="w",  # 文字靠左
            padx=10,  # 增加内边距
            fg="blue",  # 让文字更醒目
            font=("Segoe UI", 10, "bold")  # Windows 官方风格字体
        )
        self.instructions.pack(fill=tk.X, padx=10, pady=5)

        # 初始化刷新
        self.refresh_windows()
        self.schedule_refresh()

    def schedule_refresh(self):
        """每隔1秒刷新窗口列表"""
        self.refresh_windows()
        self.root.after(500, self.schedule_refresh)  # 每隔1秒调用一次

    def refresh_windows(self):
        """刷新窗口列表，并保持用户选中的项目、滚动位置，同时高亮当前焦点窗口"""
        selected_hwnd = None
        scroll_position = self.listbox.yview()  # 记录当前滚动条位置
        foreground_hwnd = win32gui.GetForegroundWindow()  # 获取当前焦点窗口的句柄

        # 记录当前选中的窗口句柄
        selection = self.listbox.curselection()
        if selection:
            selected_hwnd = self.windows[selection[0]][1]  # 获取当前选中的窗口句柄

        self.listbox.delete(0, tk.END)
        self.windows.clear()

        try:
            # 获取所有窗口并过滤
            all_windows = pywinctl.getAllWindows()
            valid_windows = []
            for win in all_windows:
                # 判断窗口是否显示在任务栏上
                style = win32gui.GetWindowLong(win._hWnd, win32con.GWL_STYLE)
                if win.title.strip() and win.isVisible and (style & win32con.WS_EX_APPWINDOW):
                    valid_windows.append(
                        (win.title.strip(), win._hWnd, self.is_window_topmost(win._hWnd))
                    )

            # 按标题排序
            valid_windows.sort(key=lambda x: x[0].lower())

            # 添加到列表
            new_selection_index = None
            for index, (title, hwnd, is_topmost) in enumerate(valid_windows):
                process_name = self.get_process_name_by_hwnd(hwnd)
                display_text = f"[{process_name}] {title}"
                self.windows.append((title, hwnd, is_topmost))
                self.listbox.insert(tk.END, display_text)

                # 设置颜色：焦点窗口 -> 红色，置顶窗口 -> 黄色
                if hwnd == foreground_hwnd:
                    self.listbox.itemconfig(index, {'bg': 'red', 'fg': 'white'})  # 焦点窗口
                elif is_topmost:
                    self.listbox.itemconfig(index, {'bg': 'lightyellow'})  # 置顶窗口

                # 恢复之前的选中项
                if selected_hwnd and hwnd == selected_hwnd:
                    new_selection_index = index

            # 重新选中用户之前选中的窗口
            if new_selection_index is not None:
                self.listbox.selection_set(new_selection_index)
                self.listbox.activate(new_selection_index)  # 让选中的项高亮显示
                self.listbox.see(new_selection_index)  # 确保选中的项在可见区域

            # 恢复滚动位置
            self.listbox.yview_moveto(scroll_position[0])

            # 更新按钮状态
            self.update_button_states()

        except Exception as e:
            messagebox.showerror("错误", f"获取窗口失败: {e}")

    def get_process_name_by_hwnd(self, hwnd):
        """通过窗口句柄获取进程名称"""
        try:
            pid = win32gui.GetWindowThreadProcessId(hwnd)[1]
            process = psutil.Process(pid)
            return process.name()
        except Exception:
            return "Unknown"

    def is_window_topmost(self, hwnd):
        """判断窗口是否置顶"""
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        return bool(style & win32con.WS_EX_TOPMOST)

    def get_selected_hwnd(self):
        """获取当前选中的窗口句柄"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先在列表中选择一个窗口")
            return None
        return self.windows[selection[0]][1]

    def on_double_click(self, event):
        """双击聚焦窗口"""
        if hwnd := self.get_selected_hwnd():
            try:
                # 恢复窗口（如果最小化）
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # 切换到该窗口
                ctypes.windll.user32.SwitchToThisWindow(hwnd, True)
            except Exception as e:
                messagebox.showerror("错误", f"聚焦窗口失败: {e}")

    def set_topmost(self):
        """设置窗口置顶"""
        if hwnd := self.get_selected_hwnd():
            try:
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                )
                self.refresh_windows()  # 刷新列表以更新状态
            except Exception as e:
                messagebox.showerror("错误", f"置顶失败: {e}")

    def remove_topmost(self):
        """取消窗口置顶"""
        if hwnd := self.get_selected_hwnd():
            try:
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                )
                self.refresh_windows()  # 刷新列表以更新状态
            except Exception as e:
                messagebox.showerror("错误", f"取消置顶失败: {e}")

    def update_button_states(self):
        """根据选中窗口的置顶状态更新按钮状态"""
        selection = self.listbox.curselection()
        if not selection:
            self.topmost_btn.config(state=tk.NORMAL)
            self.untopmost_btn.config(state=tk.NORMAL)
            return

        hwnd = self.windows[selection[0]][1]
        is_topmost = self.is_window_topmost(hwnd)

        if is_topmost:
            self.topmost_btn.config(state=tk.DISABLED)
            self.untopmost_btn.config(state=tk.NORMAL)
        else:
            self.topmost_btn.config(state=tk.NORMAL)
            self.untopmost_btn.config(state=tk.DISABLED)


def run_as_admin():
    """检测是否以管理员权限运行，如果没有则重新以管理员权限启动"""
    if ctypes.windll.shell32.IsUserAnAdmin():
        return  # 已是管理员，不需要提升权限

    # 重新启动并请求管理员权限
    try:
        exe_path = sys.executable  # 当前 Python 解释器路径
        script_path = sys.argv[0]  # 当前脚本路径
        subprocess.run(["powershell", "Start-Process", exe_path, f'-ArgumentList "{script_path}"', "-Verb", "RunAs"],
                       creationflags=subprocess.CREATE_NO_WINDOW)  # 隐藏cmd窗口
        sys.exit()  # 关闭当前进程
    except Exception as e:
        messagebox.showerror("错误", f"无法以管理员身份运行: {e}")
        sys.exit()


if __name__ == "__main__":
    run_as_admin()  # 确保以管理员权限运行
    root = tk.Tk()
    app = WindowManagerApp(root)
    root.mainloop()