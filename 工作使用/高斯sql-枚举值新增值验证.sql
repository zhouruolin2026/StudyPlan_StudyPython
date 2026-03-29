
-- 枚举值验证

SELECT 
    CASE 
        WHEN EVERY(your_column IN ('a', 'b', 'c')) THEN 1 
        ELSE 0 
    END AS result
FROM your_table;

SELECT 
    EVERY(your_column IN ('a', 'b', 'c'))::INT AS result
FROM your_table;


SELECT 
    EVERY(your_column IN ('a', 'b', 'c')) AS all_in_enum_range
FROM your_table
where condition
;


-- 存在指定值验证
SELECT EXISTS (
    SELECT 1 
    FROM your_table 
    WHERE your_column IN ('a', 'b', 'c')
) AS has_matching_value
where condition
;

SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM your_table WHERE column1 = 'a' AND condition)
         AND EXISTS (SELECT 1 FROM your_table WHERE column1 = 'b' AND condition)
        THEN 1 
        ELSE 0 
    END as has_both_a_and_b;

SELECT 
    CASE 
        WHEN COUNT(DISTINCT column1) FILTER (WHERE column1 IN ('a', 'b')) = 2 
        THEN 1 
        ELSE 0 
    END as has_both_a_and_b
FROM your_table
WHERE condition;


select
    every(
        every(column1=='value1') and 
        every(column1=='value2')
    ) as all_in_enum_range
from your_table
where condition
;



SELECT 
    EVERY(your_column IN ('a', 'b', 'c')) AS all_in_enum_range
FROM your_table;


SELECT EXISTS (
    SELECT 1 
    FROM your_table 
    WHERE your_column IN ('a', 'b', 'c')
) AS has_matching_value;




select
    case when
        bool_or(column1='value1') and 
        bool_or(column1='value2')
        then 1
    else 0 end as all_in_enum_range
from your_table
where condition
; 这么写有问题吗？


