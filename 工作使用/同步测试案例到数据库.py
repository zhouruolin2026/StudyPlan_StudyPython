# 我有一个git仓库，里面有一个testcase目录下， ods，dwd，ads目录，然后这些目录下有表名命名的目录，再下面就是有case开头的sql脚本文件， 我现在需要读取这些数据，然后存储到sqlite数据库中， 我需要把ods，dwd这一层的目录名给到数据库表中的schema_name 列，我需要把表名目录给到table_name列，我需要把是case开头的sql文件的文件名给到case_name列，把文件内容给到test_sql_code列，把文件的更新时间给到updatetime列，把文件大小给到file_size列。请问我应该怎么写这个sql脚本？

CREATE TABLE IF NOT EXISTS test_cases (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    schema_name   TEXT NOT NULL,
    table_name    TEXT NOT NULL,
    case_name     TEXT NOT NULL,
    test_sql_code TEXT NOT NULL,
    updatetime    TEXT NOT NULL,
    file_size     INTEGER NOT NULL,
    UNIQUE(schema_name, table_name, case_name)   -- 防止重复
);


import sqlite3
from pathlib import Path
from datetime import datetime
import argparse
import sys

def init_db(db_path: str):
    """初始化 SQLite 表"""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS test_cases (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            schema_name   TEXT NOT NULL,
            table_name    TEXT NOT NULL,
            case_name     TEXT NOT NULL,
            test_sql_code TEXT NOT NULL,
            updatetime    TEXT NOT NULL,
            file_size     INTEGER NOT NULL,
            UNIQUE(schema_name, table_name, case_name)
        )
    """)
    conn.commit()
    return conn

def populate_testcases(repo_root: str, db_path: str = "testcases.db"):
    """从 Git 仓库的 testcase 目录读取所有 case*.sql 并写入 SQLite"""
    conn = init_db(db_path)
    
    # 先清空旧数据（每次全量刷新）
    conn.execute("DELETE FROM test_cases")
    conn.commit()
    
    root = Path(repo_root).resolve()
    testcase_dir = root / "testcase"
    
    if not testcase_dir.is_dir():
        print(f"❌ 错误：未找到 testcase 目录 → {testcase_dir}")
        sys.exit(1)
    
    count = 0
    schemas = {"ods", "dwd", "ads"}
    
    print(f"开始扫描目录：{testcase_dir}")
    
    for schema_dir in testcase_dir.iterdir():
        if not schema_dir.is_dir() or schema_dir.name not in schemas:
            continue
            
        schema_name = schema_dir.name
        print(f"  正在处理 schema: {schema_name}")
        
        for table_dir in schema_dir.iterdir():
            if not table_dir.is_dir():
                continue
                
            table_name = table_dir.name
            
            for file_path in table_dir.iterdir():
                if not file_path.is_file() or not file_path.name.startswith("case"):
                    continue
                
                case_name = file_path.name
                
                try:
                    # 读取 SQL 文件内容（支持大量换行、引号、逗号等）
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        sql_code = f.read()
                    
                    # 获取文件信息
                    stat = file_path.stat()
                    file_size = stat.st_size
                    mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    
                    # 插入数据库（参数化，安全处理所有特殊符号）
                    conn.execute("""
                        INSERT INTO test_cases 
                        (schema_name, table_name, case_name, test_sql_code, updatetime, file_size)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (schema_name, table_name, case_name, sql_code, mtime, file_size))
                    
                    count += 1
                    if count % 50 == 0:
                        print(f"    已处理 {count} 个 case 文件...")
                        
                except Exception as e:
                    print(f"    ⚠️  读取失败 {file_path}：{e}")
                    continue
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ 同步完成！共导入 {count} 个测试用例 SQL 脚本")
    print(f"   数据库文件：{Path(db_path).resolve()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="把 Git 仓库 testcase 目录下的 SQL 测试脚本存入 SQLite")
    parser.add_argument("--repo", required=True, help="Git 仓库根目录路径（必须包含 testcase 文件夹）")
    parser.add_argument("--db", default="testcases.db", help="SQLite 数据库路径（默认 testcases.db）")
    args = parser.parse_args()
    
    populate_testcases(args.repo, args.db)
