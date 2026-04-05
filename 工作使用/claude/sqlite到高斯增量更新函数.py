# sync_sqlite_to_gauss.py  （追加在原文件末尾，或单独存放均可）

import sqlite3
import psycopg2
import psycopg2.extras
from datetime import datetime


def incremental_sync_sqlite_to_gaussdb(
    sqlite_db_path: str,
    sqlite_table: str,
    gauss_config: dict,
    gauss_table: str,
    key_columns: list[str] = ("schema_name", "table_name", "case_name"),
    time_column: str = "updatetime",
    batch_size: int = 500,
) -> dict:
    """
    增量同步 SQLite 表数据到高斯数据库。
    
    逻辑：
      1. 读取 SQLite 全量数据，以 key_columns 为主键构建索引
      2. 读取高斯数据库中对应主键 + time_column，构建索引
      3. 对比得出：新增行、变化行（updatetime 不一致）
      4. 先 DELETE 高斯中的变化行，再批量 INSERT 新增行 + 变化行
      5. 全程同一事务，失败自动回滚

    Parameters
    ----------
    sqlite_db_path : str
        SQLite 数据库文件路径
    sqlite_table : str
        SQLite 源表名
    gauss_config : dict
        高斯数据库连接参数字典
    gauss_table : str
        高斯目标表全限定名，例如 "dw_schema.test_cases"
    key_columns : tuple/list
        用于唯一标识一条记录的列名组合，默认 (schema_name, table_name, case_name)
    time_column : str
        用于判断记录是否变化的时间戳列名，默认 "updatetime"
    batch_size : int
        每批写入行数，默认 500

    Returns
    -------
    dict
        {
            "success":       True / False,
            "inserted":      新增行数,
            "updated":       更新行数（delete + re-insert）,
            "skipped":       无变化跳过行数,
            "elapsed_sec":   耗时秒数,
            "error":         错误信息（成功时为 None）
        }
    """
    start_time = datetime.now()

    # ── 1. 读取 SQLite 全量数据 ───────────────────────────────────────
    try:
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_conn.row_factory = sqlite3.Row
        cur = sqlite_conn.execute(f"SELECT * FROM {sqlite_table}")
        all_columns = [desc[0] for desc in cur.description]
        sqlite_rows = {
            tuple(dict(row)[k] for k in key_columns): dict(row)
            for row in cur.fetchall()
        }
        sqlite_conn.close()
    except Exception as e:
        return _inc_result(False, 0, 0, 0, start_time, f"读取 SQLite 失败: {e}")

    if not sqlite_rows:
        return _inc_result(True, 0, 0, 0, start_time, None)

    # ── 2. 读取高斯数据库中的主键 + updatetime 索引 ───────────────────
    try:
        gauss_conn = psycopg2.connect(**gauss_config)
        gauss_conn.autocommit = False
        gauss_cur = gauss_conn.cursor()

        key_select = ", ".join(f'"{c}"' for c in key_columns)
        gauss_cur.execute(
            f'SELECT {key_select}, "{time_column}" FROM {gauss_table}'
        )
        gauss_index = {
            row[:-1]: row[-1]          # key_tuple -> updatetime
            for row in gauss_cur.fetchall()
        }
    except Exception as e:
        return _inc_result(False, 0, 0, 0, start_time, f"读取高斯数据库失败: {e}")

    # ── 3. 对比，分类为：新增 / 变化 / 无变化 ────────────────────────
    to_insert = []    # 新增行（高斯中不存在）
    to_update = []    # 变化行（key 存在但 updatetime 不一致）
    skipped   = 0

    for key, row in sqlite_rows.items():
        if key not in gauss_index:
            to_insert.append(row)
        elif str(gauss_index[key]) != str(row[time_column]):
            to_update.append(row)
        else:
            skipped += 1

    print(f"  对比结果 → 新增: {len(to_insert)}  变化: {len(to_update)}  跳过: {skipped}")

    if not to_insert and not to_update:
        gauss_conn.close()
        return _inc_result(True, 0, 0, skipped, start_time, None)

    # ── 4. 构造 DELETE / INSERT 语句（全参数化） ──────────────────────
    # DELETE：按联合主键精确删除变化行
    key_where = " AND ".join(f'"{c}" = %s' for c in key_columns)
    delete_sql = f"DELETE FROM {gauss_table} WHERE {key_where}"

    # INSERT：全列参数化插入
    col_clause = ", ".join(f'"{c}"' for c in all_columns)
    val_clause = ", ".join("%s" for _ in all_columns)
    insert_sql = f"INSERT INTO {gauss_table} ({col_clause}) VALUES ({val_clause})"

    # 把 dict 转成有序 tuple
    def row_to_tuple(row: dict) -> tuple:
        return tuple(row.get(c) for c in all_columns)

    def row_to_key_tuple(row: dict) -> tuple:
        return tuple(row.get(c) for c in key_columns)

    # ── 5. 在同一事务内执行 DELETE + INSERT ──────────────────────────
    try:
        # 5-a. DELETE 变化行
        if to_update:
            delete_keys = [row_to_key_tuple(r) for r in to_update]
            psycopg2.extras.execute_batch(
                gauss_cur, delete_sql, delete_keys, page_size=batch_size
            )

        # 5-b. INSERT 新增行 + 变化行（重新插入）
        all_to_write = to_insert + to_update
        insert_data  = [row_to_tuple(r) for r in all_to_write]

        for i in range(0, len(insert_data), batch_size):
            psycopg2.extras.execute_batch(
                gauss_cur, insert_sql,
                insert_data[i : i + batch_size],
                page_size=batch_size,
            )

        gauss_conn.commit()
        gauss_cur.close()
        gauss_conn.close()
        return _inc_result(
            True, len(to_insert), len(to_update), skipped, start_time, None
        )

    except Exception as e:
        gauss_conn.rollback()
        gauss_cur.close()
        gauss_conn.close()
        return _inc_result(False, 0, 0, skipped, start_time, f"写入高斯数据库失败: {e}")


def _inc_result(
    success: bool, inserted: int, updated: int,
    skipped: int, start_time: datetime, error
) -> dict:
    elapsed = round((datetime.now() - start_time).total_seconds(), 2)
    return {
        "success":     success,
        "inserted":    inserted,
        "updated":     updated,
        "skipped":     skipped,
        "elapsed_sec": elapsed,
        "error":       error,
    }


from sync_sqlite_to_gauss import incremental_sync_sqlite_to_gaussdb

GAUSS_CONFIG = {
    "host":     "192.168.1.100",
    "port":     5432,
    "dbname":   "my_db",
    "user":     "my_user",
    "password": "my_password",
}

result = incremental_sync_sqlite_to_gaussdb(
    sqlite_db_path = "./testcase_registry.db",
    sqlite_table   = "test_cases",
    gauss_config   = GAUSS_CONFIG,
    gauss_table    = "dw_schema.test_cases",
    # key_columns 和 time_column 有默认值，不用传也行
)

if result["success"]:
    print(
        f"增量同步完成 | "
        f"新增 {result['inserted']} 行 | "
        f"更新 {result['updated']} 行 | "
        f"跳过 {result['skipped']} 行 | "
        f"耗时 {result['elapsed_sec']}s"
    )
else:
    print(f"同步失败: {result['error']}")
```

---

### 核心逻辑图示
```
SQLite 全量                  高斯现有索引
(key → updatetime)           (key → updatetime)
       │                            │
       └──────────── 对比 ──────────┘
              │            │           │
           新增行        变化行      无变化
        (key不存在)  (time不一致)    跳过 ✓
              │            │
              └─────┬───────┘
                    │
            同一事务内执行
          DELETE 变化行的旧数据
          INSERT 新增 + 变化行
                    │
                 COMMIT ✓
          （任意失败 → ROLLBACK）