/*
Basil: Build A System Instant-Like
Copyright (C) 2014 Catalyst IT Ltd

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

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
    timeout => 0,
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
