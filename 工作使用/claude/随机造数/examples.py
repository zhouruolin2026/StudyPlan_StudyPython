"""
Python API 调用示例 —— 高斯数据库自动造数工具
可直接在代码中集成使用，无需命令行
"""

from data_gen import GaussDBConnector, DataFactory

# ─────────────── 1. 基础用法：全随机造数 ───────────────
def example_basic():
    connector = GaussDBConnector(
        host="localhost",
        port=5432,
        database="testdb",
        user="gaussdb",
        password="your_password",
    )
    with connector:
        factory = DataFactory(
            connector=connector,
            table_name="public.orders",   # 支持 schema.table
            count=1000,                   # 造 1000 条
        )
        inserted = factory.run()
        print(f"插入 {inserted} 条数据")


# ─────────────── 2. 指定字段固定值 ───────────────
def example_with_fixed_values():
    connector = GaussDBConnector(
        host="localhost", port=5432, database="testdb",
        user="gaussdb", password="your_password",
    )
    with connector:
        factory = DataFactory(
            connector=connector,
            table_name="public.orders",
            count=500,
            specified_values={
                "status":      "ACTIVE",          # 固定字符串
                "tenant_id":   10086,              # 固定整数
                "is_deleted":  False,              # 固定布尔
                "created_by":  "auto_test",        # 固定字符串
            },
        )
        factory.run()


# ─────────────── 3. 指定字段动态值（callable）───────────────
import random
import datetime

def example_with_dynamic_values():
    """使用 lambda 让每行生成不同的指定值"""
    connector = GaussDBConnector(
        host="localhost", port=5432, database="testdb",
        user="gaussdb", password="your_password",
    )
    with connector:
        factory = DataFactory(
            connector=connector,
            table_name="public.orders",
            count=200,
            specified_values={
                # 每行随机选一个状态
                "status": lambda: random.choice(["PENDING", "PAID", "SHIPPED", "CLOSED"]),
                # 每行生成今天内的随机时间
                "created_at": lambda: datetime.datetime.now() - datetime.timedelta(
                    seconds=random.randint(0, 86400)
                ),
                # 固定用户范围内随机
                "user_id": lambda: random.randint(1000, 9999),
            },
        )
        factory.run()


# ─────────────── 4. 预览模式（dry_run）───────────────
def example_dry_run():
    connector = GaussDBConnector(
        host="localhost", port=5432, database="testdb",
        user="gaussdb", password="your_password",
    )
    with connector:
        factory = DataFactory(
            connector=connector,
            table_name="public.users",
            count=10,
            dry_run=True,     # 仅打印 SQL，不写入
        )
        factory.run()


# ─────────────── 5. 中文字段 + 大批量 ───────────────
def example_chinese_large():
    connector = GaussDBConnector(
        host="localhost", port=5432, database="testdb",
        user="gaussdb", password="your_password",
    )
    with connector:
        factory = DataFactory(
            connector=connector,
            table_name="public.products",
            count=50000,
            batch_size=1000,        # 每批 1000 条，提升性能
            use_chinese=True,       # 字符串字段使用中文随机字符
        )
        factory.run()


if __name__ == "__main__":
    # 修改连接信息后取消注释运行
    # example_basic()
    # example_with_fixed_values()
    # example_with_dynamic_values()
    # example_dry_run()
    print("请修改连接信息后，取消注释对应示例函数再运行")
