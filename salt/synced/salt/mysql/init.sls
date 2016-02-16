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

database-{{ secret_config.mysql.database }}:
  mysql_database.present:
    - name: {{ secret_config.mysql.database }}

user-{{ secret_config.mysql.user }}:
  mysql_user.present:
    - name: {{ secret_config.mysql.user }}
    - host: localhost
    - password: {{ secret_config.mysql.password }}
    - require:
      - mysql_database: database-{{ secret_config.mysql.database }}
  mysql_grants.present:
    - name: {{ secret_config.mysql.user }}
    - grant: all privileges
    - database: {{ secret_config.mysql.database }}.*
    - user: {{ secret_config.mysql.user }}
    - require:
      - mysql_user: user-{{ secret_config.mysql.user }}

{% endfor %}
