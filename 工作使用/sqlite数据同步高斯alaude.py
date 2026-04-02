import sqlite3
import psycopg2
import psycopg2.extras
from datetime import datetime

# ========== 配置 ==========
SQLITE_DB_PATH = "./testcase_registry.db"
SQLITE_TABLE   = "test_cases"

GAUSS_CONFIG = {
    "host":     "your-gaussdb-host",
    "port":     5432,
    "dbname":   "your_db",
    "user":     "your_user",
    "password": "your_password",
    "options":  "-c search_path=your_schema",  # 如有 schema 前缀
}
GAUSS_TABLE = "your_schema.test_cases"   # 目标表全限定名
BATCH_SIZE  = 500                         # 每批写入行数
# ==========================


# ---------- 读取 SQLite ----------

def read_from_sqlite(db_path: str, table: str) -> tuple[list[dict], list[str]]:
    """读取 SQLite 全量数据，返回 (rows, columns)"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row          # 让每行可以按列名访问
    cursor = conn.execute(f"SELECT * FROM {table}")
    columns = [desc[0] for desc in cursor.description]
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows, columns


# ---------- 写入高斯数据库 ----------

def build_insert_sql(table: str, columns: list[str]) -> str:
    """
    构造参数化 INSERT 语句。
    列名用双引号包裹，防止与保留字冲突。
    占位符用 psycopg2 的 %s，驱动负责转义所有特殊字符。
    """
    col_clause = ", ".join(f'"{c}"' for c in columns)
    val_clause = ", ".join("%s" for _ in columns)
    return f'INSERT INTO {table} ({col_clause}) VALUES ({val_clause})'


def sync_to_gaussdb(rows: list[dict], columns: list[str]):
    if not rows:
        print("SQLite 无数据，跳过写入")
        return

    insert_sql = build_insert_sql(GAUSS_TABLE, columns)
    # 把每行 dict 转成与 columns 顺序一致的 tuple，None 保持为 NULL
    data = [tuple(row.get(col) for col in columns) for row in rows]

    conn = psycopg2.connect(**GAUSS_CONFIG)
    conn.autocommit = False                 # 手动事务，保证原子性
    cursor = conn.cursor()

    try:
        # ① 清空目标表
        print(f"  TRUNCATE {GAUSS_TABLE} ...")
        cursor.execute(f"TRUNCATE TABLE {GAUSS_TABLE}")

        # ② 分批写入（避免单次传输过大）
        total = len(data)
        written = 0
        for i in range(0, total, BATCH_SIZE):
            batch = data[i : i + BATCH_SIZE]
            psycopg2.extras.execute_batch(cursor, insert_sql, batch, page_size=BATCH_SIZE)
            written += len(batch)
            print(f"  已写入 {written}/{total} 行...")

        conn.commit()
        print(f"  ✓ 提交成功，共写入 {total} 行")

    except Exception as e:
        conn.rollback()
        print(f"  [ERROR] 写入失败，已回滚: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ---------- 主流程 ----------

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始全量同步 SQLite → GaussDB")

    print("\n① 读取 SQLite 数据...")
    rows, columns = read_from_sqlite(SQLITE_DB_PATH, SQLITE_TABLE)
    print(f"   读取到 {len(rows)} 行，列: {columns}")

    print("\n② 写入 GaussDB（TRUNCATE + INSERT）...")
    sync_to_gaussdb(rows, columns)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 同步完成")


if __name__ == "__main__":
    main()