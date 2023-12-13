#!/usr/bin/python3
# -*- coding:UTF-8 -*-

import docker
import os
import time
import re


try:
    #connect = docker.Client(base_url='unix:///var/run/docker.sock',version='auto',timeout=120)
    connect = docker.from_env()
    res = connect.version()
except:
    exit()

def getip(str):
    result = re.findall(r'\D(?:\d{1,3}\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\D', str)
    ret_start = re.match(r'(\d{1,3}\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\D', str)
    if ret_start:
        result.append(ret_start.group())
    ret_end = re.search(r'\D(\d{1,3}\.){3}(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$', str)
    if ret_end:
        result.append(ret_end.group())
    ip_list = []
    for r in result:
        ret = re.search(r'((25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)', r)
        if ret:
            ip_list.append(ret.group())
    return ip_list

containers = connect.containers.list()

for container in containers:
    container_name = container.name
    container_ip = ""

    try:
        # res = container.exec_run("bash -c 'ip a | grep inet | grep -v 127.0.0.1 | grep -v 172 | grep -v inet6 | awk '{print $2}' | tr -d \"addr:\"'")
        res = container.exec_run("bash -c 'ip a | grep inet | grep -v 127.0.0.1 | grep -v 172 | grep -v inet6  '")
        if res.exit_code == 0:
            ips = getip(str(res.output, encoding='utf-8'))
            # print(ips)
            container_ip = ips[0]
    except:
        container_ip = ""

    if container_ip != "":
        # print("{},br0,{}/22,10.100.0.1".format(container_name,container_ip))
        str = "{},br0,{}/22,10.100.0.1\n".format(container_name,container_ip)
        with open('./containers.cfg', 'a+') as file:
            file.seek(0)
            lines = file.readlines()
            if str in lines:
                pass
            else:
                file.write(str)