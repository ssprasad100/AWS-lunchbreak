openssh-server:
  pkg.installed

/etc/ssh/sshd_config:
  file.managed:
    - source: salt://ssh/files/sshd_config
    - mode: 644
    - user: root

ssh:
  service.running:
    - enable: True
    - watch:
      - file: /etc/ssh/sshd_config
