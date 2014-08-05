class django {

  package { 'python-pip':
    ensure => 'installed',
  }

  file { '/etc/init/runserver.conf':
    ensure => present,
    source => 'puppet:///modules/django/etc/init/runserver.conf',
    mode => '0555',
  }

  exec { 'sudo pip install -r requirements.txt':
    cwd => '/home/vagrant/src',
    timeout => 0,
    require => Package['python-pip'],
    path => [ '/usr/bin' ],
  }

  file { '/home/vagrant/django_project_template':
    source => 'puppet:///modules/django/home/vagrant/django_project_template',
    recurse => true,
  }

  exec { 'startproject':
    command => 'django-admin.py startproject {{__basil__.project_name}} --template="/home/vagrant/django_project_template"',
    cwd => '/home/vagrant/src',
    creates => '/home/vagrant/src/{{__basil__.project_name}}',
    require => [
      Exec['sudo pip install -r requirements.txt'],
      File['/home/vagrant/django_project_template'],
    ],
    path => [ '/usr/local/bin' ],
  }

  exec { 'service runserver start':
    cwd => '/home/vagrant/src/{{__basil__.project_name}}',
    require => [
      Exec['startproject'],
      File['/etc/init/runserver.conf'],
    ],
    path => [ '/usr/bin', '/usr/sbin', '/sbin' ],
  }

}
