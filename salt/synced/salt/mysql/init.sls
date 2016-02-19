{% from 'macros.sls' import foreach_branch with context %}

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
    - template: jinja
    - defaults:
        innodb_buffer_pool_size: {{ pillar.innodb_buffer_pool_size }}
    - require:
      - pkg: mysql-server
  service.running:
    - name: mysql
    - enable: True
    - watch:
      - file: mysql-server

{% call(branch, config) foreach_branch() %}

{% if pillar.secret_branches[branch] is defined and pillar.secret_branches[branch] %}
{% set secret_config = pillar.secret_branches[branch] %}

{% if  secret_config.mysql is defined and secret_config.mysql %}
{% set mysql = secret_config.mysql %}

database-{{ branch }}:
  mysql_database.present:
    - name: {{ mysql.database }}
    - require:
      - service: mysql-server

user-{{ branch }}:
  mysql_user.present:
    - name: {{ mysql.user }}
    - password: {{ mysql.password }}
    - require:
      - mysql_database: database-{{ branch }}
  mysql_grants.present:
    - grant: all privileges
    - database: {{ mysql.database }}.*
    - user: {{ mysql.user }}
    - require:
      - mysql_user: user-{{ branch }}

{% endif %}

{% endif %}

{% endcall %}
