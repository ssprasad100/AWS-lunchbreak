Lunchbreak-API
==============

De Lunchbreak API geschreven in Python Django.

[![Build status](https://magnum.travis-ci.com/AndreasBackx/Lunchbreak-API.svg?token=gsVV9n7i3zDy19arRrp7&branch=development)](https://magnum.travis-ci.com/AndreasBackx/Lunchbreak-API "Ga naar de Travis pagina.")

Lunchbreak kan gemakkelijk door middel van Vagrant opgestart worden op eender welk systeem en is beschikbaar op poort 8080 voor http en 4430 voor https. Om dit mogelijk te maken moet er eerst een pillar toegevoegd worden in `salt/synced/pillar/secret.sls`. Een template van dit bestand is hieronder te vinden, alle waarden moeten ingevuld worden. Daarnaast moet de map _keys_ toegevoegd worden aan `salt/synced/salt` met de volgende bestanden:

* keys/apns/business\_development.pem, keys/apns/customers\_development.pem
  * Development APNS certificaten. Indien er geen beschikbaar zijn, worden er geen push notifications verstuurd.
* keys/ssh/id_rsa
  * Private SSH key waarvan de public key toegevoegd moet worden aan de repository.

Indien SSL/TLS ingeschakeld staat moeten volgende bestanden ook aanwezig zijn:

* keys/tls/dhparam.pem
* keys/tls/lunchbreak.pem
* keys/tls/lunchbreak.key

`salt/synced/pillar/secret.sls` template:
```yaml
google_cloud_secret: INVULLEN
opbeat:
  organization_id: INVULLEN
  app_id: INVULLEN
  secret_token: INVULLEN
sendgrid:
  user: INVULLEN
  password: INVULLEN

mysql_root_password: INVULLEN
secret_branches:
  development:
    mysql:
      user: INVULLEN
      password: INVULLEN
      database: INVULLEN
```
