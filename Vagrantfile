# -*- mode: ruby; -*-
require 'etc'

Vagrant.configure('2') do |config|
  config.vm.define :web do |web|
    web.vm.box = 'ubuntu/trusty64'

    #web.vm.hostname = 'lunchbreak.dev'
    web.vm.network :forwarded_port, guest: 80, host: 8080, auto_correct: true
    web.vm.network :forwarded_port, guest: 443, host: 4430, auto_correct: true

    web.vm.synced_folder 'salt/synced/', '/srv/'

    #config.vm.provision "shell", path: "salt/extra-provision.sh"

    web.vm.provision :salt do |salt|
      salt.bootstrap_options = '-F -c /tmp/ -P'
      salt.minion_config = 'salt/minion'
      salt.run_highstate = true
      salt.verbose = true
      salt.log_level = 'warning'
      salt.colorize = true

      # salt.minion_key = 'salt/vagrant-keys/vagrant.pem'
      # salt.minion_pub = 'salt/vagrant-keys/vagrant.pub'

      # salt.install_type = 'daily'
    end

    web.vm.provider :virtualbox do |v|
      v.customize ['modifyvm', :id, '--memory', 512]
    end
  end
end
