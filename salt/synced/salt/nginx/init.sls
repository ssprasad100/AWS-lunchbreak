{% from 'macros.sls' import foreach_branch with context %}

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


{% call(branch, config) foreach_branch() %}

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
        upstream: {{ config.host | replace('.', '-') }}
        host: {{ config.host }}
        path: {{ path }}
        static_url: {{ pillar.static.url }}
        static_relative: {{ pillar.static.relative_path }}
        ssl_path: {{ nginx_dir }}/ssl

{% endcall %}

nginx-service:
  service.running:
    - name: nginx
    - default: True
    - watch:
      - pkg: nginx
{% call(branch, config) foreach_branch() %}
      - file: {{ nginx_dir }}/sites-enabled/{{ config.host }}
{% endcall %}
