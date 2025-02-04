import serial
ser = serial.Serial("/dev/ttyUSB0", 4800)



def main():
   while True:
      cc = str(ser.readline())
      line = cc[2:][:-5]
      if not line.startswith('$GPGSV'):
         continue
      f = line.split(',')

      # 1    = Total number of messages of this type in this cycle
      # 2    = Message number
      # 3    = Total number of SVs in view
      # 4    = SV PRN number
      # 5    = Elevation in degrees, 90 maximum
      # 6    = Azimuth, degrees from true north, 000 to 359
      # 7    = SNR, 00-99 dB (null when not tracking)
      # 8-11 = Information about second SV, same as field 4-7
      # 12-15= Information about third SV, same as field 4-7
      # 16-19= Information about fourth SV, same as field 4-7

      # print(line)
      for i in range(4, 17, 4):
         try:
            s_id = f[i]
            s_snr = f[i + 3]
            if s_snr and '*' not in s_snr:
               print(f'sat id = {s_id}, snr = {s_snr}')
         except:
            pass



if __name__ == '__main__':
   main()
