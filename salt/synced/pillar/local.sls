innodb_buffer_pool_size: 100M

local:
  path: /vagrant/lunchbreak
  host: local.lunchbreakapp.be
  ssl: False
  opbeat: False
  certificates:
    business: business_development.pem
    customers: customers_development.pem
  branch: development
  requirements: dev-requirements.txt
