-- 创建自增函数

DROP SEQUENCE IF EXISTS global_seq;
CREATE SEQUENCE global_seq; -- 创建序列值
drop function if exists public.row_num();
CREATE OR REPLACE FUNCTION public.row_num()
RETURNS BIGINT
LANGUAGE SQL
AS $$
SELECT nextval('public.global_seq');
$$;

-- 创建重置自增函数

drop function if exists public.reset_row_num();
CREATE OR REPLACE FUNCTION public.reset_row_num()
RETURNS BIGINT
LANGUAGE SQL
AS $$
SELECT setval('public.global_seq',1,false);
$$;



-- 最新版本,使用时需要加上表名为参数

CREATE OR REPLACE FUNCTION public.reset_row_num(schema_table text)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    seq_name text;
BEGIN

    seq_name := replace(lower(schema_table),'.','_');

    EXECUTE 'CREATE SEQUENCE IF NOT EXISTS ' || quote_ident(seq_name);
	EXECUTE 'SELECT setval(''' || seq_name || ''',1,false)';

    RETURN 1;

END;
$$;

CREATE OR REPLACE FUNCTION public.row_num(schema_table text)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    seq_name text;
    result bigint;
BEGIN

    -- 统一小写 + 处理 schema
    seq_name := replace(lower(schema_table),'.','_');

    EXECUTE 'CREATE SEQUENCE IF NOT EXISTS ' || quote_ident(seq_name);
    -- 获取 nextval
    EXECUTE 'SELECT nextval(''' || seq_name || ''')'
    INTO result;

    RETURN result;

END;
$$;