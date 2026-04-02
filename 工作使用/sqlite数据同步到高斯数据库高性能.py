import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import sys
import time

# ====================== 配置区 ======================
SQLITE_DB = "your_sqlite.db"          # ← 修改为你的 SQLite 文件路径
SQLITE_TABLE = "users"                # ← 要同步的 SQLite 表名

GAUSSDB_CONFIG = {
    "host": "your-gaussdb-host",
    "port": 5432,
    "dbname": "your_database",
    "user": "your_user",
    "password": "your_password",
    # "sslmode": "require",           # 华为云 GaussDB 建议开启
}

GAUSSDB_TABLE = "users"               # ← GaussDB 目标表名

# 要同步的字段列表（根据你的表调整，不要包含自增 id 时让 GaussDB 自动生成）
COLUMNS_TO_SYNC = ["username", "createtime"]

# 性能参数（20万条推荐以下设置，可微调）
BATCH_SIZE = 5000          # 每次从 SQLite 读取的行数（内存友好）
PAGE_SIZE = 1000           # execute_values 每页插入行数（GaussDB 优化）
# ====================================================

def sync_large_data():
    start_time = time.time()
    
    try:
        # 1. 连接 SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_cursor = sqlite_conn.cursor()
        
        # 获取总记录数（可选，用于显示进度）
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {SQLITE_TABLE}")
        total_rows = sqlite_cursor.fetchone()[0]
        print(f"SQLite 表中共有 {total_rows} 条记录，开始同步...")

        # 2. 连接 GaussDB
        gauss_conn = psycopg2.connect(**GAUSSDB_CONFIG)
        gauss_cursor = gauss_conn.cursor()

        # 3. 分页读取 + 分批插入
        offset = 0
        processed = 0

        columns_str = ", ".join(COLUMNS_TO_SYNC)
        placeholders = ", ".join(["%s"] * len(COLUMNS_TO_SYNC))
        
        insert_sql = f"INSERT INTO {GAUSSDB_TABLE} ({columns_str}) VALUES %s"

        while True:
            # 从 SQLite 分页查询
            sqlite_cursor.execute(
                f"SELECT {columns_str} FROM {SQLITE_TABLE} LIMIT ? OFFSET ?",
                (BATCH_SIZE, offset)
            )
            batch = sqlite_cursor.fetchall()
            
            if not batch:
                break  # 读取完毕

            # 使用 execute_values 批量插入（性能最佳之一）
            execute_values(
                gauss_cursor,
                insert_sql,
                batch,
                page_size=PAGE_SIZE,      # 关键优化参数
                template=None
            )
            
            gauss_conn.commit()           # 每个批次提交一次
            
            processed += len(batch)
            offset += BATCH_SIZE
            
            # 显示进度
            progress = min(100, round(processed / total_rows * 100, 1))
            print(f"已同步 {processed}/{total_rows} 条 ({progress}%) - 本批 {len(batch)} 条")

        elapsed = time.time() - start_time
        print(f"\n✅ 同步完成！共处理 {processed} 条数据，用时 {elapsed:.1f} 秒")

    except Exception as e:
        print(f"❌ 同步失败: {e}")
        if 'gauss_conn' in locals():
            gauss_conn.rollback()
        sys.exit(1)
    finally:
        if 'sqlite_cursor' in locals():
            sqlite_cursor.close()
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'gauss_cursor' in locals():
            gauss_cursor.close()
        if 'gauss_conn' in locals():
            gauss_conn.close()

if __name__ == "__main__":
    sync_large_data()