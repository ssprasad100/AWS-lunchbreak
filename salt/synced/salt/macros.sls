{% macro foreach_branch() -%}

{% for branch, config in pillar.get('branches', {}).iteritems() -%}

{% set allowed = false %}
{% if pillar.specify_branches_required is defined and pillar.specify_branches_required -%}
 {% if pillar.specified_branches is defined and branch in pillar.specified_branches %}
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

