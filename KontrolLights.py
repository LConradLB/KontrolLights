import pywinusb.hid as hid
import time
import math
import mido

def Connect():
    global komplete_device
    global reports
    global bufferC
    kompleteVID = 0x17cc
    kompletePID = 0x1360
    all_devices = hid.HidDeviceFilter(vendor_id = kompleteVID, product_id = kompletePID).get_devices()
    found = False
    if len(all_devices) == 0:
        print ("No komplete device found!")
        found = False
    else:
        print ("Komplete found :-)" )
        komplete_device = all_devices[0]
        komplete_device.open()
        found = True
     
        reports = komplete_device.find_output_reports()

        # Initialize else the light control does not seem to work
        bufferI = [0x00] * 249
        bufferI[0] = 0xa0

        reports[3].set_raw_data(bufferI)
        reports[3].send()

        # Set all keys to 0x00 - Black / no light
        bufferC = [0x00] * 249
        bufferC[2] = 0x82

        reports[2].set_raw_data(bufferC)
        reports[2].send()
   
    return found
            
def accept_notes(port, channel):
    """Only let note_on and note_off messages through."""
    for message in port:
        if message.type in ('note_on', 'note_off'):
            print(message)
            if message.channel == channel:
                yield message

def SetNote(note, status):
    bufferC[0] = 0x82
    offset = -36
    key = ((note + offset)*3) + 1
    if status == 'note_on':
        bufferC[key] = 0xff      # Set color to white (RGB)
        bufferC[key+1] = 0xff
        bufferC[key+2] = 0xff
    if status == 'note_off':
        bufferC[key] = 0x00      # Set color to black (RGB)
        bufferC[key+1] = 0x00
        bufferC[key+2] = 0x00
    reports[2].set_raw_data(bufferC)
    reports[2].send()
    
def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def net(number, key, buffer, bufferOffset):
    # print(number, key, buffer, bufferOffset)
    bufferC = buffer
    tempBuffer = number#bufferC[(key*3)+bufferOffset]
    if(number == 0):
                tempBuffer = bufferC[((key-2)*3)+bufferOffset]
    # print(tempBuffer)
    return clamp(tempBuffer, 6, 127)

def rainbowloopTwo():

    frequency  = float(0.01)
    delay = 0.01
    x = 200
    keycount = 61
    for k in range (0,keycount):
        for i in range (0,keycount): #This gets it to move
            curve = float(i/keycount) * math.pi #Revolve around the smooth curve of sine 0 -> 3.14
            red = 128 * math.sin(curve) #Change values 0 -> 1 to 0 -> 127
            blue = 128 * abs(math.sin(curve - math.pi/2))# abs to limit to postitive
            # green = 128 * abs(math.sin(curve - (math.pi/3 * 2)))

            sk = i+k
            if sk >= keycount: #Use all keys
                sk = sk-keycount

            bufferC[(sk*3)+1] = net(int(red), sk, bufferC, 1)
            # bufferC[(sk*3)+2] = net(int(green), sk, bufferC, 2)
            bufferC[(sk*3)+3] = net(int(blue), sk, bufferC, 3)
        reports[2].set_raw_data(bufferC)
        reports[2].send()
        time.sleep(delay)
        
if __name__ == '__main__':
    connected = Connect()
    if connected:
        while True:
            rainbowloopTwo()

        
        




        