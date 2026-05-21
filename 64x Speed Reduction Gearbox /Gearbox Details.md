# 3 Stage Spur Gearbox

## Summary

This project designs, analyses, and fabricates a compact three-stage spur gear reduction gearbox capable of achieving a **64:1 speed reduction** (within the required 65:1 ±3% tolerance) while delivering **20 Nm output torque** from a 1500 RPM input. The gearbox operates bidirectionally with no self-locking, and was designed for both prototype testing and steel fatigue life verification.

Five independent concepts were evaluated using a weighted design matrix across efficiency, longevity, feasibility, and manufacturability. The **3-stage spur gearbox** scored highest (86.7/100) and was selected as the final design.

The prototype was fabricated using laser-cut acrylic gears, plywood housing, and aluminium shafts. Testing confirmed a maximum efficiency of **83.5%**, exceeding the 80% theoretical target. The steel design analysis verified infinite shaft fatigue life (min FOS 9.46) and over two years of continuous gear life (min FOS 2.22).

---

## Parts

### Gears (Laser-cut Acrylic, Module 3, 9 mm face width)

| Part | Teeth | Pitch Diameter (mm) | Shaft | File |
|---|---|---|---|---|
| Gear A (Pinion, Stage 1) | 20 | 60 | 10 mm |  |
| Gear B (Driven, Stage 1) | 80 | 240 | 10 mm |  |
| Gear C (Pinion, Stage 2) | 20 | 60 | 10 mm |  |
| Gear D (Driven, Stage 2) | 80 | 240 | 12 mm |  |
| Gear E (Pinion, Stage 3) | 20 | 60 | 12 mm |  |
| Gear F (Driven, Stage 3) | 80 | 240 | 15.88 mm |  |

### Shafts (Aluminium)

| Part | Diameter | Material | File |
|---|---|---|---|
| Input Shaft | 10 mm | 6060 T5 Al |  |
| Intermediate Shaft 1 | 10 mm | 6060 T5 Al |  |
| Intermediate Shaft 2 | 12 mm | 6060 T5 Al |  |
| Output Shaft | 15.88 mm (5/8") | 6061 T6 Al |  |

### Split Collars

| Part | File |
|---|---|
| Split Collar (10 mm bore) |  |
| Split Collar (12 mm bore) |  |
| Split Collar (15.88 mm bore) |  |

### Housing Panels

| Part | Description | File |
|---|---|---|
| Front Panel | Acrylic bearing plate, shaft holes |  |
| Back Panel / Other Panel | Rear acrylic bearing plate |  |
| Side Panel (Left) | Plywood side wall |  |
| Side Panel (Right) | Plywood side wall |  |
| Bottom Panel | Plywood base |  |
| Top Panel | Plywood top cover |  |

### Shaft Sub-assemblies

| Part | File |
|---|---|
| Input Shaft Assembly |  |
| 2nd Shaft Assembly |  |
| 3rd Shaft Assembly |  |
| Output Shaft Assembly |  |

### Full Assembly

| Part | File |
|---|---|
| Complete Gearbox Prototype |  |

> STL files included for all panel and collar components for laser cutting and fabrication. All gears are 9 mm laser-cut acrylic (prototype). Housing is 10 mm plywood. Shaft-to-gear connections use split collars with pin holes for positive locking.

---

## Design and Logic

### Design Objectives

- Achieve 65:1 (±3%) speed reduction — two or more stages required
- Deliver 20 Nm output torque at 1500 RPM input without failure
- Operate bidirectionally — no self-locking mechanisms
- Maintain ≥80% theoretical efficiency, ≥70% prototype efficiency
- All shafts and gears to withstand shear, bending, and torsion stresses
- Steel design: infinite shaft fatigue life, ≥2 years continuous gear life

### Design Selection

Five concepts were evaluated using a weighted matrix (Efficiency ×4, Longevity ×3, Feasibility ×2, Manufacturability ×1):

| Concept | Score (/100) | Key Trade-off |
|---|---|---|
| 2-Stage Spur | 75.6 | High efficiency, poor longevity (high pinion stress) |
| 2-Stage Split Torque | 76.8 | Good spread load, input gear overworked |
| **3-Stage Spur** | **86.7** | **Best balance across all categories — selected** |
| 4-Stage Spur | 72.0 | High longevity, poor compactness and efficiency |
| 3-Stage Planetary | 70.4 | High efficiency/longevity, very hard to manufacture |

The 3-stage spur design was selected for its strong balance of all four criteria and its simplicity in layout and manufacture.

### Gear Ratios and Stage Layout

Each stage uses an identical 4:1 reduction (20T pinion → 80T driven gear, module 3):

```
Stage 1:  1500 RPM  →  375 RPM    Torque: 0.364 Nm → 1.385 Nm
Stage 2:   375 RPM  →  93.75 RPM  Torque: 1.385 Nm → 5.263 Nm
Stage 3:  93.75 RPM →  23.44 RPM  Torque: 5.263 Nm → 20 Nm

Overall ratio: 4 × 4 × 4 = 64:1  (within 65 ±3% tolerance)
```

### Mesh Forces (Steel Design)

All forces calculated from 20 Nm output requirement, working backwards. Pressure angle 20° for all gears.

| Stage | Gear Pair | Pinion Torque (Nm) | Ft (N) | Fr (N) |
|---|---|---|---|---|
| 1 | A → B | 0.364 | 12.15 | 4.42 |
| 2 | C → D | 1.385 | 46.17 | 16.80 |
| 3 | E → F | 5.263 | 175.44 | 63.85 |

### Shaft Fatigue Analysis — Steel (Modified Goodman, Infinite Life)

Material: AISI 4140 | Sut = 1020 MPa | Sy = 655 MPa | Sn = 278.89 MPa

| Shaft | d (mm) | M (N·mm) | T (N·mm) | σa (MPa) | σm (MPa) | Critical Mode | FOS |
|---|---|---|---|---|---|---|---|
| Input | 10 | 133.6 | 364 | 1.36 | 3.20 | Fatigue | **124.8** |
| Intermediate 1 | 10 | 989.4 | 1385 | 10.08 | 12.21 | Fatigue | **20.8** |
| Intermediate 2 | 12 | 3758.7 | 5263 | 22.15 | 26.86 | Fatigue | **9.46** |
| Output | 15.88 | 2500.8 | 20000 | 6.37 | 44.09 | Yielding | **12.98** |

All shafts meet infinite fatigue life requirement (min FOS 9.46).

### Gear Fatigue Analysis — Steel (AGMA, 2-Year Life)

Material: AISI 1040 | Sut = 500 MPa | Surface hardness 375 Bhn

| Stage | Ft (N) | Bending FOS | Contact FOS | Governing FOS |
|---|---|---|---|---|
| A–B (Stage 1) | 12.15 | 79.0 | 6.13 | **6.13** |
| C–D (Stage 2) | 46.17 | 24.2 | 3.76 | **3.76** |
| E–F (Stage 3) | 175.44 | 6.92 | 2.22 | **2.22** |

Surface contact fatigue (pitting) governs all stages. Minimum overall FOS: **2.22** (Stage 3). All stages meet the 2-year continuous life requirement.

### Design Iterations

| Version | Description | Changes |
|---|---|---|
| V1 | Initial 3-stage kinematic layout | No defined assembly method, bearing placement, or gear-shaft connection |
| V2 | Prototype CAD with shaft diameters and bearing pockets | Fixed housing assembly — gears used friction-fit only, slipped under load |
| V3 (Final) | Pin holes added to all gears and shafts | Eliminated gear slip, optimised bearing spacers for shaft alignment |

---

## Code

### MATLAB — Angular Velocity Analysis

Computes and plots ω₃ and ω₄ (coupler and output angular velocities) across the full 360° input cycle for all three stages.

```matlab
omega_2 = 2 * pi * 1500 / 60;  % rad/s input speed (1500 RPM)

% Angular velocity equations
omega_3 = (a * omega_2 * sind(theta_4 - theta_2)) / (b * sind(theta_3 - theta_4));
omega_4 = (a * omega_2 * sind(theta_2 - theta_3)) / (c * sind(theta_4 - theta_3));
```

Separate figures are generated for each stage's velocity profiles across the full input sweep.

---

## Challenges Faced + Solutions

| Challenge | Solution |
|---|---|
| Gears slipping around shafts under load | Replaced friction-fit with pin holes through both gear hub and shaft, providing positive mechanical locking |
| Housing panels cracking/splintering when screwed | Switched to pre-drilled pilot holes; identified need for thicker material (5 mm plywood prone to splitting) |
| Partial gear misalignment during testing | Added precision bearing spacers and alignment tabs to the housing panels to enforce correct shaft positioning |
| Housing not rigid enough — frame flexing | Identified need for L-bracket bracing and cross-members; noted as improvement for future build |
| Prototype efficiency lower than steel analysis | Expected — aluminium shafts and acrylic gears have higher friction and surface roughness than assumed steel values |
| Exposed screw tips in assembly | Identified as safety issue; bolt-and-nut replacement recommended for future builds |

---

## Design Improvements

- **Housing bracing** — Add L-brackets and support beams connecting housing panels to the base plate to reduce flex and gear misalignment, directly improving efficiency.
- **Thicker housing material** — 5 mm plywood splintered during screw assembly. 10–12 mm plywood or aluminium plate would significantly improve structural reliability.
- **Bolts instead of screws** — Replace all self-tapping screws with M4 bolts and nuts to eliminate exposed sharp tips and improve clamp consistency.
- **Lubrication** — Adding grease to gear meshes and bearing surfaces would reduce friction losses and improve prototype efficiency toward the steel design's theoretical values.
- **Steel construction** — The full steel design (AISI 4140 shafts, AISI 1040 gears) is analytically verified for infinite shaft life and 2+ years of gear life. A steel build would be suitable for continuous industrial use.
- **Motor mount integration** — The current design has no dedicated motor mount. A machined motor bracket aligned with the input shaft coupling would improve drivetrain alignment and reduce vibration.
