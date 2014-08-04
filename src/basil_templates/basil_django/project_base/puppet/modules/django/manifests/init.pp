class django {

  package { 'python-pip':
    ensure => 'installed',
  }

  file { '/home/vagrant/src/requirements.txt':
    ensure => present,
    source => "puppet:///modules/django/home/vagrant/src/requirements.txt",
  }

  file { '/etc/init/runserver.conf':
    ensure => present,
    source => "puppet:///modules/django/etc/init/runserver.conf",
    mode => "0555",
  }

  exec { 'sudo pip install -r requirements.txt':
    cwd => '/home/vagrant/src',
    require => [
      Package['python-pip'],
      File['/home/vagrant/src/requirements.txt'],
    ],
    path => [ '/usr/bin' ],
  }

  exec { 'django-admin.py startproject {{__basil__.project_name}}':
    cwd => '/home/vagrant/src',
    creates => '/home/vagrant/src/{{__basil__.project_name}}',
    require => Exec['sudo pip install -r requirements.txt'],
    path => [ '/usr/local/bin' ],
  }

  exec { 'service runserver start':
    cwd => '/home/vagrant/src/{{__basil__.project_name}}',
    require => [
      Exec['django-admin.py startproject {{__basil__.project_name}}'],
      File['/etc/init/runserver.conf'],
    ],
    path => [ '/usr/bin', '/usr/sbin', '/sbin' ],
  }

}
