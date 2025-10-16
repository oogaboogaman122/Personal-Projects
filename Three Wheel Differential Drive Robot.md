# 3-Wheeled ESP32 Robot
### Programmable and remotely controlled through a web interface

---

## Summary
This project is a compact 3-wheeled robot that can be programmed or controlled remotely over Wi-Fi using an onboard web interface.  
The system is built around an ESP32 microcontroller, which handles both motor control and network communication without any external modules.  
The entire robot was built experimentally — no formal circuit diagram or simulation, just iterative wiring and logic testing until the performance matched expectations.  
Despite the hands-on build approach, the result is a stable, responsive robot capable of smooth motion, braking, and precise directional control.  
It serves as a solid foundation for future robotics development involving web-based control and autonomous movement.

---

## Parts
- **MD33A Motor Driver**  
- **2 × TT Motors** (3 V, 150 mA no-load)  
- **1 × Tracker Ball** (salvaged from a vacuum cleaner)  
- **Laser-cut flat chassis** (Plywood_
- **ESP32 Development Board**  
- **Power Bank** (for ESP32)  
- **6 × AA Ni-MH Rechargeable Batteries** (connected in series for motor power)

---

## Design and Logic
The robot uses a **differential drive system**, powered by two motors at the sides and a single tracker ball for balance.  
Each motor is driven through one half of the MD33A motor driver, controlled by PWM signals from the ESP32.  
A signed PWM value determines direction and speed:  
- Positive = forward  
- Negative = reverse  
- Zero = coast  
- Both inputs high = hard brake  

The ESP32 also runs a **web server**, which provides a control page accessible from any phone or computer.  
Commands are sent over HTTP using simple GET requests, triggered by either keyboard input (W, A, S, D, Space, Shift) or touchscreen buttons.  
The ESP32 processes these requests, calculates the correct signed PWM values for each motor, and updates them at a 50 Hz control loop for smooth, predictable motion.  

A **ramping system** prevents sudden acceleration, while an **anti-stiction pulse** briefly increases PWM when the motors start from rest to overcome static friction.  
Even though the wiring was improvised, the layout remained efficient, with short, direct connections between components to minimize loss and noise.

The ESP32 has its own power supply via powerbank for a clean regulated 5v source, while the motors had a roundabout 7.2V supply from the 6 makeshift battery pack.

<div align="center">
  <img src="https://github.com/user-attachments/assets/413f6713-7383-4c41-ae99-bbbd2cd54331" width="400">
  <p><i>Top View</i></p>
<br><br>
  <img src="https://github.com/user-attachments/assets/1024f86a-8aba-484c-96d6-a0be3a2bf03a" width="400">
  <p><i>Side View</i></p>
</div>



## Challenges Faced + Solutions
**Wheel placement and balance**  
The drive wheels were positioned near the middle of the chassis, and the tracker ball was placed at the back.  
This caused a **reverse-fulcrum effect**, where acceleration made the robot lean slightly backward and braking made it tilt forward and be unbalanced.  
*Solution:* Future iterations should place the drive wheels further forward and keep the tracker ball at the rear for proper balance, traction, and weight distribution.

**Power setup**  
Without a battery holder, the six Ni-MH cells were connected in series using duct tape. Initially, jumper wires were used, but they caused poor contact and high resistance.  
*Solution:* Stripping the wires improved conductivity, but the right approach is to use a **battery holder** or **flat metal connectors** for stable contact and safety.


---

## Design Improvements
- Reposition the drive wheels forward to correct weight balance.  
- Replace the temporary battery wiring with a **proper holder or 3D-printed case**.  
- Add **wheel encoders** for precise closed-loop feedback.  
- Include **status LEDs** or a **small OLED display** to show Wi-Fi and battery levels.  
- Upgrade to a **TB6612FNG motor driver** or create a **custom motor driver** for cleaner switching and current sensing.    
- Integrate all electronics into a **3D-printed chassis** for strength and cable management.


---

## Code
The firmware handles both web hosting and low-level motor control.  
The following is a simplified version showing the core loop and PWM structure:

```cpp
/*
A B
0 1 = REVERSE
1 0 = FORWARD
1 1 = HARD BRAKE
0 0 = COAST
*/
#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>

//Set up bot credentials
const char* AP_SSID   = "Bot_AP";
const char* AP_PASS   = "robot123";

//Webserver set up
WebServer http(80);

//MD33A pins
const int M1A_PIN = 19, M1B_PIN = 18;   // left
const int M2A_PIN = 17, M2B_PIN = 16;   // right

const int CH_M1A = 0;
const int CH_M1B = 1;
const int CH_M2A = 2;
const int CH_M2B = 3;

const uint32_t PWM_FREQ = 20000;
const uint8_t  PWM_RES  = 9;
const int      MAX_DUTY = (1 << PWM_RES) - 1;

const int      SPEED_PWM     = 420;
const int      RAMP_STEP     = 30;
const int      MIN_START_PWM = 90;
const uint32_t KICK_MS       = 80;
const uint32_t TICK_MS       = 20;
const uint32_t HOLD_MS       = 120;

//Movement logic
uint32_t tW=0, tA=0, tS=0, tD=0, tBrake=0;
bool web_W=false, web_A=false, web_S=false, web_D=false;
bool web_BRAKE=false, web_BOOST=false;

int curL=0, curR=0;
int tgtL=0, tgtR=0;
uint32_t kickL_until=0, kickR_until=0;
uint32_t lastTick=0;

//Check if button is held down
inline bool held(uint32_t t, uint32_t now){ return (now - t) < HOLD_MS; }
inline void rampToward(int &x, int tgt, int step){
  if (x < tgt) x = min(x + step, tgt);
  else if (x > tgt) x = max(x - step, tgt);
}

static inline void pwmWriteCH(int ch, int duty){ ledcWrite(ch, duty); }

//Control one motor
void writeOneMotor(int chA, int chB, int cmdSigned, bool inverted){
  if (cmdSigned == 0){ pwmWriteCH(chA,0); pwmWriteCH(chB,0); return; }
  const int duty = abs(cmdSigned);
  const bool forward = (cmdSigned > 0) ^ inverted;
  if (forward){
    pwmWriteCH(chA, duty); pwmWriteCH(chB, 0);
  } else {
    pwmWriteCH(chA, 0);    pwmWriteCH(chB, duty);
  }
}

//Control both motors
void writeHBridge(int pwmL, int pwmR, bool hardBrake){
  if (hardBrake && pwmL==0 && pwmR==0){
    pwmWriteCH(CH_M1A, MAX_DUTY); pwmWriteCH(CH_M1B, MAX_DUTY);
    pwmWriteCH(CH_M2A, MAX_DUTY); pwmWriteCH(CH_M2B, MAX_DUTY);
    return;
  }
  const bool INV_LEFT = true;
  const bool INV_RIGHT = false;
  writeOneMotor(CH_M1A, CH_M1B, pwmL,  INV_LEFT);
  writeOneMotor(CH_M2A, CH_M2B, pwmR, INV_RIGHT);
}

//Handle serial input from putty
void handleSerialKey(char k){
  const uint32_t now = millis();
  if (k=='\r'||k=='\n') return;
  if (k=='x'||k=='X'){ tW=tA=tS=tD=tBrake=0; return; }
  if (k==' ')        { tBrake = now; return; }
  if (k=='w'||k=='W') tW = now;
  if (k=='a'||k=='A') tA = now;
  if (k=='s'||k=='S') tS = now;
  if (k=='d'||k=='D') tD = now;
}

const char HTML[] PROGMEM = R"HTML(
<!doctype html><html><head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>ESP32 Robot Controller</title>
<style>
  body { font-family: system-ui, sans-serif; margin: 24px; }
  .pad { display:grid; grid-template-columns:repeat(3,80px); gap:12px; margin-top:16px; }
  button { padding:16px; font-size:18px; border-radius:12px; border:1px solid #ccc; }
  .row { display:flex; gap:12px; align-items:center; margin-top:12px; }
  .led { width:10px; height:10px; border-radius:50%; background:#ccc; display:inline-block; margin-left:6px;}
  .on { background:#0a0; }
  .bad { color:#b00; }
</style>
</head><body>
<h2>ESP32 Robot Controller</h2>
<p>Use keyboard: <b>W/A/S/D</b>, <b>Shift</b>=Turbo, <b>Space</b>=Hard brake, <b>X</b>=Coast stop.</p>
<div class="row">
  <label><input id="turbo" type="checkbox"> Turbo (Shift)</label>
  <span>Connected: <span id="net" class="led"></span></span>
</div>
<div class="pad">
  <span></span><button id="btnW">W</button><span></span>
  <button id="btnA">A</button><button id="btnS">S</button><button id="btnD">D</button>
</div>
<div class="row"><button id="btnBrake">Hard Brake</button><button id="btnCoast">Coast (X)</button></div>
<p id="msg" class="bad"></p>
<script>
const net = document.getElementById('net');
const turbo = document.getElementById('turbo');
const msg = document.getElementById('msg');
let pressed = new Set();
let online = false;
function setLed(ok){ net.classList.toggle('on', !!ok); online = !!ok; }
async function send(k, down) {
  try{
    const shift = (turbo.checked || pressed.has('Shift')) ? 1 : 0;
    const url = `/k?k=${encodeURIComponent(k)}&s=${down?1:0}&shift=${shift}`;
    const res = await fetch(url, {method:'GET', cache:'no-cache'});
    setLed(res.ok);
    if(!res.ok){ msg.textContent = 'HTTP not OK'; }
    else { msg.textContent = ''; }
  }catch(e){
    setLed(false);
    msg.textContent = 'Network error';
  }
}
function press(k){ if(pressed.has(k)) return; pressed.add(k); send(k,true); }
function release(k){ if(!pressed.has(k)) return; pressed.delete(k); send(k,false); }
document.addEventListener('keydown', (e)=>{
  if (['w','a','s','d','W','A','S','D',' '].includes(e.key) || e.key==='Shift'){
    e.preventDefault();
    if(e.key===' ') press('SPACE'); else press(e.key);
  }
});
document.addEventListener('keyup', (e)=>{
  if (['w','a','s','d','W','A','S','D',' '].includes(e.key) || e.key==='Shift'){
    e.preventDefault();
    if(e.key===' ') release('SPACE'); else release(e.key);
  }
});
function bindHold(id, key){
  const el = document.getElementById(id);
  el.addEventListener('mousedown', ()=>press(key));
  el.addEventListener('mouseup',   ()=>release(key));
  el.addEventListener('mouseleave',()=>release(key));
  el.addEventListener('touchstart',(ev)=>{ev.preventDefault(); press(key);},{passive:false});
  el.addEventListener('touchend',  (ev)=>{ev.preventDefault(); release(key);},{passive:false});
}
bindHold('btnW','w'); bindHold('btnA','a'); bindHold('btnS','s'); bindHold('btnD','d');
document.getElementById('btnBrake').addEventListener('click', ()=> send('SPACE', true));
document.getElementById('btnCoast').addEventListener('click', ()=> send('X', true));
setInterval(()=>send('PING', true), 2000);
</script>
</body></html>
)HTML";

void handleRoot(){
  http.setContentLength(strlen_P(HTML));
  http.send_P(200, "text/html", HTML);
}

void handleKeyHTTP(){
  if (!http.hasArg("k") || !http.hasArg("s")){
    http.send(400, "text/plain", "bad args");
    return;
  }
  String key = http.arg("k");
  bool down  = http.arg("s").toInt() == 1;
  bool shift = http.hasArg("shift") && (http.arg("shift").toInt() == 1);

  if (key == "w" || key == "W") web_W = down;
  else if (key == "a" || key == "A") web_A = down;
  else if (key == "s" || key == "S") web_S = down;
  else if (key == "d" || key == "D") web_D = down;
  else if (key == "SPACE") web_BRAKE = down;
  else if (key == "X" || key == "x"){
    web_W=web_A=web_S=web_D=web_BRAKE=false;
    web_BOOST=false;
  }
  web_BOOST = shift;
  http.send(200, "text/plain", "ok");
}

void setup(){
  Serial.begin(115200);

  ledcSetup(CH_M1A, PWM_FREQ, PWM_RES);
  ledcSetup(CH_M1B, PWM_FREQ, PWM_RES);
  ledcSetup(CH_M2A, PWM_FREQ, PWM_RES);
  ledcSetup(CH_M2B, PWM_FREQ, PWM_RES);

  ledcAttachPin(M1A_PIN, CH_M1A);
  ledcAttachPin(M1B_PIN, CH_M1B);
  ledcAttachPin(M2A_PIN, CH_M2A);
  ledcAttachPin(M2B_PIN, CH_M2B);

  ledcWrite(CH_M1A,0); ledcWrite(CH_M1B,0);
  ledcWrite(CH_M2A,0); ledcWrite(CH_M2B,0);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  uint32_t t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 10000){
    delay(100);
  }
  if (WiFi.status() == WL_CONNECTED){
    Serial.print("WiFi STA OK. http://"); Serial.println(WiFi.localIP());
  } else {
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASS);
    Serial.print("AP mode. SSID="); Serial.print(AP_SSID);
    Serial.print("  http://"); Serial.println(WiFi.softAPIP());
  }

  http.on("/", HTTP_GET, handleRoot);
  http.on("/k", HTTP_GET, handleKeyHTTP);
  http.begin();

  lastTick = millis();
}

void loop(){
  http.handleClient();

  while (Serial.available()){
    handleSerialKey((char)Serial.read());
  }

  const uint32_t now = millis();
  if (now - lastTick < TICK_MS) return;
  lastTick += TICK_MS;

  const bool W = web_W || held(tW, now);
  const bool A = web_A || held(tA, now);
  const bool S = web_S || held(tS, now);
  const bool D = web_D || held(tD, now);
  const bool brake = web_BRAKE || held(tBrake, now);
  const bool boost = web_BOOST;

  int base = (W ? 1 : 0) - (S ? 1 : 0);
  int turn = (D ? 1 : 0) - (A ? 1 : 0);
  int leftSign  = constrain(base - turn, -1, 1);
  int rightSign = constrain(base + turn, -1, 1);

  const int mag = boost ? MAX_DUTY : SPEED_PWM;
  const int newTgtL = leftSign  * mag;
  const int newTgtR = rightSign * mag;

  if (curL==0 && newTgtL!=0) kickL_until = now + KICK_MS;
  if (curR==0 && newTgtR!=0) kickR_until = now + KICK_MS;

  tgtL = newTgtL;  tgtR = newTgtR;

  rampToward(curL, tgtL, RAMP_STEP);
  rampToward(curR, tgtR, RAMP_STEP);

  int outL = curL, outR = curR;
  if (now < kickL_until && outL!=0 && abs(outL)<MIN_START_PWM)
    outL = (outL>0)? MIN_START_PWM : -MIN_START_PWM;
  if (now < kickR_until && outR!=0 && abs(outR)<MIN_START_PWM)
    outR = (outR>0)? MIN_START_PWM : -MIN_START_PWM;

  if (leftSign==0 && rightSign==0 && !brake) writeHBridge(0,0,false);
  else writeHBridge(outL, outR, brake && leftSign==0 && rightSign==0);
}
```

## Prototype Proof:
https://github.com/user-attachments/assets/08b92a20-9a07-4f44-80c4-63731d2354ee

