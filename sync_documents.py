#!/usr/bin/env python
import json, logging, os, sys
from pathlib import Path

# Настройки
DJANGO_PROJECT_ROOT    = Path('/opt/medica-perevod/')  # изменить
DJANGO_SETTINGS_MODULE = 'config.settings'              # изменить
SCAN_DIR               = 'documents'                    # относительно MEDIA_ROOT
CACHE_FILE = Path(__file__).with_name('.sync_cache.json')
LOCK_FILE  = Path(__file__).with_name('.sync_documents.lock')
SUPPORTED_EXTENSIONS   = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'gif'}

# Django
sys.path.insert(0, str(DJANGO_PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', DJANGO_SETTINGS_MODULE)
import django; django.setup()

from django.conf import settings
from core.models import Document

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s  %(levelname)s  %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(__name__)

# Кеш
def load_cache() -> set:
    if CACHE_FILE.exists():
        try:
            return set(json.loads(CACHE_FILE.read_text()).get('processed', []))
        except (json.JSONDecodeError, KeyError):
            pass
    return set()

def save_cache(processed: set) -> None:
    CACHE_FILE.write_text(
        json.dumps({'processed': sorted(processed)}, ensure_ascii=False, indent=2)
    )

# Замок
class AlreadyRunning(Exception):
    pass

def acquire_lock():
    if LOCK_FILE.exists():
        pid = LOCK_FILE.read_text().strip()
        if pid and Path(f'/proc/{pid}').exists():
            raise AlreadyRunning(f'Уже запущен (PID {pid})')
        LOCK_FILE.unlink(missing_ok=True)
    LOCK_FILE.write_text(str(os.getpid()))

def release_lock():
    LOCK_FILE.unlink(missing_ok=True)

# Логика 
def scan_disk(media_root: Path) -> dict:
    result = {}
    scan_root = media_root / SCAN_DIR
    if not scan_root.exists():
        log.warning('Папка не найдена: %s', scan_root)
        return result
    for path in scan_root.rglob('*'):
        if not path.is_file(): continue
        if 'preview' in path.parts: continue
        if path.suffix.lstrip('.').lower() not in SUPPORTED_EXTENSIONS: continue
        result[str(path.relative_to(media_root))] = path
    return result

def sync():
    media_root = Path(settings.MEDIA_ROOT)
    cache      = load_cache()
    disk_files = scan_disk(media_root)
    db_map     = {doc.file.name: doc for doc in Document.objects.exclude(file='')}

    # Записи без файла на диске → удалить из БД
    orphaned = set(db_map.keys()) - set(disk_files.keys())
    for rel in sorted(orphaned):
        db_map[rel].delete()
        cache.discard(rel)
        log.info('  [-] Удалена запись: %s', rel)

    # Файлы без записи в БД → создать запись
    new_files = set(disk_files.keys()) - set(db_map.keys()) - cache
    for rel in sorted(new_files):
        title = Path(rel).stem.replace('_', ' ').replace('-', ' ').title()
        try:
            Document(title=title, file=rel, is_published=False).save()
            cache.add(rel)
            log.info('  [+] Создан: %s  →  «%s»', rel, title)
        except Exception as exc:
            log.error('  [!] Ошибка: %s: %s', rel, exc)

    if not orphaned and not new_files:
        log.info('Нет изменений.')

    save_cache(cache)

if __name__ == '__main__':
    try:
        acquire_lock()
    except AlreadyRunning as e:
        log.warning('%s — выходим.', e)
        sys.exit(0)
    try:
        sync()
    finally:
        release_lock()