class nodejs {


  exec { 'update':
    command => 'apt-get update',
    path => [ '/usr/bin' ],
  }

  package { 'curl':
    ensure => present,
    require => Exec['update'],
  }

  exec { 'nodesource':
    command => 'curl -sL https://deb.nodesource.com/setup | sudo bash -',
    creates => '/etc/apt/sources.list.d/nodesource.list',
    path    => [ '/usr/bin', '/bin' ],
    require => Package['curl']
  }

  package { 'nodejs':
    ensure => 'installed',
    require => Exec['nodesource'],
  }

  exec { 'forever':
    command => 'npm install forever -g',
    creates => '/usr/bin/forever',
    path    => [ '/usr/bin'],
    require => Package['nodejs']
  }

  package { 'build-essential':
    ensure => 'installed',
  }

  file { '/etc/init/nodeapp.conf':
    ensure => present,
    source => "puppet:///modules/nodejs/etc/init/nodeapp.conf",
    mode => "0555",
  }

  exec { 'service nodeapp restart':
    require => [
      File['/etc/init/nodeapp.conf'],
      Exec['forever'],
    ],
    path => [ '/usr/bin', '/usr/sbin', '/sbin' ],
  }

}
