CREATE OR REPLACE FUNCTION random_table_data(
    target_table TEXT,
    row_count BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    col RECORD;
    col_list TEXT := '';
    val_list TEXT := '';
    sql TEXT;
BEGIN
    -- 遍历目标表字段
    FOR col IN
        SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale
        FROM information_schema.columns
        WHERE table_schema = split_part(target_table,'.',1)
          AND table_name = split_part(target_table,'.',2)
        ORDER BY ordinal_position
    LOOP
        IF col_list <> '' THEN
            col_list := col_list || ', ';
            val_list := val_list || ', ';
        END IF;

        col_list := col_list || col.column_name;

        -- 根据字段类型生成高性能随机数据
        IF col.data_type = 'smallint' THEN
            val_list := val_list || '(random()*least(32766,gs))::smallint - (random()*least(32766,gs))::smallint';
        ELSIF col.data_type LIKE '%int%' THEN
            val_list := val_list || '(random()*gs)::int-(random()*gs)::int';
        ELSIF col.data_type = 'real' or col.data_type like 'double%' THEN
            val_list := val_list || '(random()*100)::int';
        ELSIF col.data_type = 'numeric' THEN
            val_list := val_list || format('(random() * least(gs, (10::numeric^(%s-%s) - 10::numeric^(-%s))))::numeric(%s, %s)',
                           COALESCE(col.numeric_precision),
                           COALESCE(col.numeric_scale, 0),
                           COALESCE(col.numeric_scale, 0),
                           COALESCE(col.numeric_precision),
                           COALESCE(col.numeric_scale, 0));
        ELSIF col.data_type LIKE '%char%' OR col.data_type = 'text' THEN
            val_list := val_list || format('substr(md5(gs||random()::text),1,(random()*(%s-1))::int+1)', COALESCE(col.character_maximum_length,32));
        ELSIF col.data_type LIKE 'timestamp%' THEN
            val_list := val_list || '(now() - random() * interval ''365 days'')';
        ELSIF col.data_type = 'date' THEN
            val_list := val_list || '(current_date - (random()*365)::int)';
        ELSIF col.data_type = 'boolean' THEN
            val_list := val_list || '(random() > 0.5)';
        ELSIF col.data_type = 'uuid' THEN
            val_list := val_list || format(
                '(
            	  lower(substr(md5(random()::text || clock_timestamp()::text || gs),1,8) || ''-'' ||
                  substr(md5(random()::text || clock_timestamp()::text || gs),9,4) || ''-'' ||
                  substr(md5(random()::text || clock_timestamp()::text || gs),13,4) || ''-'' ||
                  substr(md5(random()::text || clock_timestamp()::text || gs),17,4) || ''-'' ||
                  substr(md5(random()::text || clock_timestamp()::text || gs),21,12))
        		 )::uuid'
            );
        ELSE
            val_list := val_list || 'NULL';
        END IF;
    END LOOP;

    -- 生成动态 SQL，确保 generate_series 列名为 gs
    sql := format(
        'INSERT into %s (%s) SELECT %s FROM generate_series(1,%s) AS gs;',
        target_table, col_list, val_list, row_count
    );

    -- 调试打印 SQL，可注释掉
    RAISE NOTICE '%', sql;
    
    EXECUTE format('TRUNCATE TABLE %s;', target_table);
    -- 执行生成数据
    EXECUTE sql;
END;
$$;