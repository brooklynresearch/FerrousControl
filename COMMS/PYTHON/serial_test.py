import serial
import time
import array
from random import randint

PACKET_LEN = 320

def main():
  s = serial.Serial('/dev/tty.usbmodem5803660', 1000000)

  count = 0
  while True:
    start = time.time()
    nums = []
    count += 1
    for i in range(PACKET_LEN):
      nums.append(randint(0, 200))

    nums[-1] = count % 255

    print("SENDING " + str(nums))

    s.write(array.array('B', nums))

    checksum = sum(nums) % 65535

    print("\n\nChecksum: " + str(checksum))

    recv = s.read(1)
    while recv != b'$':
      recv = s.read(1)

    #time.sleep(0.1)
    dt = (time.time() - start) * 1000
    print("\n\nTime: " + str(dt))


if __name__ == '__main__':
  main()
