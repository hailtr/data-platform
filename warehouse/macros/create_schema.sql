{% macro create_my_schema(schema_name) %}
  
  {# Just force the SQL, skip adapter.get_relation complexity #}
  {% call statement('create_schema') %}
    CREATE SCHEMA IF NOT EXISTS `{{ target.project }}.{{ schema_name }}`
    OPTIONS(location="US");
  {% endcall %}
  
  {{ print("Executed CREATE SCHEMA for " ~ schema_name) }}
{% endmacro %}
