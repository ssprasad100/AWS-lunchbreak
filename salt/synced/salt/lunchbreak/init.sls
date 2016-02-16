lunchbreak-dependencies:
  pkg.installed:
    - pkgs:
      - libffi-dev

{% set ssh_key = pillar.lunchbreak_path + 'id_rsa' %}

{{ pillar.lunchbreak_path }}:
  file.directory:
    - mode: 755
    - makedirs: True
    - recurse:
      - mode

github-identity:
  file.managed:
    - name: {{ ssh_key }}
    - source: salt://keys/ssh/id_rsa
    - mode: 600
    - makedirs: True

github.com:
  ssh_known_hosts.present:
    - require:
      - file: github-identity

{% macro cmd_ssh_key(command) -%}
  cmd.run:
    - name: "ssh-agent bash -c 'ssh-add {{ ssh_key }}; {{ command }}'"
{%- endmacro %}

{% for branch, config in pillar.get('branches', {}).items() %}

{% set path = pillar.project_path + branch %}
{% set secret_config = pillar.secret_branches[branch] %}

{{ branch }}-clone:
  {{ cmd_ssh_key('git clone ' + pillar.git_repository + ' ' + path) }}
    - unless:
      - ls {{ path }}
    - require:
      - ssh_known_hosts: github.com

{{ branch }}-fetch:
  {{ cmd_ssh_key('git fetch --all') }}
    - cwd: {{ path }}
    - require:
      - cmd: {{ branch }}-clone

{{ branch }}-reset:
  {{ cmd_ssh_key('git reset --hard origin/' + branch + '; git checkout ' + branch) }}
    - cwd: {{ path }}
    - require:
      - cmd: {{ branch }}-fetch

{{ branch }}-virtualenv:
  virtualenv.managed:
    - name: {{ pillar.lunchbreak_path }}{{ branch }}
    - venv_bin: /usr/local/pyenv/shims/virtualenv
    - requirements: {{ path }}/requirements.txt
    - distribute: True
    - require:
      - cmd: {{ branch }}-reset
      - pkg: lunchbreak-dependencies

{{ branch }}-migration:
  cmd.run:
    - name: {{ pillar.lunchbreak_path }}{{ branch }}/bin/python {{ path }}/manage.py migrate --noinput
    - env:
      - LB_{{ branch }}_password: {{ secret_config.mysql.password }}
      - DJANGO_SETTINGS_BRANCH: {{ branch }}
    - require:
      - virtualenv: {{ branch }}-virtualenv

{{ branch }}-static:
  file.directory:
    - name: {{ path }}{{ pillar.static.relative_path }}
    - mode: 755
    - makedirs: True
    - require:
      - virtualenv: {{ branch }}-virtualenv
  cmd.run:
    - name: {{ pillar.lunchbreak_path }}{{ branch }}/bin/python {{ path }}/manage.py collectstatic --noinput -c
    - require:
      - file: {{ branch }}-static

{% endfor %}
