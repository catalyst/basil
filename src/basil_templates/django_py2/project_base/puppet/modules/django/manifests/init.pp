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

  exec { 'django_startproject':
    command => 'django-admin.py startproject {{__basil__.project_name}} --template="/home/vagrant/django_project_template"',
    cwd => '/home/vagrant/src',
    creates => '/home/vagrant/src/{{__basil__.project_name}}',
    require => [
      Exec['sudo pip install -r requirements.txt'],
      File['/home/vagrant/django_project_template'],
    ],
    path => [ '/usr/local/bin' ],
  }

  exec { 'django_syncdb':
    command => 'python manage.py syncdb --noinput',
    cwd => '/home/vagrant/src/{{__basil__.project_name}}',
    require => Exec['django_startproject'],
    path => [ '/usr/bin', '/usr/local/bin' ],
  }

  exec { 'django_createsuperuser':
    command => 'echo "from django.contrib.auth.models import User; User.objects.create_superuser(\'{{__basil__.admin_username}}\', \'{{__basil__.admin_email}}\', \'{{__basil__.admin_password}}\')" | python manage.py shell',
    cwd => '/home/vagrant/src/{{__basil__.project_name}}',
    require => Exec['django_syncdb'],
    path => [ '/bin', '/usr/bin', '/usr/local/bin' ],
  }

  exec { 'service runserver restart':
    cwd => '/home/vagrant/src/{{__basil__.project_name}}',
    require => [
      Exec['django_createsuperuser'],
      File['/etc/init/runserver.conf'],
    ],
    path => [ '/usr/bin', '/usr/sbin', '/sbin' ],
  }

}
