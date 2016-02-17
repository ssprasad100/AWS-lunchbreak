mysql-server:
  debconf.set:
    - name: mysql-server
    - data:
        'mysql-server/root_password':  {'type': 'string', 'value': '{{ pillar.get("mysql_root_password", "password") }}'}
        'mysql-server/root_password_again': {'type': 'string', 'value': '{{ pillar.get("mysql_root_password", "password") }}'}
  pkg.installed:
    - pkgs:
      - mysql-server
      # MySQL-python pip module
      - libmysqlclient-dev
    - require:
      - debconf: mysql-server
  file.managed:
    - name: /etc/mysql/my.conf
    - source: salt://mysql/files/my.conf
    - require:
      - pkg: mysql-server
  service.running:
    - name: mysql
    - enable: True
    - watch:
      - file: mysql-server

{% macro mysql_config(id, config) %}

{% if config.branch is defined and config.branch %}
  {% set branch = config.branch %}
{% else %}
  {% set branch = id %}
{% endif %}

{% if pillar.secret_branches[branch] is defined and pillar.secret_branches[branch] %}
  {% set secret_config = pillar.secret_branches[branch] %}
  {% if  secret_config.mysql is defined and secret_config.mysql %}
    {% set mysql = secret_config.mysql %}
  {% endif %}
{% endif %}

{% if mysql is defined %}

database-{{ id }}:
  mysql_database.present:
    - name: {{ mysql.database }}

user-{{ id }}:
  mysql_user.present:
    - name: {{ mysql.user }}
    - password: {{ mysql.password }}
    - require:
      - mysql_database: database-{{ id }}
  mysql_grants.present:
    - grant: all privileges
    - database: {{ mysql.database }}.*
    - user: {{ mysql.user }}
    - require:
      - mysql_user: user-{{ id }}

{% endif %}

{% endmacro %}

{% for branch, config in pillar.get('branches', {}).items() %}
{{ mysql_config(branch, config) }}
{% endfor %}

