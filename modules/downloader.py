import os
import threading
import csv
from PySide6.QtCore import QObject, Signal
import M3U8Sites

DEFAULT_CONCURRENT = 2
MAX_CONCURRENT = 10

class DownloadItem:
    def __init__(self, url: str, name: str = '', state: str = ''):
        self.url = url
        self.name = name or url.rstrip('/').split('/')[-1]
        self.state = state
        self.progress = 0
        self.speed = ''
        self._lock = threading.RLock()

class DownloadManager(QObject):
    """Refactored Qt-native download manager using Signals & Slots."""
    
    # Signals for UI communication
    stateChanged = Signal(str, str, str) # url, state, name
    progressUpdated = Signal(str, int, str) # url, progress, speed
    listChanged = Signal()
    
    def __init__(self, max_concurrent: int = DEFAULT_CONCURRENT):
        super().__init__()
        self._pending = []
        self._active = {}
        self._items = {}
        self._lock = threading.RLock()
        self._max_concurrent = max_concurrent
        self._prep_sem = threading.Semaphore(1)

    @property
    def max_concurrent(self) -> int:
        return self._max_concurrent

    @max_concurrent.setter
    def max_concurrent(self, value: int):
        self._max_concurrent = max(1, min(value, MAX_CONCURRENT))
        for _ in range(value):
            self._try_next()

    def add_item(self, url: str, name: str = '', state: str = ''):
        with self._lock:
            if url not in self._items:
                self._items[url] = DownloadItem(url, name, state)
                self.listChanged.emit()

    def get_items(self) -> list[DownloadItem]:
        with self._lock:
            return list(self._items.values())

    def enqueue(self, url: str, dest: str):
        with self._lock:
            if url in self._active:
                return
            if any(u == url for u, _ in self._pending):
                return
            
            if len(self._active) < self._max_concurrent:
                self._active[url] = None
                threading.Thread(target=self._run, args=(url, dest), daemon=True).start()
            else:
                self._pending.append((url, dest))
                self._set_state(url, 'state_waiting')

    def _run(self, url: str, dest: str):
        self._set_state(url, 'state_preparing')
        try:
            self._prep_sem.acquire()
            try:
                job = M3U8Sites.CreateSite(url, dest)
            finally:
                self._prep_sem.release()
                
            if not job or not job.is_url_vaildate():
                with self._lock:
                    self._active.pop(url, None)
                self._set_state(url, 'state_bad_url')
                self._try_next()
                return
                
            with self._lock:
                self._active[url] = job
            
            name = job.target_name() or ''
            self._set_state(url, 'state_downloading', name=name)
            
            job._progress_callback = lambda d, t, s: self._on_progress(url, d, t, s)
            job.start_download()
            
            with self._lock:
                self._active.pop(url, None)
                
            if job._cancel_job:
                self._set_state(url, 'state_cancelled')
            else:
                self._set_state(url, 'state_downloaded', progress=100)
        except Exception as exc:
            print(f'[Downloader] Error: {exc}')
            with self._lock:
                self._active.pop(url, None)
            self._set_state(url, 'state_unfinished')
        self._try_next()

    def _try_next(self):
        with self._lock:
            if not self._pending or len(self._active) >= self._max_concurrent:
                return
            url, dest = self._pending.pop(0)
            self._active[url] = None
        threading.Thread(target=self._run, args=(url, dest), daemon=True).start()

    def _set_state(self, url: str, state: str, name: str = '', progress: int = -1):
        with self._lock:
            item = self._items.get(url)
            if item:
                with item._lock:
                    item.state = state
                    if name: item.name = name
                    if progress >= 0: item.progress = progress
                self.stateChanged.emit(url, state, item.name)

    def _on_progress(self, url: str, done: int, total: int, speed_bps: float):
        if total <= 0: return
        pct = int(done * 100 / total)
        spd = (f'{speed_bps / 1024:.0f} KB/s' if speed_bps < 1024 * 1024
               else f'{speed_bps / 1024 / 1024:.1f} MB/s')
        with self._lock:
            item = self._items.get(url)
            if item:
                with item._lock:
                    item.progress = pct
                    item.speed = spd
                self.progressUpdated.emit(url, pct, spd)

    def save_csv(self, path: str):
        with self._lock:
            items = list(self._items.values())
        with open(path, 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['狀態', '名稱', '進度', '速度', '網址'])
            for item in items:
                w.writerow([item.state, item.name, f'{item.progress}%', item.speed, item.url])

    def load_csv(self, path: str):
        if not os.path.exists(path): return
        with open(path, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                url = row.get('網址', '')
                if url:
                    self.add_item(url, row.get('名稱', ''), row.get('狀態', ''))
