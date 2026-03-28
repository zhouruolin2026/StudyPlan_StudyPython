-- 最快方法：SELECT COUNT(*), SUM(hashtext(col::text)) FROM table_name;（利用内置哈希函数求和，比 MD5 拼接字符串性能高几个数量级）。


SELECT 
    COUNT(*) as total_rows, 
    SUM(hashtext(column_name::text)) as content_hash 
FROM table_a;
