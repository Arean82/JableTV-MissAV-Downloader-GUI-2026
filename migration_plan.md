# Migration Plan: CustomTkinter to PySide6 (Qt)

This document outlines the strategy for refactoring the JableTV & MissAV Downloader from its current `customtkinter` implementation to an industrial-grade PySide6 (Qt) architecture.

## 1. Core GUI File Mapping

| Current File           | Role                 | Migration Target                         | Priority           |
| :--------------------- | :------------------- | :--------------------------------------- | :----------------- |
| `gui_modern.py`      | Main App & Tabs      | `MainWindow.ui` + `main_window.py`   | **Critical** |
| `browser.py`         | Video Grid & Sidebar | `BrowsePanel.ui` + `browse_panel.py` | **High**     |
| `mywidget.py`        | Custom ListViews     | Custom `QTreeView` or `QTableWidget` | **Medium**   |
| `gui.py`             | Legacy UI            | Deprecate or replace with Main UI        | **Low**      |
| `jable_smalltool.py` | Standalone Utility   | `SmallTool.ui` + `smalltool.py`      | **Low**      |

## 2. Widget Mapping Table

| CustomTkinter / Tkinter Widget | PySide6 (Qt) Equivalent        | Advantages                                           |
| :----------------------------- | :----------------------------- | :--------------------------------------------------- |
| `ctk.CTk`                    | `QMainWindow`                | Native window management, built-in menu/status bars. |
| `ctk.CTkTabview`             | `QTabWidget`                 | Faster switching, native look and feel.              |
| `ctk.CTkScrollableFrame`     | `QScrollArea` + `QWidget`  | Smoother scrolling, better memory management.        |
| `ctk.CTkButton`              | `QPushButton`                | CSS-like styling via QSS, native hover/click states. |
| `tk.Label` (Thumbnails)      | `QLabel` + `QPixmap`       | High-performance image rendering and scaling.        |
| `ttk.Treeview`               | `QTreeView` / `QTableView` | Robust data binding, built-in sorting/filtering.     |
| `RedirectConsole` (Listbox)  | `QPlainTextEdit`             | Better performance for high-frequency log updates.   |

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

## 6. Migration Progress Roadmap

### Phase 1: Foundation [COMPLETED]

- [X] Set up PySide6 environment.
- [X] Create project structure: `ui/` for XML, `widgets/` for logic.
- [X] Integrate existing `locales.py` for dynamic translation.

### Phase 2: Core UI Construction [COMPLETED]

- [X] **MainWindow**: Modular shell with tab management. [DONE]
- [X] **Settings Tab**: Form-based configuration with live language swap. [DONE]
- [X] **Download Tab**: High-performance "Card" architecture for the queue. [DONE]
- [X] **Browse Tab**: Thumbnail grid with lazy loading. [DONE]

### Phase 3: Logic & Threading [COMPLETED]
- [x] **Signal Migration**: Convert `DownloadManager` callbacks to Qt Signals. [DONE]
- [x] **Thread Management**: Use `QThread` for background scrapers. [DONE]
- [x] **Clipboard Monitor**: Replace `after()` loop with `QClipboard` listener. [DONE]

### Phase 4: Polish [COMPLETED]
- [x] Apply global QSS for "Modern Dark" aesthetic. [DONE]
- [x] Add loading animations (Smooth Spinner). [DONE]
- [x] Image Caching for thumbnails. [DONE]
- [x] Dual Themes (Dark & Light) with Menu Bar toggle. [DONE]
- [x] Native Menu Bar integration. [DONE]
- [x] JSON-based dynamic localization. [DONE]

## Summary of Migration
The JableTV & MissAV Downloader has been successfully migrated to **PySide6 (Qt)**. 
- **Performance**: High (Hardware accelerated).
- **Architecture**: Modular (Separated UI, Logic, and Models).
- **Usability**: Enhanced (Dual themes, Menu bar, Instant clipboard detection).
