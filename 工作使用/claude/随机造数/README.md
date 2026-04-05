# 高斯数据库自动化造数工具

自动查询表结构，按字段类型生成随机最大值，批量插入高斯数据库（GaussDB / openGauss）。

---

## 安装依赖

```bash
pip install psycopg2-binary
```

---

## 命令行用法

### 基础造数
```bash
python data_gen.py \
  --host localhost --port 5432 \
  --database testdb --user gaussdb --password yourpwd \
  --table public.orders \
  --count 1000
```

### 指定字段值
```bash
python data_gen.py \
  --host localhost --port 5432 \
  --database testdb --user gaussdb --password yourpwd \
  --table public.orders \
  --count 500 \
  --set status=ACTIVE \
  --set tenant_id=10086 \
  --set is_deleted=false
```

### 使用配置文件
```bash
# 复制配置模板
cp db_config.example.json db_config.json
# 编辑 db_config.json 填入真实信息

python data_gen.py \
  --config db_config.json \
  --table public.users \
  --count 2000
```

### 预览模式（不写入）
```bash
python data_gen.py --config db_config.json \
  --table public.orders --count 5 --dry-run
```

### 中文数据 + 自定义批次大小
```bash
python data_gen.py --config db_config.json \
  --table public.products --count 50000 \
  --batch-size 1000 --chinese
```

---

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--host` | 数据库主机 | localhost |
| `--port` | 端口 | 5432 |
| `--database` | 数据库名 | postgres |
| `--user` | 用户名 | gaussdb |
| `--password` | 密码 | 空 |
| `--config` | JSON 配置文件路径 | — |
| `--table` | 表名（支持 schema.table）| 必填 |
| `--count` | 造数数量 | 必填 |
| `--set` | 指定字段值 `field=value`，可多次 | — |
| `--batch-size` | 批量插入大小 | 500 |
| `--chinese` | 字符串使用中文随机字符 | false |
| `--dry-run` | 预览模式，不写入 | false |
| `--verbose` | 输出 DEBUG 日志 | false |

---

## 支持的字段类型

| 类型 | 生成规则 |
|------|---------|
| `varchar(n)` / `char(n)` | 填满 n 位随机字母数字（或中文） |
| `text` | 随机 500 字符字符串 |
| `smallint` | 接近最大值 32767 的随机整数 |
| `integer` | 接近最大值 2147483647 的随机整数 |
| `bigint` | 接近最大值 9223372036854775807 的随机整数 |
| `numeric(p,s)` | 贴近精度上限的随机小数 |
| `float` / `double` | 随机大浮点数 |
| `boolean` | 随机 true/false |
| `date` | 1970-01-01 ~ 2099-12-31 内随机日期 |
| `timestamp` | 随机日期时间 |
| `timestamptz` | 带时区的随机日期时间 |
| `uuid` | 随机 UUID v4 |
| `json` / `jsonb` | 随机键值 JSON 对象 |
| `bytea` | 随机字节流 |
| 数组类型 | 随机 3 元素数组 |
| SERIAL / 自增列 | **自动跳过，由数据库生成** |
| 可空字段 | 10% 概率生成 NULL |

---

## Python API 集成

参见 `examples.py`，支持：
- 固定值 `"field": "value"`
- 动态值（每行不同）`"field": lambda: random.choice([...])`
- dry_run 预览
- 大批量高性能插入

---

## 注意事项

1. SERIAL / nextval 自增列会自动跳过，无需指定
2. 外键约束字段建议通过 `--set` 手动指定合法值
3. 唯一约束字段建议使用 `--set` 配合 `lambda` 保证唯一性
4. 大量造数建议适当增大 `--batch-size`（推荐 500-2000）
