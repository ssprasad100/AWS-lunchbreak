nginx:
  pkg.installed

{% set nginx_dir = '/etc/nginx' %}

{{ nginx_dir }}/ssl/lunchbreak.key:
  file.managed:
    - source: salt://keys/tls/lunchbreak.key
    - makedirs: True
    - mode: 644

{{ nginx_dir }}/ssl/lunchbreak.pem:
  file.managed:
    - source: salt://keys/tls/lunchbreak.pem
    - makedirs: True
    - mode: 644

{{ nginx_dir }}/ssl/dhparam.pem:
  file.managed:
    - source: salt://keys/tls/dhparam.pem
    - makedirs: True
    - mode: 644

{{ nginx_dir }}/sites-enabled/default:
  file.absent


{% macro nginx_config(branch, config) -%}

{% set path = pillar.project_path + branch %}

{% if config.ssl %}
  {% set source = 'salt://nginx/files/server-https' %}
{% else %}
  {% set source = 'salt://nginx/files/server-http' %}
{% endif %}

{{ nginx_dir }}/sites-enabled/{{ config.host }}:
  file.managed:
    - source: {{ source }}
    - makedirs: True
    - mode: 644
    - template: jinja
    - defaults:
        branch: {{ branch }}
        host: {{ config.host }}
        path: {{ path }}
        static_url: {{ pillar.static.url }}
        static_relative: {{ pillar.static.relative_path }}
        ssl_path: {{ nginx_dir }}/ssl

{%- endmacro %}

{% for branch, config in pillar.get('branches', {}).items() %}

{{ nginx_config(branch, config) }}

{% endfor %}

{% if pillar.local is defined and pillar.local %}
{{ nginx_config('development', pillar.local) }}
{% endif %}

nginx-service:
  service.running:
    - name: nginx
    - default: True
    - watch:
      - pkg: nginx
{% for branch, config in pillar.get('branches', {}).items() %}
      - file: {{ nginx_dir }}/sites-enabled/{{ config.host }}
{% endfor %}
