
-- 判断主键唯一性
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 
            FROM 表名 
            GROUP BY 业务主键字段 
            HAVING COUNT(*) > 1
        ) THEN 0  -- 发现了重复，验证失败，返回 0
        ELSE 1      -- 没发现任何重复，验证通过，返回 1
    END AS is_unique;


SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 
            FROM 表名 
            GROUP BY 字段A, 字段B, 字段C  -- 这里列出所有组成主键的字段
            HAVING COUNT(*) > 1
        ) THEN 0  -- 存在重复组合，校验失败
        ELSE 1      -- 所有组合均唯一，校验通过
    END AS is_unique;

-- 判断空表
select 
    case when exists (select 1 from table_name where etl_dt='2024-01-01' limit 1) then 1 else 0 end as data_exists;

-- 主键为空校验

SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 
            FROM 表名 
            WHERE 字段A IS NULL 
              AND 字段B IS NULL 
              AND 字段C IS NULL
            limit 1
        ) THEN 0  -- 发现全空行，校验失败
        ELSE 1 
    END AS no_all_nulls;
