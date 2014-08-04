class flask {

  package { 'python-pip':
    ensure => 'installed',
  }

  file { '/etc/init/runflask.conf':
    ensure => present,
    source => "puppet:///modules/flask/etc/init/runflask.conf",
    mode => "0555",
  }

  exec { 'sudo pip install -r requirements.txt':
    cwd => '/home/vagrant/src',
    require => Package['python-pip'],
    path => [ '/usr/bin' ],
  }

  exec { 'service runflask start':
    require => File['/etc/init/runflask.conf'],
    path => [ '/usr/bin', '/usr/sbin', '/sbin' ],
  }

}
