### Quirky little device that displays custom messages on an LCD, paired with LED lighting sequences and buzzer tones.

---

## Summary
A compact Arduino Uno-based device designed to display personalized text messages on a 16×2 LCD, synchronized with coordinated LED lighting and buzzer tones.  
The goal was to create something expressive, a small emotional circuit that reacts through light and sound.  

This was built entirely on a breadboard with direct pin wiring to a standard parallel LCD

---

## Parts:
- **Arduino Uno**  
- **1602 LCD Display (parallel 16-pin version)**  
- **Passive Buzzer**  
- **Green LED**  
- **Red and Blue LEDs**  
- **Push Buttons)**  
- **10 kΩ Resistor** (button pull-down / input protection)  
- **Current-limiting resistors** (~220–330 Ω for LEDs)  
- **Jumper wires + Breadboard**  
- **Laptop USB (5 V) as power source**

---

## Design and Logic:
Pressing the button triggers a short sequence: the LCD displays a message while LEDs and buzzer tones activate in sync.  
The **green LED** acts as the final cue — the emotional highlight — while the **red and blue LEDs** alternate to add motion and rhythm.  
The **passive buzzer** plays short tones that match each LED flash.  

All control was handled by the **Arduino Uno**, which directly drove the LCD in **4-bit parallel mode**, using six control/data pins (RS, EN, D4–D7) along with power and contrast pins.  
This setup used nearly all available digital I/O on the Uno — a tight but workable configuration for a small single-board device.  

The breadboard prototype was powered directly through the laptop’s 5 V USB supply, which provided stable power for both the LEDs and the LCD.

---

## Electrical Justification:
Resistors were placed in series with the LEDs to limit current and protect both the LEDs and the Uno’s pins.  
Each LED drops roughly 2.1 V, leaving about 2.9 V across the resistor at 5 V input, producing around 11–12 mA of current — bright enough for visual clarity while staying safe for the MCU.  
A **10 kΩ pull-down resistor** was connected to the push button to stabilize the input and prevent random triggers caused by floating voltage.  

The LCD’s contrast was adjusted using a small **10 kΩ potentiometer** connected to the VO pin, ensuring text visibility without overdriving the display.  
The passive buzzer was driven directly from a digital output pin, with short tone durations to prevent excessive current draw.

---

## Challenges + Solutions:
- **Tone freezing LEDs:** Using `delay()` for buzzer timing blocked LED updates. Adjusted tone durations and sequencing to keep transitions smooth.  
- **Uneven brightness:** The LEDs dimmed slightly when the buzzer played. This was mitigated by powering the Uno directly from the laptop’s USB 5 V source.  
- **Pin management:** The LCD in parallel mode used many pins, leaving limited I/O for other functions. Solved by reusing analog pins as digital outputs where possible.  
- **LCD flicker:** Repeated writes caused flickering; fixed by only updating the text when necessary.  

---

## Design Improvements:
- Implement proper **button debouncing** (hardware RC or software-based) to avoid multiple triggers per press.  
- Build a **housing or enclosure** to protect the wiring and make it more presentable.  
- Replace the **passive buzzer** with a **small speaker** for richer and cleaner audio output.  
- Upgrade to an **OLED display** or **I²C LCD** to free up pins and simplify wiring.  
- Store multiple messages and tone sequences in EEPROM for replay options.  
- Add motion or touch sensors for automatic activation instead of relying on a button.  

---

## Code:
```cpp
#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 11, 10, 9, 8, 7); // RS, EN, D4, D5, D6, D7

const int buzzer = 6;
const int redLED = 3;
const int blueLED = 4;
const int greenLED = 5;
const int button = 2;

bool active = false;
unsigned long lastPress = 0;
const int debounceDelay = 200;

void playTone(int freq, int dur){
  tone(buzzer, freq);
  delay(dur);
  noTone(buzzer);
}

void setup() {
  lcd.begin(16, 2);
  pinMode(buzzer, OUTPUT);
  pinMode(redLED, OUTPUT);
  pinMode(blueLED, OUTPUT);
  pinMode(greenLED, OUTPUT);
  pinMode(button, INPUT_PULLUP);
  lcd.clear();
  lcd.print("Press to Begin");
}

void loop() {
  if (digitalRead(button) == LOW && millis() - lastPress > debounceDelay) {
    active = true;
    lastPress = millis();
    lcd.clear();
    lcd.print("Happy Birthday!");
    digitalWrite(redLED, HIGH);
    playTone(523, 200);
    digitalWrite(redLED, LOW);
    delay(200);

    digitalWrite(blueLED, HIGH);
    playTone(659, 200);
    digitalWrite(blueLED, LOW);
    delay(200);

    lcd.clear();
    lcd.print("Shine Bright :)");
    digitalWrite(greenLED, HIGH);
    playTone(784, 600);
    digitalWrite(greenLED, LOW);
    delay(1000);
    lcd.clear();
    lcd.print("Press to Replay");
  }
}

Prototype Proof:
(Demo Video)
https://github.com/user-attachments/assets/ea758439-1e10-4a11-b26e-d77baa101c60

```

## Prototype Proof:
https://github.com/user-attachments/assets/ea758439-1e10-4a11-b26e-d77baa101c60
