"""Atomic local history. A damaged history is reported, never silently reset."""
import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from backend.config import settings
from backend.models.schemas import HistoryItem

class HistoryService:
    _lock=threading.RLock()
    def __init__(self,path=None):
        self.history_file=Path(path or settings.history_file)
        self.max_items=settings.max_history_items
        self.history_file.parent.mkdir(parents=True,exist_ok=True)

    def _load_history(self):
        if not self.history_file.exists(): return []
        result=json.loads(self.history_file.read_text(encoding='utf-8'))
        if not isinstance(result,list): raise ValueError('Повреждён файл истории')
        return [HistoryItem.model_validate(item).model_dump(mode='json') for item in result]

    def _save_history(self,items):
        temp=self.history_file.with_suffix('.tmp')
        temp.write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
        temp.replace(self.history_file)

    def add_entry(self,request_type,request_summary,response_summary,*,result=None,source=None,duration_s=None):
        with self._lock:
            history=self._load_history()
            item=HistoryItem(id=str(uuid.uuid4()),timestamp=datetime.now(timezone.utc),request_type=request_type,
                request_summary=request_summary[:200],response_summary=response_summary[:1000],
                result=result,source=source,duration_s=duration_s)
            self._save_history([item.model_dump(mode='json')]+history[:self.max_items-1])
            return item

    def get_history(self):
        with self._lock: return [HistoryItem.model_validate(x) for x in self._load_history()]

    def clear_history(self):
        with self._lock:
            self._load_history()
            self._save_history([])

history_service=HistoryService()
