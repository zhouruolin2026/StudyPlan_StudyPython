# sync_sqlite_to_gauss.py

import sqlite3
import psycopg2
import psycopg2.extras
from datetime import datetime


def sync_sqlite_to_gaussdb(
    sqlite_db_path: str,
    sqlite_table: str,
    gauss_config: dict,
    gauss_table: str,
    batch_size: int = 500,
) -> dict:
    """
    全量同步 SQLite 表数据到高斯数据库（TRUNCATE + INSERT）。

    Parameters
    ----------
    sqlite_db_path : str
        SQLite 数据库文件路径，例如 "./testcase_registry.db"

    sqlite_table : str
        SQLite 源表名，例如 "test_cases"

    gauss_config : dict
        高斯数据库连接参数，例如：
        {
            "host":     "192.168.1.100",
            "port":     5432,
            "dbname":   "my_db",
            "user":     "my_user",
            "password": "my_password",
            "options":  "-c search_path=my_schema",  # 可选
        }

    gauss_table : str
        高斯目标表全限定名，例如 "dw_schema.test_cases"

    batch_size : int
        每批写入的行数，默认 500，数据量大时可调大到 1000~2000

    Returns
    -------
    dict
        {
            "success":      True / False,
            "total_rows":   同步行数,
            "elapsed_sec":  耗时秒数,
            "error":        错误信息（成功时为 None）
        }
    """
    start_time = datetime.now()

    # ── 1. 读取 SQLite ────────────────────────────────────────────────
    try:
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_conn.row_factory = sqlite3.Row
        cursor = sqlite_conn.execute(f"SELECT * FROM {sqlite_table}")
        columns = [desc[0] for desc in cursor.description]
        rows = [dict(row) for row in cursor.fetchall()]
        sqlite_conn.close()
    except Exception as e:
        return _result(False, 0, start_time, f"读取 SQLite 失败: {e}")

    total = len(rows)
    if total == 0:
        return _result(True, 0, start_time, None)

    # ── 2. 构造参数化 INSERT ──────────────────────────────────────────
    col_clause = ", ".join(f'"{c}"' for c in columns)
    val_clause = ", ".join("%s" for _ in columns)
    insert_sql = f"INSERT INTO {gauss_table} ({col_clause}) VALUES ({val_clause})"

    # 将每行 dict 转为与 columns 顺序一致的 tuple（None → NULL）
    data = [tuple(row.get(col) for col in columns) for row in rows]

    # ── 3. 写入高斯数据库 ─────────────────────────────────────────────
    gauss_conn = None
    try:
        gauss_conn = psycopg2.connect(**gauss_config)
        gauss_conn.autocommit = False
        cur = gauss_conn.cursor()

        # TRUNCATE 与 INSERT 在同一事务，保证原子性
        cur.execute(f"TRUNCATE TABLE {gauss_table}")

        for i in range(0, total, batch_size):
            psycopg2.extras.execute_batch(
                cur, insert_sql, data[i : i + batch_size], page_size=batch_size
            )

        gauss_conn.commit()
        cur.close()
        return _result(True, total, start_time, None)

    except Exception as e:
        if gauss_conn:
            gauss_conn.rollback()
        return _result(False, 0, start_time, f"写入高斯数据库失败: {e}")

    finally:
        if gauss_conn:
            gauss_conn.close()


def _result(success: bool, total: int, start_time: datetime, error) -> dict:
    elapsed = round((datetime.now() - start_time).total_seconds(), 2)
    return {
        "success":    success,
        "total_rows": total,
        "elapsed_sec": elapsed,
        "error":      error,
    }


# your_other_script.py

from sync_sqlite_to_gauss import sync_sqlite_to_gaussdb

GAUSS_CONFIG = {
    "host":     "192.168.1.100",
    "port":     5432,
    "dbname":   "my_db",
    "user":     "my_user",
    "password": "my_password",
}

result = sync_sqlite_to_gaussdb(
    sqlite_db_path = "./testcase_registry.db",
    sqlite_table   = "test_cases",
    gauss_config   = GAUSS_CONFIG,
    gauss_table    = "dw_schema.test_cases",
)

if result["success"]:
    print(f"同步成功，共 {result['total_rows']} 行，耗时 {result['elapsed_sec']} 秒")
else:
    print(f"同步失败: {result['error']}")