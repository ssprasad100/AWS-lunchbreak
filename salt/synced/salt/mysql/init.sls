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

{% for branch, config in pillar.get('branches', {}).items() %}

{% set secret_config = pillar.secret_branches[branch] %}

{% if config.mysql is defined and config.mysql %}
  {% set mysql = config.mysql %}
{% elif secret_config.mysql %}
  {% set mysql = secret_config.mysql %}
{% endif %}

database-{{ mysql.database }}:
  mysql_database.present:
    - name: {{ mysql.database }}

user-{{ mysql.user }}:
  mysql_user.present:
    - name: {{ mysql.user }}
    - host: localhost
    - password: {{ mysql.password }}
    - require:
      - mysql_database: database-{{ mysql.database }}
  mysql_grants.present:
    - name: {{ mysql.user }}
    - grant: all privileges
    - database: {{ mysql.database }}.*
    - user: {{ mysql.user }}
    - require:
      - mysql_user: user-{{ mysql.user }}

{% endfor %}
