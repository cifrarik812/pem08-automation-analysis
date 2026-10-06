"""Read-only Selenium capture for the three approved public landing pages."""
import asyncio
import base64
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from backend.config import settings, ROOT

ALLOWED_URLS = frozenset(settings.competitor_urls)
def validate_url(url):
    if url not in ALLOWED_URLS:
        raise ValueError('Разрешены только URL n8n, Make и Albato из конфигурации')
    return url

class ParserService:
    def _parse_sync(self,url):
        driver=None
        try:
            validate_url(url)
            options=webdriver.ChromeOptions()
            options.add_argument('--headless=new')
            options.add_argument('--window-size=1280,900')
            options.page_load_strategy='eager'
            driver=webdriver.Chrome(options=options)
            driver.set_page_load_timeout(settings.parser_timeout)
            driver.get(url)
            WebDriverWait(driver,settings.parser_timeout).until(lambda d: d.find_element(By.TAG_NAME,'body').text.strip())
            final=urlparse(driver.current_url)
            if final.scheme!='https' or final.hostname not in ('n8n.io','www.n8n.io','make.com','www.make.com','albato.ru','www.albato.ru'):
                raise ValueError('Страница перенаправила на неподдерживаемый адрес')
            body=driver.find_element(By.TAG_NAME,'body').text
            if any(marker in body.lower() for marker in ('verify you are human','checking your browser','captcha','access denied')):
                raise ValueError('Сайт требует проверку доступа; автоматический обход не выполняется')
            headings=driver.find_elements(By.TAG_NAME,'h1')
            heading=headings[0].text if headings else None
            screenshot=driver.get_screenshot_as_png()
            folder=ROOT/'outputs'/'captures';folder.mkdir(parents=True,exist_ok=True)
            name=final.hostname.replace('.','_')
            (folder/f'{name}.png').write_bytes(screenshot)
            (folder/f'{name}.txt').write_text(body,encoding='utf-8')
            return driver.title,heading,body[:12000],screenshot,None
        except ValueError as exc:
            return None,None,None,None,str(exc)
        except Exception as exc:
            return None,None,None,None,'Не удалось получить страницу через Selenium: '+type(exc).__name__
        finally:
            if driver is not None:
                driver.quit()

    async def parse_url(self,url):
        try: validate_url(url)
        except ValueError as exc: return None,None,None,None,str(exc)
        return await asyncio.to_thread(self._parse_sync,url)

    def screenshot_to_base64(self,data):
        return base64.b64encode(data).decode()

    async def close(self):
        pass

parser_service=ParserService()
