certificate_directory: /etc/lunchbreak/apns/
static:
  relative_path: /static/
  url: /static/

mysql.default_file: /etc/mysql/debian.cnf
innodb_buffer_pool_size: 350M

project_path: /var/www/
git_repository: git@github.com:AndreasBackx/Lunchbreak-API.git
virtualenv_path: /etc/lunchbreak/

branches:
  master:
    host: api.lunchbreakapp.be
    ssl: True
    certificates:
      business: business_production.pem
      customers: customers_production.pem
  staging:
    host: staging.lunchbreakapp.be
    ssl: True
    certificates:
      business: business_development.pem
      customers: customers_development.pem
  development:
    host: development.lunchbreakapp.be
    ssl: False
    certificates:
      business: business_development.pem
      customers: customers_development.pem
    requirements: dev-requirements.txt
