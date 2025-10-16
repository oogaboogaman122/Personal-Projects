### A programmable 4x4x4 LED cube that also responds to motion via ultrasonic sensors.

## Parts:
64 Yellow LED pieces (~2.2 V) <br>
1 Darlington Array <br>
2 octal latches <br>
250 Ohm Resistors <br>
Arduino Nano

## Design and Logic:
Uses multiplexing to drive 64 leds. Led works layer by layer, so technically only about 16 leds are active. each layer has a common cathode thus connecting all the leds at once. you drive each led by the layer its on and the column its on. 
## Challenges Faced:
Dont have a shift register. Had to improvise by using 2 octal latches and daisy chaining them to drive 16 leds. Was worried about too much current going back into my 
mcu, so I used darlington arrays to sink current. 




## Prototype proof:
(Motion Activated)
https://github.com/user-attachments/assets/4cf554fa-84f7-4b95-b790-a4dea2f1b42d <br>
(Programmed)
https://github.com/user-attachments/assets/80ba579c-8529-408b-b6a3-5153667e5b73<br>


