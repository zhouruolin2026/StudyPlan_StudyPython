CREATE OR REPLACE FUNCTION get_table_concat_data(p_table_name text, p_exclude_n integer)
RETURNS SETOF text AS $$
DECLARE
    v_cols text;
    v_sql text;
BEGIN
    -- 1. 获取该表除去最后 n 个字段之外的所有列名，并用逗号隔开
    SELECT string_agg(quote_ident(column_name), ', ' ORDER BY ordinal_position)
    INTO v_cols
    FROM (
        SELECT column_name, ordinal_position
        FROM information_schema.columns
        WHERE table_name = p_table_name
        ORDER BY ordinal_position
        -- 核心逻辑：总列数减去排除的 n 个
        LIMIT (SELECT count(*) - p_exclude_n FROM information_schema.columns WHERE table_name = p_table_name)
    ) sub;

    -- 2. 构建动态 SQL，使用 concat_ws 以 '|' 拼接
    -- concat_ws 会自动忽略 NULL 值，如果你需要保留 NULL 建议改用 a || '|' || b
    v_sql := 'SELECT concat_ws(''|'', ' || v_cols || ') FROM ' || quote_ident(p_table_name);

    -- 3. 执行并返回结果
    RETURN QUERY EXECUTE v_sql;
END;
$$ LANGUAGE plpgsql;




CREATE OR REPLACE FUNCTION concat_table_cols(
    p_table_name TEXT,
    p_exclude_last_n INT
)
RETURNS SETOF TEXT
AS $$
DECLARE
    v_sql TEXT;
    v_cols TEXT;
BEGIN
    -- 1. 获取字段列表（去掉最后 n 个）
    SELECT string_agg(
        format('%I', column_name),
        ', '
        ORDER BY ordinal_position
    )
    INTO v_cols
    FROM (
        SELECT column_name, ordinal_position
        FROM information_schema.columns
        WHERE table_name = p_table_name
        ORDER BY ordinal_position
        LIMIT (
            SELECT COUNT(*) - p_exclude_last_n
            FROM information_schema.columns
            WHERE table_name = p_table_name
        )
    ) t;

    -- 防御：避免 n 太大
    IF v_cols IS NULL THEN
        RAISE EXCEPTION 'Invalid column selection: check table or exclude count';
    END IF;

    -- 2. 拼接 SQL（concat_ws 自动处理 NULL）
    v_sql := format(
        'SELECT concat_ws(''|'', %s) FROM %I',
        v_cols,
        p_table_name
    );

    -- 3. 返回结果
    RETURN QUERY EXECUTE v_sql;

END;
$$ LANGUAGE plpgsql;




CREATE OR REPLACE FUNCTION concat_table_cols(
    p_schema_name TEXT,
    p_table_name TEXT,
    p_exclude_last_n INT
)
RETURNS SETOF TEXT
AS $$
DECLARE
    v_sql TEXT;
    v_cols TEXT;
BEGIN
    SELECT string_agg(
        format('%I', column_name),
        ', '
        ORDER BY ordinal_position
    )
    INTO v_cols
    FROM (
        SELECT column_name, ordinal_position
        FROM information_schema.columns
        WHERE table_name = p_table_name
          AND table_schema = p_schema_name
        ORDER BY ordinal_position
        LIMIT (
            SELECT COUNT(*) - p_exclude_last_n
            FROM information_schema.columns
            WHERE table_name = p_table_name
              AND table_schema = p_schema_name
        )
    ) t;

    IF v_cols IS NULL THEN
        RAISE EXCEPTION 'Invalid column selection';
    END IF;

    v_sql := format(
        'SELECT concat_ws(''|'', %s) FROM %I.%I',
        v_cols,
        p_schema_name,
        p_table_name
    );

    RETURN QUERY EXECUTE v_sql;

END;
$$ LANGUAGE plpgsql;


IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_name = p_table_name
      AND table_schema = p_schema_name
) THEN
    RAISE EXCEPTION 'table not found';
END IF;





CREATE OR REPLACE FUNCTION concat_table_cols(
    p_schema_name TEXT,
    p_table_name TEXT,
    p_exclude_last_n INT,
    p_where TEXT DEFAULT NULL
)
RETURNS SETOF TEXT
AS $$
DECLARE
    v_sql TEXT;
    v_cols TEXT;
    v_where_clause TEXT := '';
BEGIN
    -- 1. 获取字段列表（去掉最后 n 个）
    SELECT string_agg(
        format('%I', column_name),
        ', '
        ORDER BY ordinal_position
    )
    INTO v_cols
    FROM (
        SELECT column_name, ordinal_position
        FROM information_schema.columns
        WHERE table_name = p_table_name
          AND table_schema = p_schema_name
        ORDER BY ordinal_position
        LIMIT (
            SELECT COUNT(*) - p_exclude_last_n
            FROM information_schema.columns
            WHERE table_name = p_table_name
              AND table_schema = p_schema_name
        )
    ) t;

    -- 防御
    IF v_cols IS NULL THEN
        RAISE EXCEPTION 'Invalid column selection';
    END IF;

    -- 2. 处理 where 条件
    IF p_where IS NOT NULL AND trim(p_where) <> '' THEN
        v_where_clause := ' WHERE ' || p_where;
    END IF;

    -- 3. 拼接 SQL
    v_sql := format(
        'SELECT concat_ws(''|'', %s) FROM %I.%I%s',
        v_cols,
        p_schema_name,
        p_table_name,
        v_where_clause
    );

    -- 4. 执行并返回
    RETURN QUERY EXECUTE v_sql;

END;
$$ LANGUAGE plpgsql;