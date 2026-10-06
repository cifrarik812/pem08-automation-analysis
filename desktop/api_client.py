"""
API клиент для связи с backend
"""
import requests
from typing import Optional, Dict, Any
import base64
import mimetypes
from pathlib import Path


class APIClient:
    """Клиент для работы с API backend"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8008"):
        self.base_url = base_url
        self.timeout = 120  # 2 минуты для долгих операций
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Выполнить HTTP запрос"""
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault('timeout', self.timeout)
        
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Не удалось подключиться к серверу. Убедитесь, что backend запущен."}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Превышено время ожидания ответа от сервера."}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": f"HTTP ошибка: {e}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_health(self) -> bool:
        """Проверить доступность сервера"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Анализ текста конкурента"""
        return self._request(
            "POST",
            "/analyze_text",
            json={"text": text}
        )
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Анализ изображения конкурента"""
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (Path(image_path).name, f, mimetypes.guess_type(image_path)[0] or 'application/octet-stream')}
                return self._request("POST", "/analyze_image", files=files)
        except FileNotFoundError:
            return {"success": False, "error": "Файл не найден"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_image_bytes(self, image_bytes: bytes, filename: str = "image.jpg") -> Dict[str, Any]:
        """Анализ изображения из bytes"""
        files = {'file': (filename, image_bytes, mimetypes.guess_type(filename)[0] or 'application/octet-stream')}
        return self._request("POST", "/analyze_image", files=files)
    
    def parse_demo(self, url: str) -> Dict[str, Any]:
        """Парсинг и анализ сайта"""
        return self._request(
            "POST",
            "/parse_demo",
            json={"url": url}
        )
    
    def get_history(self) -> Dict[str, Any]:
        """Получить историю запросов"""
        return self._request("GET", "/history")
    
    def clear_history(self) -> Dict[str, Any]:
        """Очистить историю"""
        return self._request("DELETE", "/history")


# Глобальный экземпляр
api_client = APIClient()

