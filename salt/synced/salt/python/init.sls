pyenv-dependencies:
  pkg.installed:
    - pkgs:
      - git
      - make
      - build-essential
      - wget
      - curl
      - llvm
      # Python ssl extension
      - libssl-dev
      # Python zlib extension
      - zlib1g-dev
      # Python bz2 extension
      - libbz2-dev
      # Python readline extension
      - libreadline-dev
      # Python sqlite3 extension
      - libsqlite3-dev
      # Pillow jpeg
      - libjpeg-dev

python-2.7.11:
  pyenv.installed:
    - name: '2.7.11'
    - default: True
    - require:
      - pkg: pyenv-dependencies

download-pip:
  file.managed:
    - name: /tmp/get-pip.py
    - source: salt://python/files/get-pip.py
    - require:
      - pyenv: python-2.7.11

pip-install-pyenv:
  module.run:
    - name: pyenv.do
    - cmdline: python /tmp/get-pip.py
    - require:
      - file: download-pip
    - reload_modules: True

pip-install-salt:
  cmd.run:
    - name: python /tmp/get-pip.py
    - require:
      - file: download-pip
    - reload_modules: True

virtualenv:
  pip.installed:
    - bin_env: /usr/local/pyenv/shims/pip
