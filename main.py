from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import requests

FAX_DIR = r"C:\Users\YourUsername\Documents\Fax"
TOKEN_URL = "https://example.com/token"        # JWT 로그인 엔드포인트
API_URL = "https://example.com/api/fax/received"  # 실제 호출할 API

# 로그인 정보
LOGIN_DATA = {
    "grant_type": "password",
    "username": "your_username",
    "password": "your_password",
}

class FaxHandler(FileSystemEventHandler):
    def __init__(self):
        self.token = self.get_token()

    def get_token(self):
        try:
            response = requests.post(
                TOKEN_URL,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=LOGIN_DATA
            )
            response.raise_for_status()
            token = response.json().get("access_token")
            if not token:
                raise ValueError("❌ 토큰 응답에 access_token 없음")
            return token
        except Exception as e:
            with open("fax_error.log", "a", encoding="utf-8") as log:
                log.write(f"{time.ctime()} - 토큰 획득 실패: {e}\n")
            return None

    def on_created(self, event):
        if not event.is_directory:
            time.sleep(1)
            if not self.token:
                self.token = self.get_token()
                if not self.token:
                    return

            headers = {"Authorization": f"Bearer {self.token}"}
            try:
                res = requests.post(API_URL, json={"file_path": event.src_path}, headers=headers)
                if res.status_code == 401:
                    # 토큰 만료 시 재발급
                    self.token = self.get_token()
                    if self.token:
                        headers = {"Authorization": f"Bearer {self.token}"}
                        requests.post(API_URL, json={"file_path": event.src_path}, headers=headers)
                elif res.status_code >= 400:
                    raise Exception(f"API 에러: {res.status_code} - {res.text}")
            except Exception as e:
                with open("fax_error.log", "a", encoding="utf-8") as log:
                    log.write(f"{time.ctime()} - API 호출 실패: {e}\n")

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
