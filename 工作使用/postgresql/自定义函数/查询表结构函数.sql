CREATE OR REPLACE FUNCTION get_table_columns(p_table_text text)
RETURNS TABLE(column_name text, column_type text)
LANGUAGE sql
AS $$
SELECT a.attname,
			 format_type(a.atttypid, a.atttypmod) AS data_type
FROM pg_attribute a
WHERE a.attrelid = (p_table_text::regclass)::oid
	AND a.attnum > 0
	AND NOT a.attisdropped
ORDER BY a.attnum;
$$;

-- example usage:
-- select * from get_table_columns('public.my_table');