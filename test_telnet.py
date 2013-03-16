from datetime import datetime
from lathem import *
        
if __name__ == '__main__':
    import sys
    import telnetlib
    
    now = datetime.today()
    #now = once = datetime(2010, 11, 8, 16, 30, 0, 0)
    
    p = telnetlib.Telnet('192.168.1.101',100)
    p.write(to_lathem_time_string(now))
    p.close()
    print now, repr(to_lathem_time_string(now))


    
	
