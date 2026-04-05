# testcase_runner.py

import sqlite3
import psycopg2
import psycopg2.extras
from datetime import datetime


# ══════════════════════════════════════════════════════════════════
#  通用工具函数：更新单条记录的指定字段
# ══════════════════════════════════════════════════════════════════

def update_gaussdb_row(
    gauss_config: dict,
    table: str,
    pk: dict,
    updates: dict,
) -> dict:
    """
    更新高斯数据库中指定表的单条记录。

    Parameters
    ----------
    gauss_config : dict    高斯连接参数
    table        : str     表全限定名，例如 "dw_schema.test_cases"
    pk           : dict    联合主键，例如 {"schema_name":"ods","table_name":"t1","case_name":"case01.sql"}
    updates      : dict    要更新的字段及值，例如 {"exec_status":"pass","exec_time":"2024-01-01 12:00:00"}

    Returns
    -------
    dict  {"success": bool, "error": str|None}
    """
    if not updates:
        return {"success": False, "error": "updates 字典不能为空"}

    set_clause   = ", ".join(f'"{k}" = %s' for k in updates)
    where_clause = " AND ".join(f'"{k}" = %s' for k in pk)
    sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    params = list(updates.values()) + list(pk.values())

    conn = None
    try:
        conn = psycopg2.connect(**gauss_config)
        conn.autocommit = False
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        cur.close()
        return {"success": True, "error": None}
    except Exception as e:
        if conn:
            conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        if conn:
            conn.close()


def update_sqlite_row(
    db_path: str,
    table: str,
    pk: dict,
    updates: dict,
) -> dict:
    """
    更新 SQLite 中指定表的单条记录。

    Parameters
    ----------
    db_path  : str   SQLite 文件路径
    table    : str   表名
    pk       : dict  联合主键，例如 {"schema_name":"ods","table_name":"t1","case_name":"case01.sql"}
    updates  : dict  要更新的字段及值

    Returns
    -------
    dict  {"success": bool, "error": str|None}
    """
    if not updates:
        return {"success": False, "error": "updates 字典不能为空"}

    set_clause   = ", ".join(f'"{k}" = ?' for k in updates)
    where_clause = " AND ".join(f'"{k}" = ?' for k in pk)
    sql = f'UPDATE "{table}" SET {set_clause} WHERE {where_clause}'
    params = list(updates.values()) + list(pk.values())

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(sql, params)
        conn.commit()
        return {"success": True, "error": None}
    except Exception as e:
        if conn:
            conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        if conn:
            conn.close()


# ══════════════════════════════════════════════════════════════════
#  核心函数：从高斯库拉取指定表的测试案例
# ══════════════════════════════════════════════════════════════════

def fetch_cases_by_tables(
    gauss_config: dict,
    gauss_table: str,
    table_names: list[str],
) -> list[dict]:
    """
    从高斯数据库案例库中，拉取 table_name 在清单内的所有测试案例。

    Returns
    -------
    list[dict]  每条案例的全字段字典，按 schema_name, table_name, case_name 排序
    """
    if not table_names:
        return []

    placeholders = ", ".join("%s" for _ in table_names)
    sql = f"""
        SELECT *
        FROM {gauss_table}
        WHERE "table_name" IN ({placeholders})
        ORDER BY "schema_name", "table_name", "case_name"
    """
    conn = psycopg2.connect(**gauss_config)
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, table_names)
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


# ══════════════════════════════════════════════════════════════════
#  核心函数：执行单条测试案例 SQL，返回是否通过
# ══════════════════════════════════════════════════════════════════

def run_single_case(
    gauss_config: dict,
    sql_code: str,
) -> dict:
    """
    在高斯数据库中执行一段 SQL 验证脚本。
    规则：查询结果第一行第一列等于 1 → pass，其他值或异常 → fail。

    Returns
    -------
    dict
        {
            "status":  "pass" | "fail",
            "result":  实际返回值（字符串），异常时为错误信息,
            "exec_time": 执行完成的时间字符串
        }
    """
    exec_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = None
    try:
        conn = psycopg2.connect(**gauss_config)
        conn.autocommit = True          # 验证脚本只读，无需事务
        cur = conn.cursor()
        cur.execute(sql_code)

        row = cur.fetchone()
        cur.close()

        if row is None:
            return {"status": "fail", "result": "查询无返回结果", "exec_time": exec_time}

        actual = row[0]
        status = "pass" if str(actual).strip() == "1" else "fail"
        return {"status": status, "result": str(actual), "exec_time": exec_time}

    except Exception as e:
        return {"status": "fail", "result": f"执行异常: {e}", "exec_time": exec_time}
    finally:
        if conn:
            conn.close()


# ══════════════════════════════════════════════════════════════════
#  主流程：按清单批量执行测试案例并回写结果
# ══════════════════════════════════════════════════════════════════

def run_testcases(
    table_list: list[str],
    gauss_config: dict,
    gauss_table: str,
    sqlite_db_path: str,
    sqlite_table: str,
    pk_columns: tuple = ("schema_name", "table_name", "case_name"),
    status_column: str = "exec_status",
    exectime_column: str = "exec_time",
) -> dict:
    """
    主入口：按用户提供的表名清单执行所有对应测试案例。

    Parameters
    ----------
    table_list       : list[str]  用户提供的表名清单，例如 ["ods_order","dwd_user"]
    gauss_config     : dict       高斯数据库连接参数
    gauss_table      : str        高斯案例库全限定表名
    sqlite_db_path   : str        SQLite 数据库路径
    sqlite_table     : str        SQLite 案例表名
    pk_columns       : tuple      联合主键列名
    status_column    : str        案例执行状态字段名
    exectime_column  : str        案例执行时间字段名

    Returns
    -------
    dict
        {
            "total":   总案例数,
            "pass":    通过数,
            "fail":    失败数,
            "details": [每条案例的执行明细],
            "elapsed_sec": 总耗时
        }
    """
    start_time = datetime.now()
    print(f"\n{'='*60}")
    print(f"  测试案例执行开始  {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  表清单: {table_list}")
    print(f"{'='*60}")

    # ── 1. 从高斯拉取案例清单 ─────────────────────────────────────
    print("\n[1/3] 从高斯数据库拉取案例...")
    cases = fetch_cases_by_tables(gauss_config, gauss_table, table_list)
    print(f"      共找到 {len(cases)} 条案例")

    if not cases:
        print("  ⚠ 未找到任何案例，请确认表名清单是否正确")
        return {"total": 0, "pass": 0, "fail": 0, "details": [], "elapsed_sec": 0}

    # ── 2. 逐条执行 ───────────────────────────────────────────────
    print("\n[2/3] 开始逐条执行案例...\n")
    details   = []
    pass_cnt  = 0
    fail_cnt  = 0

    for idx, case in enumerate(cases, 1):
        pk = {col: case[col] for col in pk_columns}
        label = f"{case['schema_name']}.{case['table_name']} / {case['case_name']}"

        # 执行 SQL 验证脚本
        run_result = run_single_case(gauss_config, case["test_sql_code"])

        status   = run_result["status"]
        exec_time = run_result["exec_time"]
        symbol   = "✓" if status == "pass" else "✗"
        print(f"  [{idx:>3}/{len(cases)}] {symbol} {label}  →  {status}  (返回值: {run_result['result']})")

        if status == "pass":
            pass_cnt += 1
        else:
            fail_cnt += 1

        updates = {
            status_column:  status,
            exectime_column: exec_time,
        }

        # ── 3a. 回写 SQLite ───────────────────────────────────────
        r_sqlite = update_sqlite_row(sqlite_db_path, sqlite_table, pk, updates)
        if not r_sqlite["success"]:
            print(f"        ⚠ SQLite 回写失败: {r_sqlite['error']}")

        # ── 3b. 回写高斯数据库 ────────────────────────────────────
        r_gauss = update_gaussdb_row(gauss_config, gauss_table, pk, updates)
        if not r_gauss["success"]:
            print(f"        ⚠ 高斯回写失败: {r_gauss['error']}")

        details.append({
            "schema_name": case["schema_name"],
            "table_name":  case["table_name"],
            "case_name":   case["case_name"],
            "status":      status,
            "result":      run_result["result"],
            "exec_time":   exec_time,
        })

    # ── 3. 汇总 ───────────────────────────────────────────────────
    elapsed = round((datetime.now() - start_time).total_seconds(), 2)
    print(f"\n{'='*60}")
    print(f"  执行完成  耗时 {elapsed}s")
    print(f"  总计: {len(cases)}  ✓ 通过: {pass_cnt}  ✗ 失败: {fail_cnt}")
    print(f"{'='*60}\n")

    return {
        "total":       len(cases),
        "pass":        pass_cnt,
        "fail":        fail_cnt,
        "details":     details,
        "elapsed_sec": elapsed,
    }


# ══════════════════════════════════════════════════════════════════
#  示例入口
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    GAUSS_CONFIG = {
        "host":     "192.168.1.100",
        "port":     5432,
        "dbname":   "my_db",
        "user":     "my_user",
        "password": "my_password",
    }

    result = run_testcases(
        table_list     = ["ods_order", "ods_user", "dwd_trade"],  # 用户提供的清单
        gauss_config   = GAUSS_CONFIG,
        gauss_table    = "dw_schema.test_cases",
        sqlite_db_path = "./testcase_registry.db",
        sqlite_table   = "test_cases",
    )
```

---

### 整体流程图
```
用户提供表名清单 ["ods_order", "dwd_user", ...]
         │
         ▼
 fetch_cases_by_tables()
 按 table_name IN (...) 从高斯拉取所有匹配案例
         │
         ▼  逐条循环
 ┌───────────────────────────────┐
 │  run_single_case()            │
 │  执行 test_sql_code           │
 │  返回值 == 1 → pass           │
 │  其他 / 异常  → fail          │
 └───────────┬───────────────────┘
             │
     ┌───────┴────────┐
     ▼                ▼
update_sqlite_row()   update_gaussdb_row()
回写 exec_status      回写 exec_status
     exec_time             exec_time
（联合主键定位）       （联合主键定位）


from testcase_runner import update_gaussdb_row, update_sqlite_row

# 更新高斯数据库中某条记录的多个字段
update_gaussdb_row(
    gauss_config = GAUSS_CONFIG,
    table        = "dw_schema.test_cases",
    pk           = {
        "schema_name": "ods",
        "table_name":  "ods_order",
        "case_name":   "case01.sql",
    },
    updates      = {
        "exec_status": "pass",
        "exec_time":   "2024-06-01 10:30:00",
    },
)

# 更新 SQLite 中同一条记录
update_sqlite_row(
    db_path = "./testcase_registry.db",
    table   = "test_cases",
    pk      = {
        "schema_name": "ods",
        "table_name":  "ods_order",
        "case_name":   "case01.sql",
    },
    updates = {
        "exec_status": "pass",
        "exec_time":   "2024-06-01 10:30:00",
    },
)