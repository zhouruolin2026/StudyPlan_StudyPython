import os
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

# ========== 配置 ==========
TESTCASE_DIR = "./testcase"          # testcase 目录路径
DB_PATH = "./testcase_registry.db"  # SQLite 数据库路径
TABLE_NAME = "test_cases"
SCHEMA_LAYERS = {"ods", "dwd", "ads"}  # 需要扫描的 schema 层
# ==========================


def init_db(conn: sqlite3.Connection):
    """初始化数据库表"""
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            schema_name TEXT    NOT NULL,
            table_name  TEXT    NOT NULL,
            case_name   TEXT    NOT NULL,
            test_sql_code TEXT  NOT NULL,
            updatetime  TEXT    NOT NULL,
            file_size   INTEGER NOT NULL,
            UNIQUE (schema_name, table_name, case_name)
        )
    """)
    conn.commit()


def scan_files(base_dir: str) -> list[dict]:
    """
    扫描 testcase 目录，返回所有 case*.sql 文件的元信息列表
    结构: testcase/{schema}/{table}/case*.sql
    """
    results = []
    base = Path(base_dir)

    for schema_path in base.iterdir():
        if not schema_path.is_dir():
            continue
        schema_name = schema_path.name
        if schema_name.lower() not in SCHEMA_LAYERS:
            continue

        for table_path in schema_path.iterdir():
            if not table_path.is_dir():
                continue
            table_name = table_path.name

            for sql_file in table_path.iterdir():
                if not sql_file.is_file():
                    continue
                if not sql_file.name.startswith("case") or not sql_file.suffix == ".sql":
                    continue

                stat = sql_file.stat()
                updatetime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                file_size = stat.st_size

                results.append({
                    "schema_name": schema_name,
                    "table_name": table_name,
                    "case_name": sql_file.name,
                    "file_path": str(sql_file),
                    "updatetime": updatetime,
                    "file_size": file_size,
                })

    return results


def get_db_index(conn: sqlite3.Connection) -> dict:
    """
    读取数据库中已有记录的 (schema, table, case_name) -> (updatetime, file_size)
    """
    cursor = conn.execute(f"""
        SELECT schema_name, table_name, case_name, updatetime, file_size
        FROM {TABLE_NAME}
    """)
    index = {}
    for row in cursor.fetchall():
        key = (row[0], row[1], row[2])
        index[key] = {"updatetime": row[3], "file_size": row[4]}
    return index


def find_changed_files(scanned: list[dict], db_index: dict) -> list[dict]:
    """
    对比文件系统与数据库，找出新增或发生变化的文件
    """
    changed = []
    for f in scanned:
        key = (f["schema_name"], f["table_name"], f["case_name"])
        existing = db_index.get(key)
        if existing is None:
            f["action"] = "insert"
            changed.append(f)
        elif existing["updatetime"] != f["updatetime"] or existing["file_size"] != f["file_size"]:
            f["action"] = "update"
            changed.append(f)
    return changed


def upsert_files(conn: sqlite3.Connection, files: list[dict]):
    """
    将变更文件写入数据库（新增或更新）
    """
    insert_count = update_count = error_count = 0

    for f in files:
        try:
            content = Path(f["file_path"]).read_text(encoding="utf-8")
        except Exception as e:
            print(f"  [ERROR] 读取文件失败: {f['file_path']} -> {e}")
            error_count += 1
            continue

        if f["action"] == "insert":
            conn.execute(f"""
                INSERT INTO {TABLE_NAME}
                    (schema_name, table_name, case_name, test_sql_code, updatetime, file_size)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (f["schema_name"], f["table_name"], f["case_name"],
                  content, f["updatetime"], f["file_size"]))
            insert_count += 1
        else:
            conn.execute(f"""
                UPDATE {TABLE_NAME}
                SET test_sql_code = ?,
                    updatetime    = ?,
                    file_size     = ?
                WHERE schema_name = ? AND table_name = ? AND case_name = ?
            """, (content, f["updatetime"], f["file_size"],
                  f["schema_name"], f["table_name"], f["case_name"]))
            update_count += 1

    conn.commit()
    return insert_count, update_count, error_count


def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始同步 testcase → SQLite")
    print(f"  目录: {os.path.abspath(TESTCASE_DIR)}")
    print(f"  数据库: {os.path.abspath(DB_PATH)}")

    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    # 1. 扫描文件系统
    scanned = scan_files(TESTCASE_DIR)
    print(f"\n扫描到 {len(scanned)} 个 case*.sql 文件")

    # 2. 读取数据库现有记录
    db_index = get_db_index(conn)
    print(f"数据库现有记录: {len(db_index)} 条")

    # 3. 找出需要同步的文件
    changed = find_changed_files(scanned, db_index)
    new_files = [f for f in changed if f["action"] == "insert"]
    upd_files = [f for f in changed if f["action"] == "update"]
    print(f"需要新增: {len(new_files)} 个，需要更新: {len(upd_files)} 个")

    if not changed:
        print("\n✓ 数据已是最新，无需同步")
        conn.close()
        return

    # 4. 写入数据库
    print("\n正在写入...")
    ins, upd, err = upsert_files(conn, changed)
    print(f"\n✓ 同步完成: 新增 {ins} 条，更新 {upd} 条，失败 {err} 条")

    conn.close()


if __name__ == "__main__":
    main()