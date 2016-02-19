{% from 'macros.sls' import foreach_branch with context %}

uwsgi-dependencies:
  pkg.installed:
    - pkgs:
      - libpcre3
      - libpcre3-dev

uwsgi:
  pip.installed:
    - bin_env: /usr/local/pyenv/shims/pip
    - require:
      - pkg: uwsgi-dependencies

/var/sockets:
  file.directory:
    - makedirs: True
    - require:
      - pip: uwsgi
    - user: www-data
    - group: www-data

{% set apps = '/etc/uwsgi/apps' %}
{{ apps }}:
  file.directory:
    - makedirs: True
    - require:
      - file: /var/sockets
    - user: www-data
    - group: www-data

{% set log = '/var/log/uwsgi/emperor.log' %}
{{ log }}:
  file.managed:
    - mode: 666
    - makedirs: True
    - replace: False
    - require:
      - pip: uwsgi
    - user: www-data
    - group: www-data

{% set uwsgi_conf = '/etc/init/uwsgi.conf' %}
{{ uwsgi_conf }}:
  file.managed:
    - mode: 755
    - makedirs: True
    - source: salt://uwsgi/files/uwsgi.conf
    - template: jinja
    - user: www-data
    - group: www-data
    - defaults:
        apps: {{ apps }}
        log: {{ log }}
    - require:
      - pip: uwsgi

{% call(branch, config) foreach_branch() %}

{% set path = pillar.project_path + branch %}
{% set secret_config = pillar.secret_branches[branch] %}

{{ apps }}/{{ config.host }}.ini:
  file.managed:
    - mode: 644
    - makedirs: True
    - source: salt://uwsgi/files/app.ini
    - template: jinja
    - defaults:
        branch: {{ branch }}
        host: {{ config.host }}
        chdir: {{ path }}
        virtualenv: {{ pillar.virtualenv_path }}{{ branch }}
        password_var: LB_{{ branch }}_password
        password: {{ secret_config.mysql.password }}
        business_apns_certificate: {{ pillar.certificate_directory }}{{ config.certificates.business }}
        customers_apns_certificate: {{ pillar.certificate_directory }}{{ config.certificates.customers }}
        opbeat_organization_id: {{ pillar.opbeat.organization_id }}
        opbeat_app_id: {{ pillar.opbeat.app_id }}
        opbeat_secret_token: {{ pillar.opbeat.secret_token }}
        sendgrid_user: {{ pillar.sendgrid.user }}
        sendgrid_password: {{ pillar.sendgrid.password }}
        google_cloud_secret: {{ pillar.google_cloud_secret }}
    - require:
      - file: {{ apps }}
      - file: {{ log }}
      - file: {{ uwsgi_conf }}

{% endcall %}

uwsgi-service:
  service.running:
    - name: uwsgi
    - default: True
    - watch:
      - file: {{ uwsgi_conf }}
