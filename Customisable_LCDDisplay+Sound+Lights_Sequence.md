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

LiquidCrystal lcd(7, 8, 9, 10, 11, 12);  // RS, E, D4, D5, D6, D7

const int BUTTON_PIN = 2;
const int BUZZER_PIN = 3;
const int RED_LED = 5;
const int BLUE_LED = 4;

const int LED_ON  = HIGH;
const int LED_OFF = LOW;

const unsigned long PAGE_MS = 1600;
const unsigned long BLINK_MS = 300;
const unsigned long TONE_GAP_MS = 50;

struct Page {
  const char* line1;
  const char* line2;
};

Page pages[] = {
  {"<LINE 1>", "<LINE 2>"},
  {"<LINE 3>", "<LINE 4>"},
  {"<LINE 5>", "<LINE 6>"}
};

const int NUM_PAGES = sizeof(pages) / sizeof(pages[0]);
int notes[] = {262, 294, 330, 349, 392, 440, 494, 523};
const int NUM_NOTES = sizeof(notes) / sizeof(notes[0]);

void setLEDs(bool redOn, bool blueOn) {
  digitalWrite(RED_LED, redOn ? LED_ON : LED_OFF);
  digitalWrite(BLUE_LED, blueOn ? LED_ON : LED_OFF);
}

void playToneMs(int freq, int durMs) {
  if (freq <= 0 || durMs <= 0) return;
  tone(BUZZER_PIN, freq, durMs);
  delay(durMs + TONE_GAP_MS);
  noTone(BUZZER_PIN);
}

void flashPatternStep(int stepIdx) {
  bool red = (stepIdx % 2 == 0);
  bool blue = !red;
  setLEDs(red, blue);
  playToneMs(notes[stepIdx % NUM_NOTES], 120);
  delay(BLINK_MS);
  setLEDs(false, false);
}

void drawPage(const Page& p) {
  lcd.clear();
  lcd.setCursor(0, 0); lcd.print(p.line1);
  lcd.setCursor(0, 1); lcd.print(p.line2);
}

void runShow() {
  for (int i = 0; i < NUM_PAGES; ++i) {
    drawPage(pages[i]);
    unsigned long t0 = millis();
    int step = 0;
    while (millis() - t0 < PAGE_MS) {
      flashPatternStep(step++);
    }
  }

  lcd.clear();
  lcd.setCursor(0, 0); lcd.print("<FINALE LINE 1>");
  lcd.setCursor(0, 1); lcd.print("<FINALE LINE 2>");
  for (int i = 0; i < 6; ++i) {
    setLEDs(i % 2, (i + 1) % 2);
    playToneMs(notes[(i * 2) % NUM_NOTES], 140);
  }
  setLEDs(false, false);
  delay(800);
  lcd.clear();
  lcd.print("<PRESS TO REPLAY>");
}

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(BLUE_LED, OUTPUT);

  setLEDs(false, false);

  lcd.begin(16, 2);
  lcd.clear();
  lcd.print("<PRESS TO BEGIN>");
}

void loop() {
  if (digitalRead(BUTTON_PIN) == LOW) {
    while (digitalRead(BUTTON_PIN) == LOW);
    delay(50);
    runShow();
    lcd.clear();
    lcd.print("<PRESS TO BEGIN>");
  }
}

```

Prototype Proof:

(Demo Video)
https://github.com/user-attachments/assets/ea758439-1e10-4a11-b26e-d77baa101c60
