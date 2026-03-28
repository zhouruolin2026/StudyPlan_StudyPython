CREATE OR REPLACE FUNCTION read_file_md5(p_path TEXT)
RETURNS TABLE(line_text TEXT, line_md5 TEXT)
AS $$
DECLARE
    v_table_name TEXT := 'temp_ext_' || replace(uuid_generate_v4()::text, '-', '');
BEGIN
    -- 1. 创建单列 foreign table（按原始行读取）
    EXECUTE format($f$
        CREATE FOREIGN TABLE %I (
            line TEXT
        )
        SERVER file_server
        OPTIONS (
            filename %L,
            format 'text'
        )
    $f$, v_table_name, p_path);

    -- 2. 返回结果（替换分隔符 + md5）
    RETURN QUERY EXECUTE format($f$
        SELECT 
            replace(line, ',', '|') AS line_text,
            md5(replace(line, ',', '|')) AS line_md5
        FROM %I
    $f$, v_table_name);

    -- 3. 删除外表
    EXECUTE format('DROP FOREIGN TABLE %I', v_table_name);

END;
$$ LANGUAGE plpgsql;
