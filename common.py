import hashlib
from contextlib import contextmanager
from dataclasses import dataclass

try:
    from replit import db
except Exception as e:
    import pickledb

    from config import Config

    db = pickledb.load(f"{Config.name}_datas.db", True)


@contextmanager
def db_action():
    db = pickledb.load(f"{Config.name}_datas.db", False)
    try:
        yield db
    finally:
        db.dump()


def hash_code(strs):
    return hashlib.new("md5", strs.encode()).hexdigest()


@dataclass
class DB:
    def add(self, data: dict):
        """
        数据添加
        """
        key = hash_code(data["url"])
        last_data = db.get(key)
        db[key] = data
        return not bool(last_data)

    def delete(self, key: str):
        """
        数据删除
        """
        try:
            del db[key]
        except:
            pass
