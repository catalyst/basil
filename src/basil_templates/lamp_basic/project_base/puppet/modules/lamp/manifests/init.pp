class lamp {

  exec { 'apt-get update':
    path => [ '/usr/bin' ],
  }
  package { 'apache2':
    ensure => 'installed',
    require => Exec['apt-get update'],
  }
  package { 'libapache2-mod-php5':
    ensure => 'installed',
    require => Exec['apt-get update'],
  }
  package { 'mysql-common':
    ensure => 'installed',
    require => Exec['apt-get update'],
  }
  package { 'mysql-client-5.5':
    ensure => 'installed',
    require => Exec['apt-get update'],
  }
  package { 'mysql-server':
    ensure => 'installed',
    require => Exec['apt-get update'],
  }
  package { 'mysql-server-5.5':
    ensure => 'installed',
    require => Exec['apt-get update'],
  }
  package { 'php5-common':
    ensure => 'installed',
    require => Exec['apt-get update'],
  }
  package { 'php5-mysql':
    ensure => 'installed',
    require => Exec['apt-get update'],
  }
  package { 'php5-curl':
    ensure => 'installed',
    require => Exec['apt-get update'],
  }
  package { 'php5-xdebug':
    ensure => 'installed',
    require => Exec['apt-get update'],
  }

  user { 'www-data':
    ensure => present,
    managehome => true,
  }

  file { '/usr/local/bin/sendmail':
    ensure => present,
    owner => 'root',
    group => 'root',
    mode => '555',
    source => 'puppet:///modules/lamp/usr/local/bin/sendmail',
  }

  file { '/etc/php5/apache2/php.ini':
    ensure => present,
    owner => 'root',
    group => 'root',
    mode => '444',
    source => 'puppet:///modules/lamp/etc/php5/apache2/php.ini',
    require => [ Package['apache2'], Package['libapache2-mod-php5'], Package['php5-common'] ],
  }

  file { '/etc/php5/apache2/conf.d/xdebug.ini':
    ensure => present,
    owner => 'root',
    group => 'root',
    mode => '444',
    source => 'puppet:///modules/lamp/etc/php5/apache2/conf.d/xdebug.ini',
    require => [ Package['apache2'], Package['libapache2-mod-php5'], Package['php5-common'], Package['php5-xdebug'] ],
  }

  exec { 'mod_rewrite':
    command => 'a2enmod rewrite',
    path => [ '/usr/bin', '/usr/sbin' ],
    require => Package['apache2'],
  }

  service { 'apache2':
    enable => true,
    ensure => 'running',
    require => [ Package['apache2'] ],
    subscribe => [ Exec['mod_rewrite'], File['/etc/php5/apache2/php.ini'] ],
  }

  service { 'mysql':
    enable => true,
    ensure => 'running',
    require => Package['mysql-server-5.5'],
  }

  exec { 'mysql_db':
    command => 'mysql -uroot -e "CREATE DATABASE IF NOT EXISTS {{__basil__.db_name}}"',
    path => [ '/usr/bin', '/bin' ],
    require => [ Service['mysql'], Package['mysql-client-5.5'] ],
  }
  exec { 'mysql_user':
    command => 'mysql -uroot -e "GRANT ALL PRIVILEGES ON {{__basil__.db_name}}.* TO \'{{__basil__.db_user}}\'@\'%\' IDENTIFIED BY \'{{__basil__.db_password}}\'"',
    path => [ '/usr/bin' ],
    require => [ Service['mysql'], Package['mysql-client-5.5'] ],
  }

}
