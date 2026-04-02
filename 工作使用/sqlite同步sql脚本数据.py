import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import time
import sys

# ====================== 配置区 ======================
SQLITE_DB = "your_sqlite.db"
SQLITE_TABLE = "sql_snippets"          # 你的 SQLite 表名

GAUSSDB_CONFIG = {
    "host": "your-gaussdb-host",
    "port": 5432,
    "dbname": "your_database",
    "user": "your_user",
    "password": "your_password",
    # "sslmode": "require",   # 华为云建议开启
}

GAUSSDB_TABLE = "sql_scripts"

# 要同步的字段（sql_code 包含大量特殊符号也没关系）
COLUMNS_TO_SYNC = ["script_name", "sql_code"]

BATCH_SIZE = 2000      # 建议调小一点，因为单条 sql_code 可能很长
PAGE_SIZE = 500        # execute_values 内部每页大小
# ====================================================

def sync_sql_scripts():
    start_time = time.time()
    
    try:
        # 连接 GaussDB 并清空表
        gauss_conn = psycopg2.connect(**GAUSSDB_CONFIG)
        gauss_cur = gauss_conn.cursor()
        
        print("正在清空 GaussDB 目标表...")
        gauss_cur.execute(f"TRUNCATE TABLE {GAUSSDB_TABLE} RESTART IDENTITY;")
        gauss_conn.commit()
        print("✅ 表已清空")

        # 连接 SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_cur = sqlite_conn.cursor()

        # 获取总记录数
        sqlite_cur.execute(f"SELECT COUNT(*) FROM {SQLITE_TABLE}")
        total = sqlite_cur.fetchone()[0]
        print(f"SQLite 中共有 {total} 条 SQL 脚本，开始同步...")

        columns_str = ", ".join(COLUMNS_TO_SYNC)
        insert_sql = f"INSERT INTO {GAUSSDB_TABLE} ({columns_str}) VALUES %s"

        offset = 0
        processed = 0

        while True:
            sqlite_cur.execute(
                f"SELECT {columns_str} FROM {SQLITE_TABLE} LIMIT ? OFFSET ?",
                (BATCH_SIZE, offset)
            )
            batch = sqlite_cur.fetchall()
            
            if not batch:
                break

            # execute_values 会自动、正确地处理所有单引号、双引号、换行、反斜杠等
            execute_values(gauss_cur, insert_sql, batch, page_size=PAGE_SIZE)
            
            gauss_conn.commit()   # 每批提交，防止事务过大

            processed += len(batch)
            offset += BATCH_SIZE
            print(f"已同步 {processed}/{total} 条 ({round(processed/total*100, 1)}%)")

        elapsed = time.time() - start_time
        print(f"\n✅ 同步完成！共处理 {processed} 条 SQL 脚本，用时 {elapsed:.1f} 秒")

    except Exception as e:
        print(f"❌ 错误: {e}")
        if 'gauss_conn' in locals():
            gauss_conn.rollback()
        sys.exit(1)
    finally:
        if 'sqlite_cur' in locals(): sqlite_cur.close()
        if 'sqlite_conn' in locals(): sqlite_conn.close()
        if 'gauss_cur' in locals(): gauss_cur.close()
        if 'gauss_conn' in locals(): gauss_conn.close()

if __name__ == "__main__":
    sync_sql_scripts()