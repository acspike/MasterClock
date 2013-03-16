from datetime import datetime
from lathem import *

if __name__ == '__main__':
    now = datetime.today()
    once = datetime(2010, 11, 8, 8, 25, 55, 0)
    print repr(to_lathem_time_string(once)), once, from_lathem_time_string(to_lathem_time_string(once))
    print repr(to_lathem_time_string(now)), now, from_lathem_time_string(to_lathem_time_string(now))
    
    if False:
        import serial
        p = serial.Serial(port='COM6')
        p.write(to_lathem_time_string(once))
        p.close()
    
