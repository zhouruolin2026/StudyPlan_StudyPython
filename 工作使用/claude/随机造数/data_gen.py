"""
高斯数据库自动化造数工具
支持：按表结构自动生成随机数据，支持指定字段值，批量插入
"""

import random
import string
import decimal
import datetime
import uuid
import logging
import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Tuple

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("[ERROR] 请先安装依赖: pip install psycopg2-binary")
    sys.exit(1)

# ─────────────────────────── 日志配置 ───────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─────────────────────────── 数据库连接 ───────────────────────────
class GaussDBConnector:
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.dsn = dict(host=host, port=port, dbname=database, user=user, password=password)
        self.conn = None
        self.cursor = None

    def connect(self):
        logger.info(f"连接数据库 {self.dsn['host']}:{self.dsn['port']}/{self.dsn['dbname']} ...")
        self.conn = psycopg2.connect(**self.dsn)
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        logger.info("数据库连接成功 ✓")
        return self

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("数据库连接已关闭")

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        self.close()


# ─────────────────────────── 表结构查询 ───────────────────────────
def get_table_columns(cursor, table_name: str, schema: str = "public") -> List[Dict]:
    """
    查询表字段结构，返回字段列表
    每个字段包含: column_name, data_type, character_maximum_length,
                  numeric_precision, numeric_scale, is_nullable, column_default
    """
    # 支持 schema.table 写法
    if "." in table_name:
        schema, table_name = table_name.split(".", 1)

    sql = """
        SELECT
            c.column_name,
            c.data_type,
            c.udt_name,
            c.character_maximum_length,
            c.numeric_precision,
            c.numeric_scale,
            c.datetime_precision,
            c.is_nullable,
            c.column_default,
            c.ordinal_position,
            -- 是否主键
            CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END AS is_primary_key,
            -- 是否自增序列
            CASE WHEN c.column_default LIKE 'nextval%%' THEN true ELSE false END AS is_serial
        FROM information_schema.columns c
        LEFT JOIN (
            SELECT ku.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage ku
                ON tc.constraint_name = ku.constraint_name
                AND tc.table_schema = ku.table_schema
                AND tc.table_name = ku.table_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema = %s
              AND tc.table_name = %s
        ) pk ON pk.column_name = c.column_name
        WHERE c.table_schema = %s
          AND c.table_name = %s
        ORDER BY c.ordinal_position
    """
    cursor.execute(sql, (schema, table_name, schema, table_name))
    columns = cursor.fetchall()

    if not columns:
        raise ValueError(f"表 '{schema}.{table_name}' 不存在或无权限访问")

    result = [dict(col) for col in columns]
    logger.info(f"获取表结构成功，共 {len(result)} 个字段")
    for col in result:
        pk_flag = " [PK]" if col["is_primary_key"] else ""
        serial_flag = " [SERIAL]" if col["is_serial"] else ""
        nullable = "NULL" if col["is_nullable"] == "YES" else "NOT NULL"
        logger.debug(f"  {col['column_name']:30s} {col['data_type']:20s} {nullable}{pk_flag}{serial_flag}")
    return result


# ─────────────────────────── 随机值生成器 ───────────────────────────
class RandomValueGenerator:
    """根据字段类型生成随机数据"""

    # 随机中文字符范围（可选，用于测试中文场景）
    CHINESE_CHARS = "的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也能下过子说产种面而方后多定行学法所民得经十三之进着等部度家电力里如水化高自二理起小物现实加量都两体制机当使点从业本去把性好应开它合还因由其些然前外天政四日那社义事平形相全表间样与关各重新线内数正心力理明真代高长党得向情长求更度动和民家物生大最第"
    
    def __init__(self, use_chinese: bool = False):
        self.use_chinese = use_chinese

    def random_string(self, max_length: int = 255) -> str:
        """生成随机字符串，填满最大长度"""
        length = max_length if max_length and max_length <= 255 else min(max_length or 255, 255)
        if self.use_chinese:
            return "".join(random.choices(self.CHINESE_CHARS, k=length))
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    def random_int(self, precision: Optional[int] = None, type_name: str = "integer") -> int:
        """生成随机整数，贴近类型最大值"""
        max_vals = {
            "smallint":  32767,
            "int2":      32767,
            "integer":   2147483647,
            "int4":      2147483647,
            "int":       2147483647,
            "bigint":    9223372036854775807,
            "int8":      9223372036854775807,
        }
        max_val = max_vals.get(type_name.lower(), 2147483647)
        # 生成接近最大值的随机数（后 20% 区间）
        lower = int(max_val * 0.8)
        return random.randint(lower, max_val)

    def random_numeric(self, precision: int = 18, scale: int = 6) -> decimal.Decimal:
        """生成随机 numeric/decimal，贴近精度最大值"""
        precision = precision or 18
        scale = scale or 6
        integer_digits = precision - scale
        max_int_part = 10 ** integer_digits - 1
        int_part = random.randint(int(max_int_part * 0.8), max_int_part)
        frac_part = random.randint(0, 10 ** scale - 1)
        value = decimal.Decimal(f"{int_part}.{str(frac_part).zfill(scale)}")
        return value

    def random_float(self, type_name: str = "float8") -> float:
        """生成随机浮点数"""
        return round(random.uniform(1e6, 1e15), 6)

    def random_bool(self) -> bool:
        return random.choice([True, False])

    def random_date(self) -> datetime.date:
        start = datetime.date(1970, 1, 1)
        end = datetime.date(2099, 12, 31)
        delta = end - start
        return start + datetime.timedelta(days=random.randint(0, delta.days))

    def random_datetime(self, with_tz: bool = False) -> datetime.datetime:
        d = self.random_date()
        t = datetime.time(
            random.randint(0, 23),
            random.randint(0, 59),
            random.randint(0, 59),
            random.randint(0, 999999),
        )
        dt = datetime.datetime.combine(d, t)
        if with_tz:
            tz = datetime.timezone(datetime.timedelta(hours=random.choice([-12,-8,-5,0,1,8,9])))
            dt = dt.replace(tzinfo=tz)
        return dt

    def random_time(self) -> datetime.time:
        return datetime.time(
            random.randint(0, 23),
            random.randint(0, 59),
            random.randint(0, 59),
        )

    def random_uuid(self) -> str:
        return str(uuid.uuid4())

    def random_json(self) -> str:
        keys = random.choices(string.ascii_lowercase, k=random.randint(2, 5))
        obj = {k: random.randint(1, 9999) for k in keys}
        return json.dumps(obj)

    def random_bytea(self, max_length: int = 64) -> bytes:
        length = random.randint(1, min(max_length, 64))
        return bytes(random.getrandbits(8) for _ in range(length))

    def random_array(self, element_type: str, length: int = 3) -> List:
        """生成简单数组"""
        gen = {
            "int4": lambda: random.randint(1, 99999),
            "int8": lambda: random.randint(1, 9999999999),
            "text": lambda: self.random_string(20),
            "float8": lambda: round(random.uniform(0, 9999), 4),
        }
        fn = gen.get(element_type, lambda: random.randint(1, 999))
        return [fn() for _ in range(length)]

    def generate(self, col: Dict) -> Any:
        """根据字段元数据生成随机值"""
        data_type = col["data_type"].lower()
        udt_name = (col.get("udt_name") or "").lower()

        # 字符串类型
        if data_type in ("character varying", "varchar", "character", "char", "bpchar"):
            max_len = col.get("character_maximum_length") or 255
            return self.random_string(max_len)

        if data_type == "text" or udt_name == "text":
            return self.random_string(500)

        if data_type == "name":
            return self.random_string(63)

        # 整数类型
        if data_type in ("smallint", "integer", "int", "int2", "int4"):
            return self.random_int(type_name=data_type)

        if data_type in ("bigint", "int8"):
            return self.random_int(type_name="bigint")

        # 浮点
        if data_type in ("real", "float4", "double precision", "float8", "float"):
            return self.random_float()

        # 精确数值
        if data_type in ("numeric", "decimal"):
            p = col.get("numeric_precision") or 18
            s = col.get("numeric_scale") or 6
            return self.random_numeric(p, s)

        # 布尔
        if data_type == "boolean":
            return self.random_bool()

        # 日期时间
        if data_type == "date":
            return self.random_date()

        if data_type in ("timestamp without time zone", "timestamp"):
            return self.random_datetime(with_tz=False)

        if data_type in ("timestamp with time zone", "timestamptz"):
            return self.random_datetime(with_tz=True)

        if data_type in ("time without time zone", "time"):
            return self.random_time()

        if data_type in ("time with time zone", "timetz"):
            return self.random_time()

        # UUID
        if data_type == "uuid":
            return self.random_uuid()

        # JSON
        if data_type in ("json", "jsonb"):
            return self.random_json()

        # 二进制
        if data_type == "bytea":
            max_len = col.get("character_maximum_length") or 64
            return self.random_bytea(max_len)

        # 数组类型（udt_name 以 _ 开头）
        if udt_name.startswith("_"):
            element_type = udt_name[1:]
            return self.random_array(element_type)

        # 枚举或其他，返回随机字符串
        logger.warning(f"未识别类型 '{data_type}' (udt={udt_name})，使用默认字符串")
        return self.random_string(50)


# ─────────────────────────── 造数核心 ───────────────────────────
class DataFactory:
    def __init__(
        self,
        connector: GaussDBConnector,
        table_name: str,
        count: int,
        specified_values: Optional[Dict[str, Any]] = None,
        batch_size: int = 500,
        use_chinese: bool = False,
        dry_run: bool = False,
    ):
        self.connector = connector
        self.table_name = table_name
        self.count = count
        self.specified_values = specified_values or {}
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.generator = RandomValueGenerator(use_chinese=use_chinese)

    def _build_row(self, columns: List[Dict]) -> Dict[str, Any]:
        """为一行数据生成值"""
        row = {}
        for col in columns:
            name = col["column_name"]

            # 跳过自增列
            if col.get("is_serial"):
                continue

            # 优先使用指定值（支持 callable，每行重新调用）
            if name in self.specified_values:
                val = self.specified_values[name]
                row[name] = val() if callable(val) else val
                continue

            # 非空字段必须生成值；可空字段随机 10% 概率给 NULL
            if col["is_nullable"] == "YES" and random.random() < 0.10:
                row[name] = None
            else:
                row[name] = self.generator.generate(col)

        return row

    def _insert_batch(self, cursor, columns: List[Dict], rows: List[Dict]):
        """批量插入"""
        col_names = list(rows[0].keys())
        placeholders = ", ".join([f"%({c})s" for c in col_names])
        quoted_cols = ", ".join([f'"{c}"' for c in col_names])
        sql = f'INSERT INTO {self.table_name} ({quoted_cols}) VALUES ({placeholders})'

        if self.dry_run:
            logger.info(f"[DRY RUN] SQL: {sql}")
            logger.info(f"[DRY RUN] 示例行: {rows[0]}")
            return

        psycopg2.extras.execute_batch(cursor, sql, rows, page_size=self.batch_size)

    def run(self) -> int:
        """执行造数并插入，返回成功插入行数"""
        cursor = self.connector.cursor
        conn = self.connector.conn

        # 1. 获取表结构
        schema = "public"
        tname = self.table_name
        if "." in self.table_name:
            schema, tname = self.table_name.split(".", 1)
        columns = get_table_columns(cursor, tname, schema)

        # 2. 打印表结构概览
        self._print_schema(columns)

        # 3. 校验 specified_values 字段名
        col_names_set = {c["column_name"] for c in columns}
        for k in self.specified_values:
            if k not in col_names_set:
                raise ValueError(f"指定字段 '{k}' 不存在于表 '{self.table_name}' 中")

        # 4. 分批造数插入
        inserted = 0
        remaining = self.count
        batch_no = 0

        while remaining > 0:
            current_batch = min(remaining, self.batch_size)
            rows = [self._build_row(columns) for _ in range(current_batch)]

            batch_no += 1
            logger.info(f"正在插入第 {batch_no} 批，本批 {current_batch} 条 ...")
            self._insert_batch(cursor, columns, rows)

            if not self.dry_run:
                conn.commit()

            inserted += current_batch
            remaining -= current_batch
            logger.info(f"累计已插入: {inserted}/{self.count}")

        return inserted

    def _print_schema(self, columns: List[Dict]):
        logger.info(f"\n{'─'*60}")
        logger.info(f"表名: {self.table_name}  |  目标造数: {self.count} 条")
        logger.info(f"{'─'*60}")
        logger.info(f"{'字段名':<30} {'类型':<25} {'可空':<8} {'备注'}")
        logger.info(f"{'─'*60}")
        for col in columns:
            nullable = "YES" if col["is_nullable"] == "YES" else "NO "
            flags = []
            if col.get("is_primary_key"): flags.append("PK")
            if col.get("is_serial"):      flags.append("SERIAL")
            if col["column_name"] in self.specified_values: flags.append("SPECIFIED")
            logger.info(
                f"{col['column_name']:<30} {col['data_type']:<25} {nullable:<8} {','.join(flags)}"
            )
        logger.info(f"{'─'*60}\n")


# ─────────────────────────── CLI 入口 ───────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        description="高斯数据库自动造数工具",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
示例:
  # 基本造数
  python data_gen.py --table public.orders --count 1000

  # 指定字段值
  python data_gen.py --table public.orders --count 500 \\
      --set status=active --set user_id=12345

  # 使用配置文件
  python data_gen.py --config db_config.json --table users --count 200

  # 仅预览，不写入
  python data_gen.py --table users --count 10 --dry-run
        """,
    )
    # 数据库连接参数
    parser.add_argument("--host",     default="localhost",  help="数据库主机")
    parser.add_argument("--port",     type=int, default=5432, help="端口 (默认 5432)")
    parser.add_argument("--database", default="postgres",   help="数据库名")
    parser.add_argument("--user",     default="gaussdb",    help="用户名")
    parser.add_argument("--password", default="",           help="密码")
    parser.add_argument("--config",   help="JSON 配置文件路径（可替代以上参数）")

    # 造数参数
    parser.add_argument("--table",   required=True, help="表名，支持 schema.table 格式")
    parser.add_argument("--count",   type=int, required=True, help="造数数量")
    parser.add_argument(
        "--set",
        action="append",
        metavar="FIELD=VALUE",
        dest="set_values",
        help="指定字段值，格式: field=value，可多次使用",
    )
    parser.add_argument("--batch-size", type=int, default=500, help="批量插入大小 (默认 500)")
    parser.add_argument("--chinese",    action="store_true",   help="字符串字段使用中文随机字符")
    parser.add_argument("--dry-run",    action="store_true",   help="预览模式，不实际写入数据库")
    parser.add_argument("--verbose",    action="store_true",   help="输出 DEBUG 日志")

    return parser.parse_args()


def load_config(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_set_values(set_list: Optional[List[str]]) -> Dict[str, Any]:
    """解析 --set key=value 参数，自动尝试转换为数字/bool"""
    if not set_list:
        return {}
    result = {}
    for item in set_list:
        if "=" not in item:
            raise ValueError(f"--set 参数格式错误: '{item}'，应为 field=value")
        key, value = item.split("=", 1)
        # 类型推断
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        elif value.lower() in ("null", "none"):
            value = None
        else:
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass  # 保持字符串
        result[key.strip()] = value
    return result


def main():
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 读取数据库连接配置
    if args.config:
        cfg = load_config(args.config)
    else:
        cfg = {
            "host":     args.host,
            "port":     args.port,
            "database": args.database,
            "user":     args.user,
            "password": args.password,
        }

    # 解析指定字段值
    specified_values = parse_set_values(args.set_values)
    if specified_values:
        logger.info(f"指定字段值: {specified_values}")

    # 执行造数
    connector = GaussDBConnector(**cfg)
    with connector:
        factory = DataFactory(
            connector=connector,
            table_name=args.table,
            count=args.count,
            specified_values=specified_values,
            batch_size=args.batch_size,
            use_chinese=args.chinese,
            dry_run=args.dry_run,
        )
        inserted = factory.run()

    if args.dry_run:
        logger.info("✓ [DRY RUN] 预览完成，未写入数据")
    else:
        logger.info(f"✓ 造数完成！共插入 {inserted} 条数据到表 [{args.table}]")


if __name__ == "__main__":
    main()
