# Technical Audit & Bug Report

This document identifies potential issues, architectural weaknesses, and bugs discovered during the analysis of the JableTV & MissAV Downloader codebase.

## 1. Bug Tracking & Criticality

| ID | Issue | Criticality | Status | Description |
| :--- | :--- | :--- | :--- | :--- |
| **B01** | Filename Sanitization | `CRITICAL` | [x] DONE | Strips CJK characters (Chinese/Japanese/Korean) from titles. |
| **B02** | Thread-Safety / Race Condition | `HIGH` | [x] DONE | Background threads writing to state while UI thread reads. |
| **B03** | Resource Leakage (Disk Bloat) | `HIGH` | [x] DONE | Temporary fragments not cleaned up on cancel/failure. |
| **B04** | Error Handling / Retry Logic | `MEDIUM` | [x] DONE | Doesn't distinguish between fatal (404) and transient (5xx) errors. |
| **B05** | UI Update Bottleneck | `MEDIUM` | [x] DONE | UI stuttering when the download list grows large. |
| **B06** | Speed Limiter Contention | `LOW` | [x] DONE | Global lock can slightly degrade performance at high concurrency. |

## 2. Detailed Technical Analysis

### B01: Filename Sanitization (Localization)
*   **Location**: `M3U8Sites/M3U8Crawler.py:134`
*   **Impact**: Loss of descriptive titles for almost all content.
*   **Suggested Fix**: Update regex to `[^\w\-_\. \u4e00-\u9fff\u3040-\u30ff\u31f0-\u31ff\uff00-\uffef]`.

### B02: Thread-Safety & Race Conditions
*   **Location**: `gui_modern.py` & `DownloadManager`
*   **Impact**: Potential intermittent crashes or UI "glitches".
*   **Suggested Fix**: Implement thread-safe property updates.

### B03: Resource Leakage
*   **Location**: `M3U8Sites/M3U8Crawler.py:271`
*   **Impact**: Gigabytes of wasted disk space from partial downloads.
*   **Suggested Fix**: Add `shutil.rmtree` in `cancel_download` and on app startup.

### A. Error Handling & Retry Logic
*   **Issue**: The crawler's `_scrape` method uses a blanket `try...except Exception`. 
*   **Description**: It doesn't distinguish between a **404 Not Found** (which should stop the download) and a **503 Service Unavailable** or **Timeout** (which should trigger a longer delay or retry). 
*   **Impact**: Transient network glitches can cause a segment to fail permanently, resulting in a corrupted final video merge.

### B. UI Update Bottleneck
*   **Issue**: Frequency of `_refresh_downloads` and `_update_dl_row`.
*   **Description**: `_refresh_downloads` runs every 1000ms and calls `configure()` on multiple labels and progress bars for *every* item in the list. 
*   **Impact**: As the download list grows, this will cause visible stuttering in the "Modern" UI because `customtkinter` (and `tkinter`) UI updates are computationally expensive on the main thread.

### C. Speed Limiter Contention
*   **Issue**: Global token-bucket lock.
*   **Description**: The `speed_limiter` uses a single lock shared across all segments of all concurrent downloads.
*   **Impact**: With high concurrency (e.g., 32 segments at once), threads will spend significant time waiting for the lock rather than downloading data, artificially capping performance below the requested limit.

## 3. UI/UX Suggestions

| Feature | Current State | Suggested Improvement |
| :--- | :--- | :--- |
| **Clipboard** | Polls every 800ms. | Use a native Clipboard Listener (Windows API) to reduce CPU wakeups. |
| **Merging** | Simple binary append. | Use `ffmpeg` for merging to ensure stream consistency and better container metadata. |
| **Search** | Hardcoded base URLs. | Move URLs to `config.py` to allow easy updates when sites change domains. |
| **Status Bar** | Simple text. | Add a total speed indicator and disk space warning. |

## 4. Immediate Action Items

1. [ ] **Fix Regex**: Update `M3U8Crawler.py` to support CJK characters in filenames.
2. [ ] **Error Logic**: Enhance `_scrape` to handle HTTP 429 (Rate Limit) and 5xx errors gracefully.
3. [ ] **Cleanup**: Add a "Purge Temp Files" button in Settings.
4. [ ] **Qt Migration**: Prioritize moving the `VideoCard` grid to PySide6 to solve the UI stuttering described in issue 2B.
