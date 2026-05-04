# Migration Plan: CustomTkinter to PySide6 (Qt)

This document outlines the strategy for refactoring the JableTV & MissAV Downloader from its current `customtkinter` implementation to an industrial-grade PySide6 (Qt) architecture.

## 1. Core GUI File Mapping

| Current File | Role | Migration Target | Priority |
| :--- | :--- | :--- | :--- |
| `gui_modern.py` | Main App & Tabs | `MainWindow.ui` + `main_window.py` | **Critical** |
| `browser.py` | Video Grid & Sidebar | `BrowsePanel.ui` + `browse_panel.py` | **High** |
| `mywidget.py` | Custom ListViews | Custom `QTreeView` or `QTableWidget` | **Medium** |
| `gui.py` | Legacy UI | Deprecate or replace with Main UI | **Low** |
| `jable_smalltool.py` | Standalone Utility | `SmallTool.ui` + `smalltool.py` | **Low** |

## 2. Widget Mapping Table

| CustomTkinter / Tkinter Widget | PySide6 (Qt) Equivalent | Advantages |
| :--- | :--- | :--- |
| `ctk.CTk` | `QMainWindow` | Native window management, built-in menu/status bars. |
| `ctk.CTkTabview` | `QTabWidget` | Faster switching, native look and feel. |
| `ctk.CTkScrollableFrame` | `QScrollArea` + `QWidget` | Smoother scrolling, better memory management. |
| `ctk.CTkButton` | `QPushButton` | CSS-like styling via QSS, native hover/click states. |
| `tk.Label` (Thumbnails) | `QLabel` + `QPixmap` | High-performance image rendering and scaling. |
| `ttk.Treeview` | `QTreeView` / `QTableView` | Robust data binding, built-in sorting/filtering. |
| `RedirectConsole` (Listbox) | `QPlainTextEdit` | Better performance for high-frequency log updates. |

## 3. Architectural Suggestions

### A. Signal/Slot Pattern
Replace the current callback-heavy system (e.g., `_on_progress`) with Qt's **Signals and Slots**. 
- The `DownloadManager` should emit a `progress_updated(url, pct, speed)` signal.
- The UI connects to this signal to update the progress bars without blocking the main thread.

### B. Multi-Threading (QThread)
CustomTkinter currently uses standard `threading.Thread`. In PySide6, using `QThread` or `QRunnable` with `QThreadPool` is recommended for:
1. **Thumbnail Fetching**: Prevents "pop-in" lag during grid scrolling.
2. **Scraping**: Keeps the UI responsive while waiting for network responses.

### C. Resource Management (QSS)
Instead of hardcoding colors like `ACCENT = '#e94560'` in Python, use a **Qt Style Sheet (QSS)**.
- This allows you to swap themes (Dark/Light) or change the branding without touching the Python logic.

### D. Componentization (The "Video Card")
The `VideoCard` in `browser.py` is currently a `tk.Frame`. In Qt:
- Create a `VideoCard.ui` file.
- Implement a `VideoCard(QWidget)` class that loads this UI.
- This makes the grid logic much cleaner and allows for easier animation effects (e.g., smooth zoom on hover).

## 4. Performance Optimizations

1. **Lazy Loading**: Only fetch and render thumbnails that are currently visible in the `QScrollArea`.
2. **Image Caching**: Use `QCache` or a simple dictionary of `QPixmap` to avoid re-decoding images when scrolling back up.
3. **Async Network**: Use `QNetworkAccessManager` for fetching thumbnails; it's non-blocking and handles multiple requests efficiently.

## 5. Proposed Project Structure (Post-Migration)
```text
/
├── ui/                 # .ui files created in Qt Designer
│   ├── main_window.ui
│   ├── browse_panel.ui
│   └── video_card.ui
├── modules/            # Refactored logic
│   ├── downloader.py   # DownloadManager (Logic only)
│   ├── scraper.py      # Site browsers (Logic only)
│   └── signals.py      # Global communication signals
├── widgets/            # Custom Qt classes
│   ├── video_card.py
│   └── log_viewer.py
└── main.py             # App entry point
```
