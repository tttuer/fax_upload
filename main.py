from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import requests

FAX_DIR = r"C:\Users\YourUsername\Documents\Fax"  # ← 실제 경로로 수정
API_ENDPOINT = ""

class FaxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(1)  # 파일 저장 지연 대비
            try:
                requests.post(API_ENDPOINT, json={"file_path": event.src_path})
            except Exception as e:
                with open("fax_error.log", "a", encoding="utf-8") as log:
                    log.write(f"{time.ctime()} - 오류: {e}\n")

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(FaxHandler(), path=FAX_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
