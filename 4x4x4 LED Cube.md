### A programmable 4x4x4 LED cube that also responds to motion via ultrasonic sensors.

## Summary
A 4×4×4 LED cube built from scratch using discrete logic — two 74HC373 latches to drive the 16 columns and a ULN2803A Darlington array to handle layer sinking. The cube runs multiplexed LED animations and reacts to motion detected through an ultrasonic sensor. Its entire operation is managed by an Arduino Nano.

The design intentionally separates logic control and high-current drive to protect the MCU and ensure reliable brightness across all 64 LEDs. Despite limited parts, the setup achieves smooth scanning and dynamic visual effects.

---

## Parts:
- **64 × Yellow LEDs** (~2.2 V forward voltage)  
- **2 × 74HC373 Octal Latches** (column control)  
- **1 × ULN2803A Darlington Array** (layer sinking)  
- **Resistors (~250 Ohms)** per column  
- **Arduino Uno** (ATmega328P)  
- **HC-SR04 Ultrasonic Sensor**  
- **5 V Power Supply** (shared logic + LED drive)

---

## Design and Logic:
The cube operates on a **time-multiplexed display system**, where only one of the four LED layers (each a common cathode plane) is active at a time. The Arduino rapidly cycles through layers to create persistence of vision — making all 64 LEDs appear active simultaneously.

Each layer is connected through the **ULN2803A Darlington array**, which safely sinks the combined current of up to 16 LEDs. The **74HC373 latches** handle the 16 column lines; they store LED states for each layer until refreshed by the microcontroller.

Resistors were included in the circuit to limit the current flowing through each LED and protect both the LEDs and the driver circuitry from excessive current draw. Without them, the LEDs would pull as much current as the circuit allows, quickly overheating or burning out. The value of 250 Ω was chosen because it provides about 11–12 mA of peak current per LED from a 5 V source with a 2.1 V LED drop, which maintains strong brightness while staying within safe electrical limits. Since the cube is multiplexed, each LED is only on 25 % of the time, keeping the average current near 3 mA and preventing overheating. The resistors were placed near the microcontroller output (on the column lines) to ensure current is limited right at the signal source, reducing voltage noise, protecting the logic pins, and keeping the wiring that runs to the LEDs at a safe and stable current level.

This approach avoids the need for shift registers or expensive LED drivers. By writing 16 bits of data (8 per latch) and toggling the latch enable lines, the cube updates all columns instantly without flicker.

When motion is detected via the **ultrasonic sensor**, distance values influence animation selection and timing — for example, closer movement might trigger brighter or faster sequences.

---

## Code
```cpp
#include <Arduino.h>

const uint8_t COL_DATA_PINS[8] = {2,3,4,5,6,7,8,9};
const uint8_t COL_LE_A = 10;
const uint8_t COL_LE_B = 11;
const uint8_t LAYER_PINS[4] = {A0, A1, A2, A3};
const uint8_t US_TRIG = A4;
const uint8_t US_ECHO = A5;

const uint16_t LAYER_HOLD_US = 2000;
volatile uint16_t frame[4];
volatile uint8_t currentLayer = 0;

inline void setBus8(uint8_t value){
  for(uint8_t i=0;i<8;i++) digitalWrite(COL_DATA_PINS[i], (value>>i)&1);
}
inline void latch(uint8_t le){ digitalWrite(le,LOW); digitalWrite(le,HIGH); }

void writeCols(uint16_t mask){
  setBus8(mask & 0xFF); latch(COL_LE_A);
  setBus8((mask>>8)&0xFF); latch(COL_LE_B);
}

void enableLayer(uint8_t k){
  for(uint8_t i=0;i<4;i++) digitalWrite(LAYER_PINS[i], HIGH);
  digitalWrite(LAYER_PINS[k], LOW);
}

uint16_t readDist(){
  digitalWrite(US_TRIG,LOW); delayMicroseconds(2);
  digitalWrite(US_TRIG,HIGH); delayMicroseconds(10);
  digitalWrite(US_TRIG,LOW);
  unsigned long d=pulseIn(US_ECHO,HIGH,30000UL);
  return (uint16_t)(d/5.8);
}

void setup(){
  for(auto p:COL_DATA_PINS) pinMode(p,OUTPUT);
  pinMode(COL_LE_A,OUTPUT); pinMode(COL_LE_B,OUTPUT);
  for(auto p:LAYER_PINS) pinMode(p,OUTPUT);
  pinMode(US_TRIG,OUTPUT); pinMode(US_ECHO,INPUT);
  frame[0]=0b1111000000000000;
  frame[1]=0b0000111100000000;
  frame[2]=0b0000000011110000;
  frame[3]=0b0000000000001111;
}

void loop(){
  writeCols(frame[currentLayer]);
  enableLayer(currentLayer);
  delayMicroseconds(LAYER_HOLD_US);
  currentLayer=(currentLayer+1)&3;

  static uint32_t last=0;
  if(millis()-last>80){
    uint16_t d=readDist();
    if(d<200) frame[0]=0xFFFF;
    else if(d<400) frame[1]=0x0F0F;
    else if(d<700) frame[2]=0x00FF;
    else frame[3]=0x000F;
    last=millis();
  }
}
```
---

## Challenges Faced + Solutions:
**No shift registers available**
Solved by using two 74HC373 latches to hold the column data. The latch method allowed atomic updates with minimal flicker. 


**Excess current concerns**
Solved by routing all high-current paths through the ULN2803A array, isolating the Arduino’s I/O pins from LED drive currents. 


**Twitchy ultrasonic readings**
Implemented delay filtering and distance band mapping to stabilize responses. Future versions could use median filtering. 


**Wiring complexity**
Managed by keeping all column lines aligned in parallel with shared data bus lines.


---

## Design Improvements:
- Replace 74HC373 + ULN2803A with a dedicated LED driver like **TLC5940** or **MAX7219** for current control and easier scaling.  
- Implement PWM fading per layer for smoother animation transitions.  
- Add capacitive or sound-reactive input to diversify motion triggers.  
- Use a PCB backplane for neater wiring and consistent ground routing.  
- Introduce serial pattern loading via UART for dynamic animation updates.

---

## Proof:
**(Motion Activated)**  


https://github.com/user-attachments/assets/4cf554fa-84f7-4b95-b790-a4dea2f1b42d 


**(Programmed)**  


https://github.com/user-attachments/assets/80ba579c-8529-408b-b6a3-5153667e5b73 



