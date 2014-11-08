from __future__ import with_statement
from fabric.api import *
#from fabric.operations import *

def read_hosts():
    import sys
    env.hosts = [ h.strip() for h in sys.stdin.readlines() if h.strip() and not h.strip().startswith(('#','/')) ]

def get_hash(user=env.user):
    with hide('everything'):
        print(sudo('grep {user} /etc/shadow | cut -d\':\' -f 2'.format(**locals())))

def up():
    with settings(hide('everything'), warn_only=True):
        run('uptime')

@parallel
def uptime():
        run('uptime')

@parallel
def reboot_servers():
    reboot()

def dns_fix():
    run('cat /etc/resolv.conf')
    sudo("sed -ibup 's/128.228.170.10/172.16.18.10/' /etc/resolv.conf")

def restart_puppet():
    sudo('service puppet restart')
    #sudo('service puppet restart && tail -f /var/log/messages | { sed "/Finished catalog/ q" && kill $$ ;} | grep puppet-agent')

def clean_puppet():
    dns_domain = local('hostname -d', capture=True).strip()
    fqdn = '.' in env.host and env.host or '{host}.{dns_domain}'.format(host=env.host, dns_domain=dns_domain)
    sudo('rpm --import http://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL')
    sudo('rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm || true')
    sudo('yum install -y -q puppet')
    local('sudo puppet cert clean {fqdn} || true'.format(**locals()))
    sudo('/usr/sbin/ntpd -q -g')
    sudo('/sbin/service puppet stop')
    sudo('rm -rf /var/lib/puppet/ssl')
    sudo('puppet agent -t --report --pluginsync || true')
    local('sudo puppet cert --sign {fqdn} --allow-dns-alt-names'.format(**locals()))
    sudo('/sbin/service puppet start')

def clean_rhn():
    sudo('rpm --import http://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL')
    sudo('rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm')
    sudo('yum install -y puppet')
    sudo('sudo /usr/sbin/rhnreg_ks  --serverUrl https://rhn1.cuny.edu/XMLRPC --activationkey 1-6008306d2fedb6b8010178b6fe89cb2d --force')


def yum_update():
    pass