# Four-Bar Linkage Walking Robot
## Summary

This project designs, analyses, and fabricates a walking robot driven by four-bar linkage mechanisms. Two independent four-bar linkages — one for the front legs and one for the back legs — are powered by a shared crank (driving link `a`), producing a coordinated gait cycle. The mechanism was modelled in SolidWorks, kinematically verified through a custom Python simulation (`trajectory_finder.py`), and physically fabricated via FDM 3D printing using PLA on a Creality CR-10 Smart Pro.

The system satisfies a single degree of freedom (M = 1), meets the Grashof crank-rocker condition for both leg pairs, and achieves transmission angles close to 90° throughout the full rotation cycle, indicating efficient torque transfer and smooth locomotion. The robot achieves a measured walking speed of **0.153 m/s** (2 m in 13 s).

**Group 67** | Rave Bonto (Design & Fabrication) · Jon Lotilla (Design Verification & Analysis)

---

## Parts

The following components were designed in SolidWorks and 3D printed in PLA:

| Part | File | Role |
|---|---|---|
| Driving Link | `Driving Link (a).SLDPRT` | Shared crank input for both leg mechanisms |
| Front Output Link | `Front output.SLDPRT` | Output rocker for the front leg pair |
| Back Couple (L) | `Back Couple (l).SLDPRT` | Coupler link for the back leg mechanism |
| Leg Links (b, p) | `Leg Links (b,p).SLDPRT` | Front coupler, back output link and foot-offset links |
| Cover | `Cover.SLDPRT` | Protective shell cover |
| Side Shell | `Sideshell.SLDPRT` / `Sideshell - Mirror.SLDPRT` | Left and right chassis side panels |
| Top Shell | `TopShell.SLDPRT` | Upper enclosure |
| Full Assembly | `Robot Assembly.SLDASM` | Complete robot assembly |

> STL and G-code files are included for all printed components. Print settings: 0.16 mm nozzle, 210°C nozzle temp, 60°C bed temp, 0.5 mm shaft/hole clearance.

All links feature **male/female interlocking parts** for easy assembly and manufacturing. Non-critical areas include **lightening holes** (filleted cutouts) to reduce mass without compromising structural integrity, and stress concentrations at corners are mitigated by fillets.

---

## Design and Logic

### Design Objectives

The mechanism was designed around the following goals:

- **Ideal walking trajectory** — foot path imitates a natural lift phase (leg in the air) and stance phase (foot in contact with the ground)
- **Low centre of gravity** — shorter leg links reduce tipping moments and improve stability
- **Low friction** — enables effective torque and energy transfer throughout the gait cycle
- **Low mass** — lighter construction allows faster walking speed

### Degree of Freedom

The mechanism uses a standard four-bar linkage: 4 links, 4 revolute (full) joints, 0 half joints.

```
M = 3(L - 1) - 2·J1 - J2
M = 3(4 - 1) - 2(4) - 0
M = 1
```

A single degree of freedom means one motor input fully determines the motion of the entire system — ideal for a simple walking robot.

### Grashof Condition (Crank-Rocker)

For continuous rotation, both leg mechanisms must satisfy the Grashof condition with the shortest link as the crank:

```
S + L ≤ P + Q
```

**Front Mechanism** (d=27.5, a=10, b=20, c=32):
```
10 + 32 ≤ 20 + 27.5
42 ≤ 47.5  ✓
```

**Back Mechanism** (d=122.1, a=10, b=123, c=20):
```
10 + 123 ≤ 122.1 + 20
133 ≤ 142.1  ✓
```

Both mechanisms satisfy the Grashof condition, enabling full crank rotation from a single motor.

### Link Length Rationale

Link lengths were not chosen arbitrarily — a custom Python trajectory simulator was used to test different configurations and find foot paths that most closely resemble natural walking (long flat stance phase + fast symmetrical lift phase).

| Link | Value (mm) | Role | Design Reasoning |
|---|---|---|---|
| Driving link `a` | 10 | Shared crank | Short crank = controlled, stable input. Longer cranks produced erratic, jerky foot trajectories. |
| Front coupler `b` | 20 | Coupler | Determines foot path curvature and arc smoothness. Critical for stride quality. |
| Front output `c` | 32 | Output rocker | Controls step height and forward reach. Sized to avoid excessive air time. |
| Front ground `d` | 27.5 | Ground | Sets mechanism scale and positional stability for the front legs. |
| Back coupler `l` | 123 | Coupler | Chosen approximately equal to `m` — elongated configuration lowers foot path curvature, producing a flatter trajectory, longer horizontal travel, and improved stance duration. |
| Back output `b` | 20 | Output rocker | Shorter output limits back leg lift, keeping the rear grounded during propulsion. |
| Back ground `m` | 122.1 | Ground | Derived from chassis geometry: `m = √(122² + 5²) = 122.1 mm`. Matched to back coupler for correct Grashof ratio. |
| Foot offset `B_to_P` | 8 | Foot extension | Converts joint rotation into a realistic walking stride. Tuned for flat stance and optimal lift clearance. |

### Transmission Angle

The transmission angle μ is the acute angle between the coupler and output link, and must remain between 40° and 140° for effective force transfer (optimal at 90°).

```
α = |θ₄ - θ₃|
μ = min(α, 180° - α)
```

Simulation results confirm transmission angles remain close to 90° throughout the full crank rotation for both leg pairs, indicating near-maximum torque transfer and minimal risk of mechanism lock.

---

## Code

Two analysis tools were developed: a MATLAB script for angular velocity analysis, and a Python GUI simulation for interactive gait cycle visualisation.

### Python — Gait Cycle Simulator (`trajectory_finder.py`)

An interactive PyQtGraph application that animates the full gait cycle in real time. Users can adjust all link lengths and observe the resulting foot trajectories and transmission angles live. This tool was central to the link length selection process.

**Key functions:**

```python
def grashof_gcrr(link_list):
    # Returns True if mechanism satisfies Grashof crank-rocker condition
    s = min(link_list)
    l = max(link_list)
    ...
    return (s + l < p + q) and (s == link_list[0])

def k_vals(a, b, c, d):
    # Freudenstein equation constants
    k1 = d / a
    k2 = d / c
    k3 = (a**2 - b**2 + c**2 + d**2) / (2 * a * c)
    return k1, k2, k3

def theta_4(a_inter, b_inter, c_inter):
    # Solves for output link angle (open and crossed configurations)
    # Uses half-angle substitution method
    ...

def transmission_angle(theta_4_open, theta_4_crossed, theta_3_open, theta_3_crossed):
    # Computes μ = min(|θ4 - θ3|, 180 - |θ4 - θ3|)
    ...

def generate_trajectory(front_leg, back_leg, B_to_P, step=0.25):
    # Sweeps theta_2 from 0–360° and records foot (P) positions
    ...
```

The `GaitApp` class renders the animated mechanism with live joint positions, link segments, foot paths, and current transmission angles displayed in the plot title.

**Dependencies:** `pyqtgraph`, `math` (stdlib)

---

### MATLAB — Angular Velocity Analysis

Computes and plots ω₃ and ω₄ (coupler and output angular velocities) across the full 360° input cycle for both leg mechanisms.

```matlab
omega_2 = 12.56;  % rad/s input speed

% Angular velocity equations
omega_3 = (a * omega_2 * sind(theta_4 - theta_2)) / (b * sind(theta_3 - theta_4));
omega_4 = (a * omega_2 * sind(theta_2 - theta_3)) / (c * sind(theta_4 - theta_3));
```

Separate figures are generated for the front and back leg velocity profiles across the full input sweep.

---

## Challenges Faced + Solutions

| Challenge | Solution |
|---|---|
| Prototype too heavy and unstable | Reduced leg link lengths to lower the centre of gravity. Moved rear legs further outward to widen the support base and improve gait balance. |
| Excessive friction in prototype | Increased clearances between male and female parts. Switched to interlocking part geometry to reduce binding at joints. |
| Unreliable pin-shaft joints in prototype | Replaced pin system with integrated male/female part design for more reliable and repeatable assembly. |
| Jerky, unstable foot trajectory | Reduced driving link length (`a = 10`). Shorter crank produced smoother, more controlled foot arcs. |
| Mechanism locking during rotation | Adjusted link ratios to maintain transmission angle within 40°–140° range throughout full crank cycle. Verified computationally via `mechanism_valid()`. |
| Back leg trajectory too tall / excessive air time | Chose back coupler `l ≈ m` (both ~122–123 mm) to create an elongated configuration that flattens the foot path and increases stance phase duration. |
| 3D printing fit issues (shaft binding) | Applied 0.5 mm clearance between all shaft and hole features across all printed parts. |
| Difficult assembly in prototype | Incorporated male/female interlocking features on all links. Redesign made assembly and disassembly straightforward. |

---

## Design Improvements

- **Dynamic load analysis** — The current model is purely kinematic. Incorporating dynamic modelling (inertia, ground reaction forces) would allow for better motor and structural sizing.
- **Material upgrade** — PLA is suitable for a prototype but brittle under repeated stress. PETG or ABS would improve fatigue life for extended use.
- **Multi-leg coordination** — Currently front and back legs share a crank but are not actively phased. Introducing a deliberate phase offset between front and back pairs would improve gait stability and reduce tipping.
- **Terrain adaptability** — The mechanism is tuned for flat surfaces. Adding passive compliance (e.g. spring-loaded foot links) would allow the robot to handle minor surface irregularities.
- **Motor mounting** — The current assembly does not include a dedicated motor mount or gearbox housing. A proper drivetrain enclosure would improve robustness and replaceability.
- **Adjustable foot offset** — Making `B_to_P` mechanically adjustable would allow stride length to be tuned without reprinting parts.

---

## Proof

**Assembly Video**

[![Watch assembly](https://img.youtube.com/vi/0cOz-wgVECU/0.jpg)](https://youtu.be/0cOz-wgVECU)

**Demo Video**

[![Watch the demo](https://img.youtube.com/vi/JxqmznvLmQk/0.jpg)](https://youtube.com/shorts/JxqmznvLmQk)
