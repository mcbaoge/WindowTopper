import ctypes
import winreg

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton, QLabel, QHeaderView,
    QCheckBox, QLineEdit, QAbstractItemView, QStatusBar, QFrame,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QColor, QBrush

from win_manager import (
    enum_windows, set_window_topmost, get_foreground_window, is_window_topmost,
    get_window_text, get_class_name, WindowInfo, WindowPicker,
)
from fluent_style import FLUENT_STYLE, FLUENT_DARK_STYLE


HWND_ROLE = Qt.UserRole + 1
TOPMOST_ROLE = Qt.UserRole + 2
DEPTH_ROLE = Qt.UserRole + 3
FOCUSED_ROLE = Qt.UserRole + 4
WIN_INFO_ROLE = Qt.UserRole + 5
DISPLAY_TITLE_ROLE = Qt.UserRole + 6


def _count_descendants(win):
    count = 0
    for c in win.children:
        count += 1 + _count_descendants(c)
    return count

COLOR_NORMAL = QColor("#1a1a1a")
COLOR_TOPMOST = QColor("#0078d4")
COLOR_FOCUSED = QColor("#ff8c00")
COLOR_TOPMOST_FOCUSED = QColor("#b84d00")
COLOR_CHILD_NORMAL = QColor("#666666")
COLOR_CHILD_TOPMOST = QColor("#4a9bd6")

DARK_COLOR_NORMAL = QColor("#e0e0e0")
DARK_COLOR_TOPMOST = QColor("#4fc3f7")
DARK_COLOR_FOCUSED = QColor("#ffb300")
DARK_COLOR_TOPMOST_FOCUSED = QColor("#ff8f00")
DARK_COLOR_CHILD_NORMAL = QColor("#999999")
DARK_COLOR_CHILD_TOPMOST = QColor("#4fc3f7")


class WindowTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(4)
        self.setHeaderLabels(['窗口名称', '进程', '类名', '状态'])
        self.setIndentation(20)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setRootIsDecorated(True)
        self.setAnimated(True)
        self.setSortingEnabled(False)
        self.setMouseTracking(True)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.itemDoubleClicked.connect(self._on_double_click)
        self.itemExpanded.connect(self._on_item_expanded)
        self.itemCollapsed.connect(self._on_item_collapsed)
        self._is_dark = False

    def set_dark_mode(self, dark):
        self._is_dark = dark
        self._recolor_all()

    def _on_item_expanded(self, item):
        base = item.data(0, DISPLAY_TITLE_ROLE)
        if base:
            item.setText(0, base)

    def _on_item_collapsed(self, item):
        base = item.data(0, DISPLAY_TITLE_ROLE)
        if base and item.childCount() > 0:
            total = self._count_visible_children(item)
            item.setText(0, f"{base}  [{total}个子窗口]")

    def _count_visible_children(self, item):
        count = 0
        for i in range(item.childCount()):
            count += 1
            count += self._count_visible_children(item.child(i))
        return count

    def _toggle_topmost_hwnd(self, hwnd, topmost):
        set_window_topmost(hwnd, topmost)
        for item in self.get_all_items():
            if item.data(0, HWND_ROLE) == hwnd:
                item.setData(0, TOPMOST_ROLE, topmost)
                self._apply_item_color(item)
                self._update_status_text(item)
                break

    def _on_double_click(self, item, column):
        self._toggle_topmost(item)

    def _toggle_topmost(self, item):
        hwnd = item.data(0, HWND_ROLE)
        current = item.data(0, TOPMOST_ROLE)
        new_state = set_window_topmost(hwnd, not current)
        item.setData(0, TOPMOST_ROLE, new_state)
        self._apply_item_color(item)
        self._update_status_text(item)

    def _update_status_text(self, item):
        is_topmost = item.data(0, TOPMOST_ROLE)
        item.setText(3, '● 置顶' if is_topmost else '')

    def _apply_item_color(self, item):
        is_topmost = item.data(0, TOPMOST_ROLE)
        is_focused = item.data(0, FOCUSED_ROLE)
        depth = item.data(0, DEPTH_ROLE)

        if self._is_dark:
            if is_focused and is_topmost:
                color = DARK_COLOR_TOPMOST_FOCUSED
            elif is_focused:
                color = DARK_COLOR_FOCUSED
            elif is_topmost:
                color = DARK_COLOR_TOPMOST
            else:
                color = DARK_COLOR_CHILD_NORMAL if depth > 0 else DARK_COLOR_NORMAL
        else:
            if is_focused and is_topmost:
                color = COLOR_TOPMOST_FOCUSED
            elif is_focused:
                color = COLOR_FOCUSED
            elif is_topmost:
                color = COLOR_TOPMOST
            else:
                color = COLOR_CHILD_NORMAL if depth > 0 else COLOR_NORMAL

        for col in range(self.columnCount()):
            item.setForeground(col, QBrush(color))
            font = item.font(col)
            font.setBold(is_focused or is_topmost)
            item.setFont(col, font)

    def _recolor_all(self):
        for item in self.get_all_items():
            self._apply_item_color(item)

    def update_window_list(self, windows, focused_hwnd):
        selected_hwnds = set()
        for item in self.selectedItems():
            hwnd = item.data(0, HWND_ROLE)
            if hwnd:
                selected_hwnds.add(hwnd)
        expanded_hwnds = set()
        self._collect_expanded(self, expanded_hwnds)
        self.clear()
        self._populate_tree(self, windows, focused_hwnd)
        if expanded_hwnds:
            self._restore_expanded(self, expanded_hwnds)
        if selected_hwnds:
            self._restore_selection(self, selected_hwnds)

    def _collect_expanded(self, parent, expanded_set):
        count = parent.topLevelItemCount() if parent is self else parent.childCount()
        for i in range(count):
            item = parent.topLevelItem(i) if parent is self else parent.child(i)
            if item.isExpanded():
                hwnd = item.data(0, HWND_ROLE)
                if hwnd:
                    expanded_set.add(hwnd)
            self._collect_expanded(item, expanded_set)

    def _restore_expanded(self, parent, expanded_set):
        count = parent.topLevelItemCount() if parent is self else parent.childCount()
        for i in range(count):
            item = parent.topLevelItem(i) if parent is self else parent.child(i)
            hwnd = item.data(0, HWND_ROLE)
            if hwnd in expanded_set:
                item.setExpanded(True)
            self._restore_expanded(item, expanded_set)

    def _restore_selection(self, parent, selected_hwnds):
        for i in range(parent.childCount() if parent is not self else parent.topLevelItemCount()):
            item = parent.child(i) if parent is not self else parent.topLevelItem(i)
            hwnd = item.data(0, HWND_ROLE)
            if hwnd in selected_hwnds:
                item.setSelected(True)
            self._restore_selection(item, selected_hwnds)

    def _populate_tree(self, parent, windows, focused_hwnd):
        for win in windows:
            item = QTreeWidgetItem(parent)
            depth = win.depth

            display_title = win.title if win.title else f"<{win.class_name}>"
            if depth > 0:
                indent = "  " * depth
                arrow = "└ " if win.title else "└ "
                display_title = f"{indent}{arrow}{display_title}"

            item.setText(0, display_title)
            item.setText(1, win.process_name)
            item.setText(2, win.class_name)

            is_topmost = win.is_topmost
            is_focused = (win.hwnd == focused_hwnd)
            item.setText(3, '● 置顶' if is_topmost else '')

            title_for_tip = win.title if win.title else f"<{win.class_name}>"
            if depth > 0:
                item.setToolTip(0, f"子窗口: {title_for_tip}\n类名: {win.class_name}\n进程: {win.process_name}\n句柄: {win.hwnd:#x}")
            else:
                item.setToolTip(0, f"顶层窗口: {title_for_tip}\n类名: {win.class_name}\n进程: {win.process_name}\n句柄: {win.hwnd:#x}")

            item.setData(0, HWND_ROLE, win.hwnd)
            item.setData(0, TOPMOST_ROLE, is_topmost)
            item.setData(0, DEPTH_ROLE, depth)
            item.setData(0, FOCUSED_ROLE, is_focused)
            item.setData(0, WIN_INFO_ROLE, win)
            item.setData(0, DISPLAY_TITLE_ROLE, display_title)

            self._apply_item_color(item)

            if win.children:
                self._populate_tree(item, win.children, focused_hwnd)
                total = _count_descendants(win)
                item.setText(0, f"{display_title}  [{total}个子窗口]")
                item.setExpanded(False)

    def update_focus_highlight(self, focused_hwnd):
        for i in range(self.topLevelItemCount()):
            self._update_item_focus(self.topLevelItem(i), focused_hwnd)

    def _update_item_focus(self, item, focused_hwnd):
        item_hwnd = item.data(0, HWND_ROLE)
        is_focused = (item_hwnd == focused_hwnd)
        item.setData(0, FOCUSED_ROLE, is_focused)
        self._apply_item_color(item)
        for i in range(item.childCount()):
            self._update_item_focus(item.child(i), focused_hwnd)

    def get_all_items(self):
        items = []
        for i in range(self.topLevelItemCount()):
            self._collect_items(self.topLevelItem(i), items)
        return items

    def _collect_items(self, item, items):
        items.append(item)
        for i in range(item.childCount()):
            self._collect_items(item.child(i), items)


def _is_system_dark_mode():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return value == 0
    except Exception:
        return False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows Topper - 窗口置顶管理器")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)
        self._is_dark = _is_system_dark_mode()
        self.setup_ui()
        self.setup_timer()
        self.apply_fluent_style(not self._is_dark)
        self.tree.set_dark_mode(self._is_dark)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(12, 4, 12, 4)
        title_layout.addStretch()

        self.pin_btn = QPushButton("📌 本窗口置顶中")
        self.pin_btn.setFixedHeight(28)
        self.pin_btn.setCheckable(True)
        self.pin_btn.setChecked(True)
        self.pin_btn.clicked.connect(self._toggle_self_topmost)
        title_layout.addWidget(self.pin_btn)

        self.theme_btn = QPushButton("☀️ 浅色模式" if self._is_dark else "🌙 深色模式")
        self.theme_btn.setFixedHeight(28)
        self.theme_btn.clicked.connect(self._toggle_theme)
        title_layout.addWidget(self.theme_btn)

        main_layout.addWidget(title_bar)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 12, 16, 12)
        content_layout.setSpacing(12)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        header_title = QWidget()
        header_title_layout = QVBoxLayout(header_title)
        header_title_layout.setContentsMargins(0, 0, 0, 0)
        header_title_layout.setSpacing(2)
        self.section_title = QLabel("窗口列表")
        self.section_title.setObjectName("sectionTitle")
        self.count_label = QLabel("")
        self.count_label.setObjectName("countLabel")
        header_title_layout.addWidget(self.section_title)
        header_title_layout.addWidget(self.count_label)
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setPlaceholderText("🔍 搜索窗口...")
        self.search_box.setMinimumWidth(200)
        self.search_box.setMaximumWidth(240)
        self.search_box.textChanged.connect(self._filter_windows)
        header_layout.addWidget(self.search_box)

        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(self.refresh_btn)

        self.auto_refresh_cb = QCheckBox("自动刷新")
        self.auto_refresh_cb.setChecked(True)
        header_layout.addWidget(self.auto_refresh_cb)

        content_layout.addWidget(header)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.HLine)
        content_layout.addWidget(sep)

        self.tree = WindowTreeWidget()
        content_layout.addWidget(self.tree)

        bottom_bar = QWidget()
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(0, 4, 0, 0)

        self.pick_btn = QPushButton("🎯 选取窗口")
        self.pick_btn.clicked.connect(self._start_picker)
        bottom_layout.addWidget(self.pick_btn)

        self.toggle_btn = QPushButton("切换选中窗口置顶状态")
        self.toggle_btn.setObjectName("accentButton")
        self.toggle_btn.clicked.connect(self._toggle_selected)
        bottom_layout.addWidget(self.toggle_btn)
        bottom_layout.addStretch()

        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(self._select_all)
        bottom_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton("取消全选")
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        bottom_layout.addWidget(self.deselect_all_btn)

        content_layout.addWidget(bottom_bar)

        main_layout.addWidget(content)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)

        self._picker = None

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._auto_refresh)
        self.timer.start()

        self.focus_timer = QTimer()
        self.focus_timer.setInterval(500)
        self.focus_timer.timeout.connect(self._track_focus)
        self.focus_timer.start()

        QTimer.singleShot(100, self._apply_self_topmost)

    def _apply_self_topmost(self):
        hwnd = int(self.winId())
        set_window_topmost(hwnd, True)

    def _toggle_self_topmost(self, checked):
        hwnd = int(self.winId())
        set_window_topmost(hwnd, checked)
        self.pin_btn.setText("📌 本窗口置顶中" if checked else "📌 本窗口未置顶")

    def _start_picker(self):
        if self._picker and self._picker.is_active:
            self._picker.stop()
            self.pick_btn.setText("🎯 选取窗口")
            self.status_label.setText("就绪")
            self.setWindowOpacity(1.0)
            return
        self._picker = WindowPicker(
            int(self.winId()),
            self._on_window_picked,
        )
        if self._picker.start():
            self.pick_btn.setText("✕ 取消选取")
            self.status_label.setText("请点击目标窗口...")
            self.setWindowOpacity(0.85)
        else:
            self.status_label.setText("选取器启动失败")

    def _on_window_picked(self, hwnd):
        title = get_window_text(hwnd) or f"<{get_class_name(hwnd)}>"
        topmost = is_window_topmost(hwnd)
        set_window_topmost(hwnd, not topmost)
        self.pick_btn.setText("🎯 选取窗口")
        self.setWindowOpacity(1.0)
        self.status_label.setText(
            f"已{'取消置顶' if topmost else '置顶'}: {title[:40]}")
        QTimer.singleShot(0, self.refresh)

    def _track_focus(self):
        focused_hwnd = get_foreground_window()
        if focused_hwnd:
            self.tree.update_focus_highlight(focused_hwnd)

    def _auto_refresh(self):
        if self.auto_refresh_cb.isChecked():
            self.refresh()

    def refresh(self):
        try:
            filter_text = self.search_box.text()
            windows = enum_windows()
            focused_hwnd = get_foreground_window()
            self.tree.update_window_list(windows, focused_hwnd)
            if filter_text:
                self._filter_windows(filter_text)
            count = len(self.tree.get_all_items())
            self.count_label.setText(f"共 {count} 个窗口")
            self.status_label.setText(f"已刷新 — {count} 个窗口")
        except Exception as e:
            self.status_label.setText(f"刷新失败: {e}")

    def _filter_windows(self, text):
        text = text.lower()
        for i in range(self.tree.topLevelItemCount()):
            self._filter_item(self.tree.topLevelItem(i), text)

    def _filter_item(self, item, text):
        win_info = item.data(0, WIN_INFO_ROLE)
        match = not text or (
            text in win_info.title.lower() or
            text in win_info.process_name.lower() or
            text in win_info.class_name.lower()
        )
        child_visible = False
        for i in range(item.childCount()):
            if self._filter_item(item.child(i), text):
                child_visible = True
        visible = match or child_visible
        item.setHidden(not visible)
        return visible

    def _toggle_selected(self):
        items = self.tree.selectedItems()
        if not items:
            QMessageBox.information(self, "提示", "请先选择窗口")
            return
        for item in items:
            hwnd = item.data(0, HWND_ROLE)
            current = item.data(0, TOPMOST_ROLE)
            new_state = set_window_topmost(hwnd, not current)
            item.setData(0, TOPMOST_ROLE, new_state)
            self.tree._apply_item_color(item)
            self.tree._update_status_text(item)

    def _select_all(self):
        self.tree.selectAll()

    def _deselect_all(self):
        self.tree.clearSelection()

    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        self.apply_fluent_style(not self._is_dark)
        self.tree.set_dark_mode(self._is_dark)
        self.theme_btn.setText("☀️ 浅色模式" if self._is_dark else "🌙 深色模式")
        self.refresh()

    def apply_fluent_style(self, light=True):
        if light:
            self.setStyleSheet(FLUENT_STYLE)
        else:
            self.setStyleSheet(FLUENT_DARK_STYLE)
