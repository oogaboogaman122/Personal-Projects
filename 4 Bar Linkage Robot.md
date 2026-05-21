# Four-Bar Linkage Walking Robot
## Summary

This project designs, analyses, and fabricates a walking robot driven by four-bar linkage mechanisms. Two independent four-bar linkages — one for the front legs and one for the back legs — are powered by a shared crank (driving link `a`), producing a coordinated gait cycle. The mechanism was modelled in SolidWorks, kinematically verified through a custom Python simulation (`trajectory_finder.py`), and physically fabricated via FDM 3D printing using PLA on a Creality CR-10 Smart Pro.

The system satisfies a single degree of freedom (M = 1), meets the Grashof crank-rocker condition for both leg pairs, and achieves transmission angles close to 90° throughout the full rotation cycle, indicating efficient torque transfer and smooth locomotion.

**Group 67** | Rave Bonto (Design & Fabrication) · Jon Lotilla (Design Verification & Analysis)

---

## Parts

The following components were designed in SolidWorks and 3D printed in PLA:

| Part | File | Role |
|---|---|---|
| Driving Link | `Driving Link (a).SLDPRT` | Shared crank input for both leg mechanisms |
| Front Output Link | `Front output.SLDPRT` | Output rocker for the front leg pair |
| Back Couple (L) | `Back Couple (l).SLDPRT` | Coupler link for the back leg mechanism |
| Leg Links (b, p) | `Leg Links (b,p).SLDPRT` | Coupler and foot-offset links |
| Bar | `bar.SLDPRT` | Ground link / chassis connection |
| Cover | `Cover.SLDPRT` | Protective shell cover |
| Side Shell | `Sideshell.SLDPRT` / `Sideshell - Mirror.SLDPRT` | Left and right chassis side panels |
| Top Shell | `TopShell.SLDPRT` | Upper enclosure |
| Full Assembly | `Robot Assembly.SLDASM` | Complete robot assembly |

> STL and G-code files are included for all printed components. Print settings: 0.16 mm nozzle, 210°C nozzle temp, 60°C bed temp, 0.5 mm shaft/hole clearance.

---

## Design and Logic

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
133 ≤ 142.1  ✓  (note: back mechanism uses rocker-crank configuration)
```

Both mechanisms satisfy the Grashof condition, enabling full crank rotation from a single motor.

### Link Length Rationale

| Link | Role | Design Reasoning |
|---|---|---|
| Driving link `a` = 10 | Shared crank | Short crank = controlled, stable input motion. Longer cranks produced erratic, jerky foot trajectories. |
| Front coupler `b` = 20 | Coupler | Determines foot path curvature and arc smoothness. Critical for stride quality. |
| Front output `c` = 32 | Output rocker | Controls step height and forward reach. Sized to avoid excessive air time (instability). |
| Front ground `d` = 27.5 | Ground | Sets mechanism scale and positional stability for the front legs. |
| Back coupler `b` = 123 | Coupler | Long coupler produces a near-linear back foot path, improving stance phase stability. |
| Back output `c` = 20 | Output rocker | Shorter output limits back leg lift, keeping the rear grounded during propulsion. |
| Back ground `d` = 122.1 | Ground | Matched to back coupler length for correct Grashof ratio. |
| Foot offset `B_to_P` | Foot extension | Converts simple joint rotation into a realistic walking stride. Tuned for flat stance and optimal lift. |

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

An interactive PyQtGraph application that animates the full gait cycle in real time. Users can adjust all link lengths and observe the resulting foot trajectories and transmission angles live.

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

Separate figures are generated for the front and back leg velocity profiles across the input sweep.

---

## Challenges Faced + Solutions

| Challenge | Solution |
|---|---|
| Jerky, unstable foot trajectory | Reduced driving link length (`a = 10`). Shorter crank produced smoother, more controlled foot arcs. |
| Mechanism locking during rotation | Adjusted link ratios to maintain transmission angle within 40°–140° range throughout full crank cycle. Verified computationally. |
| Back leg trajectory too tall / excessive air time | Lengthened back coupler (`b = 123`) to flatten the foot path, keeping the rear legs closer to the ground during the stance phase. |
| 3D printing fit issues (shaft binding) | Applied 0.5 mm clearance between all shaft and hole features across all printed parts. |
| Front legs reaching too far forward | Tuned output link `c` and foot offset `B_to_P` together to balance stride length against forward reach without causing instability. |
| Grashof validation failing in simulation | Added `mechanism_valid()` function that sweeps all 360° positions and confirms both Grashof and full-rotation solvability before animating. |

---

## Design Improvements

- **Dynamic load analysis** — The current model is purely kinematic. Incorporating dynamic modelling (inertia, ground reaction forces) would allow for better motor and structural sizing.
- **Material upgrade** — PLA is suitable for a prototype but brittle under repeated stress. PETG or ABS would improve fatigue life for extended use.
- **Multi-leg coordination** — Currently front and back legs share a crank but are not actively phased. Introducing a deliberate phase offset between front and back pairs would improve gait stability and reduce tipping.
- **Terrain adaptability** — The mechanism is tuned for flat surfaces. Adding passive compliance (e.g. spring-loaded foot links) would allow the robot to handle minor surface irregularities.
- **Motor mounting** — The current assembly does not include a dedicated motor mount or gearbox housing. A proper drivetrain enclosure would improve robustness and replaceability.
- **Adjustable foot offset** — Making `B_to_P` mechanically adjustable would allow stride length to be tuned without reprinting parts.
