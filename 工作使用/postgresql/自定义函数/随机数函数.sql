-- 随机整数函数

CREATE OR REPLACE FUNCTION random_int(start_int INT, finish_int INT)
RETURNS INT
LANGUAGE sql
AS $$
  SELECT CASE WHEN start_int IS NULL OR finish_int IS NULL OR start_int > finish_int THEN NULL
              ELSE (floor(random() * (finish_int - start_int + 1)) + start_int)::int
         END;
$$;

-- 随机浮点数函数，第三个参数为要保留的小数位数（返回 numeric）

CREATE OR REPLACE FUNCTION random_float(start_val NUMERIC, finish_val NUMERIC, decimals INT)
RETURNS NUMERIC
LANGUAGE sql
AS $$
  SELECT CASE 
           WHEN start_val IS NULL OR finish_val IS NULL OR decimals IS NULL 
                OR start_val > finish_val OR decimals < 0
           THEN NULL
           ELSE round( (start_val + (finish_val - start_val) * random())::numeric, decimals )
         END;
$$;

-- 随机数值函数，生成一个闭区间整数 [start, finish]，第三个参数为要保留的小数位数(默认为0,返回整数)（返回 numeric）

CREATE OR REPLACE FUNCTION random_num(
    start_val NUMERIC,
    finish_val NUMERIC,
    decimals INT DEFAULT 0
)
RETURNS NUMERIC
LANGUAGE sql
AS $$
  SELECT CASE
           WHEN start_val IS NULL OR finish_val IS NULL OR decimals IS NULL
                OR start_val > finish_val OR decimals < 0
           THEN NULL
           ELSE round( (start_val + (finish_val - start_val) * random())::numeric, decimals )
         END;
$$;

-- 随机字符串函数，长度在 [min_len, max_len]，可自定义字符集,可包含部分中文

CREATE OR REPLACE FUNCTION random_str(
    min_len INT,
    max_len INT,
    allowed TEXT DEFAULT 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789你好世界中国测试'
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    target_len INT;
    result TEXT := '';
    idx INT;
BEGIN
    -- 参数校验
    IF min_len IS NULL OR max_len IS NULL OR min_len < 0 OR max_len < 0 OR min_len > max_len THEN
        RETURN NULL;
    END IF;

    -- 随机长度
    target_len := floor(random() * (max_len - min_len + 1))::int + min_len;

    -- 循环生成随机字符
    FOR i IN 1..target_len LOOP
        idx := floor(random() * char_length(allowed))::int + 1;
        result := result || substring(allowed FROM idx FOR 1);
    END LOOP;

    RETURN result;
END;
$$;

-- 随机枚举值

CREATE OR REPLACE FUNCTION random_array_value(anyarray)
RETURNS anyelement
LANGUAGE sql
AS $$
SELECT $1[1 + floor(random() * array_length($1,1))::int];
$$;

-- 随机日期时间函数，在 start_ts 和 end_ts 之间，返回timestamp类型
-- 注意：如果需要返回格式化字符串，可以在外层调用 to_char(random_timestamp(...), fmt)
-- SELECT to_char(TIMESTAMP '2024-06-18 15:32:45','YYYY-MM-DD HH24:MI:SS'); -- 格式化示例,各种组合即可

CREATE OR REPLACE FUNCTION random_timestamp(
    start_ts TIMESTAMP,
    end_ts TIMESTAMP
)
RETURNS TIMESTAMP
LANGUAGE sql
AS $$
SELECT
    CASE
        WHEN start_ts IS NULL OR end_ts IS NULL OR start_ts > end_ts
        THEN NULL
        ELSE start_ts + random() * (end_ts - start_ts)
    END;
$$;