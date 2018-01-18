__doc__ = """
    开启需要的服务，如redis, kafka等
"""

import subprocess

subprocess.Popen('C:\\env\\redis-x64-3.1.100\\redis-server.exe C:\\env\\redis-x64-3.1.100\\redis.windows.conf')
subprocess.Popen('C:\\env\\kafka_2.11-0.11.0.2\\bin\\windows\\zookeeper-server-start.bat '
                 'C:\\env\\kafka_2.11-0.11.0.2\\config\\zookeeper.properties')
subprocess.Popen('C:\\env\\kafka_2.11-0.11.0.2\\bin\\windows\\kafka-server-start.bat '
                 'C:\\env\\kafka_2.11-0.11.0.2\\config\\server.properties')
