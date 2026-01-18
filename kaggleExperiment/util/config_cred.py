import os


mongo_host="vmogi01.deri.ie"
mongo_port=27017

#172.17.0.1
# 140.203.155.12
# 127.0.0.1

#iptables -A INPUT -s <172.17.0.1> -p tcp --destination-port 27017 -m state --state NEW,ESTABLISHED -j ACCEPT
# iptables -A OUTPUT -d 172.17.0.1 -p tcp --source-port 27017 -m state --state ESTABLISHED -j ACCEPT