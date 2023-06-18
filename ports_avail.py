import serial.tools.list_ports as port_list
ports = list(port_list.comports())
print(ports)
for p in ports:
    print (p)