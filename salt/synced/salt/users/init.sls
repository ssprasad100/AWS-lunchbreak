# Revoke any users with a role of revoked
{% for user, settings in pillar.get('revokedusers', {}).iteritems() %}
{{ user }}:
  user.absent: []
  group.absent: []

{% if settings['ssh-keys'] %}
{{ user }}_root_key:
  ssh_auth.absent:
    - user: root
    - names:
      {% for key in settings['ssh-keys'] %}
      - {{ key }}
      {% endfor %}

{{ user }}_key:
  ssh_auth.absent:
    - user: {{ user }}
    - names:
      {% for key in settings['ssh-keys'] %}
      - {{ key }}
      {% endfor %}
{% endif %}
{% endfor %}

# Add users
{% for user, settings in pillar.get('users', {}).iteritems() %}
{{ user }}:
  group.present:
    - gid: {{ settings['uid'] }}
  user.present:
    - fullname: {{ settings['fullname'] }}
    - uid: {{ settings['uid'] }}
    - gid: {{ settings['uid'] }}
    - shell: /bin/bash
    {% if grains['os'] == 'Ubuntu' %}
    - groups:
      - sudo
      - adm
      - dip
      - cdrom
      - plugdev
    {% endif %}

{% if settings['ssh-keys'] %}
{{ user }}_root_key:
  ssh_auth.present:
    - user: root
    - names:
      {% for key in settings['ssh-keys'] %}
      - {{ key }}
      {% endfor %}

{{ user }}_key:
  ssh_auth.present:
    - user: {{ user }}
    - names:
      {% for key in settings['ssh-keys'] %}
      - {{ key }}
      {% endfor %}
{% endif %}
{% endfor %}

# Allow sudoers to sudo without passwords.
# This is to avoid having to manage passwords in addition to keys
/etc/sudoers.d/sudonopasswd:
  file.managed:
    - source: salt://users/files/sudonopasswd
    - user: root
    - group: root
    - mode: 440
