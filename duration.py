#!/usr/bin/python3
# -*- coding:UTF-8 -*-

import docker
import os
import time

try:
    #connect = docker.Client(base_url='unix:///var/run/docker.sock',version='auto',timeout=120)
    connect = docker.from_env()
    res = connect.version()
except:
    exit()

def Duration(id, br, addr, gw):
    try:
        container = connect.containers.get(container_id=id)
        pid = str(container.attrs['State']['Pid'])
    except:
        pid = 0

    if int(pid) != 0:
        if not os.path.exists('/var/run/netns'):
            os.makedirs('/var/run/netns')
        source_namespace = '/proc/'+pid+'/ns/net'
        destination_namespace = '/var/run/netns/'+pid

        if not os.path.exists(destination_namespace):
            link = 'ln -s %s %s' % (source_namespace,destination_namespace)
            os.system(link)
            os.system('ip link add tap%s type veth peer name veth%s 2>> /var/log/docker-static-ip.log' % (pid,pid) )
            os.system('brctl addif %s tap%s 2>> /var/log/docker-static-ip.log' % (br,pid) )
            os.system('ip link set tap%s up 2>> /var/log/docker-static-ip.log' % pid )
            os.system('ip link set veth%s netns %s 2>> /var/log/docker-static-ip.log' % (pid,pid) )
            os.system('ip netns exec %s ip link set dev veth%s name eth1 2>> /var/log/docker-static-ip.log' % (pid,pid) )
            os.system('ip netns exec %s ip link set eth1 up 2>> /var/log/docker-static-ip.log' % pid)
            os.system('ip netns exec %s ip addr add %s dev eth1 2>> /var/log/docker-static-ip.log' % (pid,addr) )
            os.system('ip netns exec %s ip route add default via %s 2>> /var/log/docker-static-ip.log' % (pid,gw) )

# 成产使用
syspid = os.fork()

if syspid == 0:
    while True:
        file = open('./containers.cfg')
        if file:
            for i in file:
                i = i.strip('\n')
                cfg = i.split(',') 
                Duration(*cfg)
        file.close()
        time.sleep(10)
else:
    exit()

# 调试使用
# if __name__ == '__main__':
#     file = open('./containers.cfg')
#     if file:
#         for i in file:
#             i = i.strip('\n')
#             cfg = i.split(',') 
#             Duration(*cfg)
#     file.close()