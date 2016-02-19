{% macro foreach_branch() %}

{% for branch, config in pillar.get('branches', {}).items() -%}

{% set allowed = false %}
{% if pillar.specify_branched_required is defined and pillar.specify_branched_required -%}
 {% if pillar.specified_branches is defined and pillar.specified_branches %}
  {% set allowed = true %}
 {% endif %}
{% else %}
  {% set allowed = true %}
{% endif %}

{% if allowed %}
{{ caller(branch, config) }}
{% endif %}

{%- endfor %}

{%- endmacro %}

