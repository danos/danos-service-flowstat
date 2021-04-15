# DANOS Dataplane flowstat plugin

This repository includes the operational templates, configuration scripts and yang for flowstat plugin.

# How to configure
First, create a firewall with DPI enabled as [link](https://danosproject.atlassian.net/wiki/spaces/DAN/pages/544243713/Deep+Packet+Inspection#4.1.-An-application-firewall-allows-access-to-permitted-websites-while-blocking-all-other-web-traffic)

Enable flow stat on interface
```sh
set interfaces dataplane dp0p33p1 flow-stat enable
```

Make a http request
```sh
curl http://google.com
```

Check for log was exported
```sh
journalctl -u vyatta-dataplane -b -f |grep FLOWSTAT
```
You should see something like
```sh
Apr 07 13:14:27 node dataplane[3228]: FLOWSTAT: Flushed 1 logs
```

Show top 10 app by total bytes in last 5 minutes
```sh
root@node:~# show dataplane flow-stat dp0p33p1 5m top app bytes 
{"items": [{"key": "Google", "in_bytes": 1017, "out_bytes": 544, "bytes": 1561}]}
```

Show timeseries bytes of Google app in last 5 minutes
```sh
root@node:~# show dataplane flow-stat dp0p33p1 5m timeseries app Google
{"items": [{"timestamp": 1617801560, "in_bytes": 1017, "out_bytes": 544, "bytes": 1561}]}
```

Disable flowstat on all interfaces
```sh
set service flowstat disable
```
