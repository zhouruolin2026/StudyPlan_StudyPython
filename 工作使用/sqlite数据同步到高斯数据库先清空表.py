import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import time
import sys

# ====================== 配置区 ======================
SQLITE_DB = "your_sqlite.db"          # ← 修改为你的 SQLite 文件路径
SQLITE_TABLE = "users"                # ← SQLite 源表名

GAUSSDB_CONFIG = {
    "host": "your-gaussdb-host",
    "port": 5432,
    "dbname": "your_database",
    "user": "your_user",
    "password": "your_password",
    # "sslmode": "require",           # 华为云建议开启
}

GAUSSDB_TABLE = "users"               # ← GaussDB 目标表名

COLUMNS_TO_SYNC = ["username", "createtime"]   # ← 要同步的字段（不含自增 id）

BATCH_SIZE = 5000      # 每次读取批次大小
PAGE_SIZE = 1000       # execute_values 内部批次
# ====================================================

def main():
    start_time = time.time()
    
    try:
        # 1. 清空 GaussDB 目标表（并重置自增序列）
        gauss_conn = psycopg2.connect(**GAUSSDB_CONFIG)
        gauss_cursor = gauss_conn.cursor()
        
        print("正在清空 GaussDB 表...")
        gauss_cursor.execute(f"TRUNCATE TABLE {GAUSSDB_TABLE} RESTART IDENTITY;")
        gauss_conn.commit()
        print("✅ 表已清空并重置自增 ID")

        # 2. 连接 SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_cursor = sqlite_conn.cursor()

        # 获取总记录数
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {SQLITE_TABLE}")
        total_rows = sqlite_cursor.fetchone()[0]
        print(f"SQLite 中共有 {total_rows} 条记录")

        # 3. 分页读取 + 批量插入
        offset = 0
        processed = 0

        columns_str = ", ".join(COLUMNS_TO_SYNC)
        insert_sql = f"INSERT INTO {GAUSSDB_TABLE} ({columns_str}) VALUES %s"

        while True:
            sqlite_cursor.execute(
                f"SELECT {columns_str} FROM {SQLITE_TABLE} LIMIT ? OFFSET ?",
                (BATCH_SIZE, offset)
            )
            batch = sqlite_cursor.fetchall()
            
            if not batch:
                break

            execute_values(
                gauss_cursor,
                insert_sql,
                batch,
                page_size=PAGE_SIZE
            )
            
            gauss_conn.commit()   # 每批提交一次，避免事务过大

            processed += len(batch)
            offset += BATCH_SIZE
            progress = min(100, round(processed / total_rows * 100, 1))
            print(f"已同步 {processed}/{total_rows} 条 ({progress}%)")

        elapsed = time.time() - start_time
        print(f"\n✅ 同步完成！共处理 {processed} 条数据，用时 {elapsed:.1f} 秒")

    except Exception as e:
        print(f"❌ 错误: {e}")
        if 'gauss_conn' in locals():
            gauss_conn.rollback()
        sys.exit(1)
    finally:
        if 'sqlite_cursor' in locals(): sqlite_cursor.close()
        if 'sqlite_conn' in locals(): sqlite_conn.close()
        if 'gauss_cursor' in locals(): gauss_cursor.close()
        if 'gauss_conn' in locals(): gauss_conn.close()

if __name__ == "__main__":
    main()