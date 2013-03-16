#
# lathem.py
# Copyright (c) 2010-2013 Aaron C Spike
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 

#DATA: 0#112233456677Z,CR (16 chars)
#'0' is address byte
#'#' is command code for Routine Time Update
#where '11' is hex MS,LS of Seconds of Minute (1-59)
#where '22' is hex MS,LS of Minutes of Hr (0-59)
#where '33' is hex MS,LS of Hour of Day (0-23)
#where '4' is hex Day of Week (Sun - 0 etc.)
#where '5' is hex Month of Year (1-12)
#where '66' is hex MS,LS of Day of Month (1-31)
#where '77' is hex MS,LS of Year offset form 1984 (0-127)
#where 'Z' is the 1's complement of the mod-64 sum of all 
#characters in the string except the CR and the checksum

from datetime import datetime

def lathem_checksum(s):
    sum = 0
    for x in s:
        sum += ord(x)
    return chr((sum & 63) ^ 255)

def to_lathem_time_string(dt):
    #In python week begins on Monday=0
    #Lathem expects Sunday=0
    weekday = (dt.weekday() + 1) % 7
    #Lathem base year is 1984
    year = dt.year - 1984
    
    format = '0#%0.2X%0.2X%0.2X%0.1X%0.1X%0.2X%0.2X'
    buffer = format % (dt.second, dt.minute, dt.hour, weekday, dt.month, dt.day, year)
    return buffer+lathem_checksum(buffer)+'\x0d'

def from_lathem_time_string(s):
    second = int(s[2:4],16)
    minute = int(s[4:6],16)
    hour = int(s[6:8],16)
    month = int(s[9],16)
    day = int(s[10:12],16)
    year = 1984 + int(s[12:14],16)
    return datetime(year, month, day, hour, minute, second, 0)
       
