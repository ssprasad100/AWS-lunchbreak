ufw:
  pkg.installed


{% macro ufw_rule(rule, grep_pattern) -%}
{% if grep_pattern != '' %}
ufw {{ rule }}:
  cmd.run:
    - unless: 'ufw status | grep {{ grep_pattern }}'
{% else %}
ufw {{ rule }}:
  cmd.run
{% endif %}
{%- endmacro %}

{{ ufw_rule('enable', 'Status: active') }}

{{ ufw_rule('default deny incoming', '') }}
{{ ufw_rule('default allow outgoing', '') }}
{{ ufw_rule('allow ssh', '') }}
{{ ufw_rule('allow 80/tcp', '') }}
{{ ufw_rule('allow 443/tcp', '') }}
{{ ufw_rule('disable', '') }}
{{ ufw_rule('--force enable', '') }}
