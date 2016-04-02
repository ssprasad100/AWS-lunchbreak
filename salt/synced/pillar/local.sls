innodb_buffer_pool_size: 100M

branches:
  development:
    path: /vagrant
    host: lunchbreak.dev
    ssl: False
    certificates:
      business: business_development.pem
      customers: customers_development.pem
    branch: development
    requirements: requirements-dev.txt
