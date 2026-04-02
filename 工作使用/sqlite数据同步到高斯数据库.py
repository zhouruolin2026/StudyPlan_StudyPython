import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import sys

# ====================== 配置区 ======================
# SQLite 配置
SQLITE_DB = "your_sqlite.db"          # ← 改成你的 SQLite 文件路径
SQLITE_TABLE = "users"                # ← 要同步的 SQLite 表名

# GaussDB 配置（PostgreSQL 兼容模式）
GAUSSDB_CONFIG = {
    "host": "your-gaussdb-host",      # ← GaussDB 实例地址（IP 或域名）
    "port": 5432,                     # ← 默认端口，通常是 5432
    "dbname": "your_database",        # ← 数据库名
    "user": "your_user",              # ← 用户名
    "password": "your_password",      # ← 密码
    # 如果是华为云 GaussDB 且要求 SSL，可加上下面两行（推荐加）：
    # "sslmode": "require",           # 或 "verify-full"
    # "sslrootcert": "/path/to/ca.crt"  # 如果需要证书验证
}

# GaussDB 目标表（必须提前建好）
GAUSSDB_TABLE = "users"               # ← 目标表名

# 要同步的字段（不包含 id 时，GaussDB 会自动生成 SERIAL）
# 如果你想保留 SQLite 的 id，把 'id' 也加进来
COLUMNS_TO_SYNC = ["username", "createtime"]   # ← 根据你的表调整
# ====================================================

def main():
    try:
        # 1. 连接 SQLite 并读取所有数据
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_cursor = sqlite_conn.cursor()
        
        # 拼接 SELECT 语句
        columns_str = ", ".join(COLUMNS_TO_SYNC)
        sqlite_cursor.execute(f"SELECT {columns_str} FROM {SQLITE_TABLE}")
        rows = sqlite_cursor.fetchall()   # 所有数据一次性取出
        
        print(f"从 SQLite 读取到 {len(rows)} 条记录")
        
        sqlite_conn.close()

        # 2. 连接 GaussDB
        gauss_conn = psycopg2.connect(**GAUSSDB_CONFIG)
        gauss_cursor = gauss_conn.cursor()
        
        # 3. 批量插入（最快的方式）
        # 构造 INSERT 语句
        placeholders = ", ".join(["%s"] * len(COLUMNS_TO_SYNC))
        insert_sql = f"""
            INSERT INTO {GAUSSDB_TABLE} ({columns_str})
            VALUES %s
        """
        
        # 使用 execute_values 进行高效批量插入（比 executemany 更快）
        execute_values(gauss_cursor, insert_sql, rows)
        
        gauss_conn.commit()
        print(f"✅ 成功同步 {len(rows)} 条记录到 GaussDB！")
        
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        sys.exit(1)
    finally:
        # 关闭连接
        if 'gauss_cursor' in locals():
            gauss_cursor.close()
        if 'gauss_conn' in locals():
            gauss_conn.close()

if __name__ == "__main__":
    main()