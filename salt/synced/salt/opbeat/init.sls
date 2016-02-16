opbeat-release:
  cmd.run:
    - name: |
      curl https://opbeat.com/api/v1/organizations/308fe549a8c042429061395a87bb662a/apps/a475a69ed8/releases/ \
            -H "Authorization: Bearer {{ pillar.opbeat_token }}" \
            -d rev=`git log -n 1 --pretty=format:%H` \
            -d branch=`git rev-parse --abbrev-ref HEAD` \
            -d status=completed
