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

{% macro lunchbreak_app(id, config) -%}

{% if config.branch is defined and config.branch %}
  {% set branch = config.branch %}
{% else %}
  {% set branch = id %}
{% endif %}

{% set local = config.path is defined and config.path %}
{% set path = pillar.project_path + id %}
{% set secret_config = pillar.secret_branches[branch] %}

{% if local %}
{{ id }}-local:
  file.symlink:
    - name: {{ path }}
    - target: {{ config.path }}
    - makedirs: True

{% else %}
{{ id }}-clone:
  {{ cmd_ssh_key('git clone ' + pillar.git_repository + ' ' + path) }}
    - unless:
      - ls {{ path }}
    - require:
      - ssh_known_hosts: github.com

{{ id }}-fetch:
  {{ cmd_ssh_key('git fetch --all') }}
    - cwd: {{ path }}
    - require:
      - cmd: {{ id }}-clone

{{ id }}-reset:
  {{ cmd_ssh_key('git reset --hard origin/' + branch + '; git checkout ' + branch) }}
    - cwd: {{ path }}
    - require:
      - cmd: {{ id }}-fetch
{% endif %}

{{ id }}-virtualenv:
  virtualenv.managed:
    - name: {{ pillar.lunchbreak_path }}{{ id }}
    - venv_bin: /usr/local/pyenv/shims/virtualenv
    - requirements: {{ path }}/{{ config.get('requirements', 'requirements.txt') }}
    - distribute: True
    - require:
      {% if local %}
      - file: {{ id }}-local
      {% else %}
      - cmd: {{ id }}-reset
      {% endif %}
      - pkg: lunchbreak-dependencies

{{ id }}-migration:
  cmd.run:
    - name: {{ pillar.lunchbreak_path }}{{ id }}/bin/python {{ path }}/manage.py migrate --noinput
    - env:
      - LB_{{ branch }}_password: {{ secret_config.mysql.password }}
      - DJANGO_SETTINGS_BRANCH: {{ branch }}
    - require:
      - virtualenv: {{ id }}-virtualenv

{{ id }}-static:
  file.directory:
    - name: {{ path }}{{ pillar.static.relative_path }}
    - mode: 755
    - makedirs: True
    - require:
      - virtualenv: {{ id }}-virtualenv
  cmd.run:
    - name: {{ pillar.lunchbreak_path }}{{ id }}/bin/python {{ path }}/manage.py collectstatic --noinput -c
    - require:
      - file: {{ id }}-static

{%- endmacro %}

{% for branch, config in pillar.get('branches', {}).items() %}
{{ lunchbreak_app(branch, config) }}
{% endfor %}

{% if pillar.local is defined and pillar.local %}
{{ lunchbreak_app('local', pillar.local) }}
{% endif %}
