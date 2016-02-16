certificate_directory: /etc/lunchbreak/apns/
static:
  relative_path: /static/
  url: /static/

mysql.default_file: /etc/mysql/debian.cnf

project_path: /var/www/
git_repository: git@github.com:AndreasBackx/Lunchbreak-API.git
lunchbreak_path: /etc/lunchbreak/

branches:
  master:
    host: api.lunchbreakapp.be
    port: 8001
    ssl: True
    opbeat: True
    certificates:
      business: business_production.pem
      customers: customers_production.pem
  staging:
    host: staging.lunchbreakapp.be
    port: 8002
    ssl: True
    opbeat: False
    certificates:
      business: business_development.pem
      customers: customers_development.pem
  development:
    host: development.lunchbreakapp.be
    port: 8003
    ssl: False
    opbeat: False
    certificates:
      business: business_development.pem
      customers: customers_development.pem
