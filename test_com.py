from datetime import datetime
from lathem import *

if __name__ == '__main__':
    import sys
    
    now = datetime.today()
    
    if 'write' in sys.argv:
        import serial
        p = serial.Serial(port='COM6')
        p.write(to_lathem_time_string(now))
        p.close()
    elif 'read' in sys.argv:
        import serial
        p = serial.Serial(port='COM6', timeout=30)
        try:
            while True:
                x = p.read(16)
                if x:
                    print repr(x), from_lathem_time_string(x)
        finally:
            p.close()
    else:
        print now, repr(to_lathem_time_string(now)), from_lathem_time_string(lathem_time_string(now))
    
	