### Quirky little device that displays custom messages on an LCD, paired with LED lighting sequences and buzzer tones.

---

## Summary
A compact Arduino Uno-based device designed to display personalized text messages on a 16×2 LCD, synchronized with alternating LED lights and buzzer tones.  
The goal was to create something expressive — a small emotional circuit that reacts through light and sound.  

This was built entirely on a breadboard with direct pin wiring to a standard **parallel 1602 LCD**, powered straight from a laptop’s USB port.

---

## Parts:
- **Arduino Uno**  
- **1602 LCD Display (parallel 16-pin version)**  
- **Passive Buzzer**  
- **Red LED**  
- **Blue LED**  
- **Push Button**  
- **10 kΩ Resistor** (button pull-down / input protection)  
- **Current-limiting resistors** (~220–330 Ω for LEDs)  
- **Jumper wires + Breadboard**  
- **Laptop USB (5 V) as power source**

---

## Design and Logic:
Pressing the button triggers a short sequence: the LCD displays a message while the red and blue LEDs alternate, synced with simple buzzer tones.  
The LEDs were connected to separate pins and alternated using simple digital toggling, creating a rhythmic, two-tone flash pattern that matched the tone sequence.

The **Arduino Uno** drove the **1602 LCD in 4-bit parallel mode**, using six I/O lines (RS, EN, D4–D7) plus power, ground, and contrast control via a potentiometer.  
This setup consumed most of the Uno’s pins, leaving just enough for the LEDs, button, and buzzer — a tight but functional layout.  

Power was supplied directly through the USB connection from a laptop, providing a stable 5 V line for logic, display, and LEDs.

---

## Electrical Justification:
Each LED dropped about 2.1 V, leaving roughly 2.9 V across the series resistor when powered from 5 V.  
Using ~250 Ω resistors resulted in around 11–12 mA per LED — bright, safe, and well within the Arduino’s per-pin current limit.  
A **10 kΩ resistor** was used as a pull-down for the button input, ensuring stable logic levels and preventing false triggers from floating voltages.  

The **LCD contrast** was tuned with a small potentiometer on the VO pin, balancing brightness and readability.  
The **passive buzzer** was driven directly from a digital pin with brief tone bursts to avoid drawing excess current.

---

## Challenges + Solutions:
- **Tone freezing LEDs:** Early code used blocking `delay()` for tone timing, which caused the LEDs to lag. Adjusting the timing and sequencing smoothed the behavior.  
- **Uneven brightness:** LED brightness dropped slightly when the buzzer played; powering the Uno via laptop USB instead of VIN solved it.  
- **Pin shortage:** The parallel LCD consumed many I/O pins; analog pins were repurposed as digital outputs to make everything fit.  
- **LCD flicker:** Frequent writes caused flicker; updating text only when needed solved it.  

---

## Design Improvements:
- Add **debouncing** (either with a capacitor + resistor or software delay) to prevent double-triggering from button bounce.  
- Create a **3D-printed housing or acrylic base** to make the build more durable and presentable.  
- Replace the **passive buzzer** with a **small speaker** for richer audio.  
- Upgrade to an **OLED** or **I²C LCD** to reduce wiring and free up pins.  
- Store multiple messages and tone sequences in EEPROM for replay options.  
- Add motion or sound sensors to automatically activate the display.  

---

## Code:
```cpp
#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 11, 10, 9, 8, 7); // RS, EN, D4, D5, D6, D7

const int buzzer = 6;
const int redLED = 3;
const int blueLED = 4;
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
  pinMode(button, INPUT_PULLUP);
  lcd.clear();
  lcd.print("Press to Begin");
}

void loop() {
  if (digitalRead(button) == LOW && millis() - lastPress > debounceDelay) {
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
    for (int i = 0; i < 4; i++) {
      digitalWrite(redLED, HIGH);
      playTone(784, 100);
      delay(100);
      digitalWrite(redLED, LOW);
      digitalWrite(blueLED, HIGH);
      playTone(880, 100);
      delay(100);
      digitalWrite(blueLED, LOW);
    }
    lcd.clear();
    lcd.print("Press to Replay");
  }
}
```

Prototype Proof:

(Demo Video)
https://github.com/user-attachments/assets/ea758439-1e10-4a11-b26e-d77baa101c60
