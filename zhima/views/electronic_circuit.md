Raspi Hat
=========

On the 40 pins GPIO, only outside pins from 4 (2nd +5V) till 18 (GPIO24) are used.

    -------
  1 | x x | 2   
  3 | x o | 4  : +5V      --> +5V
  5 | x o | 6  : Ground   --> GND
  7 | x o | 8  : GPIO 14  --> Green 1 LED  --> Resistance --> GND
  9 | x o | 10 : GPIO 15  --> Green 2 LED  --> Resistance --> GND
 11 | x o | 12 : GPIO 18  --> Red LED --> Resistance --> GND
 13 | x o | 14 : Ground   --> GND
 14 | x o | 16 : GPIO 23  --> Proximity
 15 | x o | 18 : GPIO 24  --> Relay
 17 | x x | 20 
 
 Relay
 =====
 
 
   2 +5V       1
   | |         |
 +---------------+
 | o o         o |
 | |  Top view   |
 | o o         o |
 +---------------+
   | |         |
   3 |         1
     |
     +-------------->  Collector
GPIO -> resistance ->  Base
GND  --------------->  Emitter

When relay ON:      1 --> 2
When relay is OFF:  1 --> 3
