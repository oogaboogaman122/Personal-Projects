import math
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets


#MECHANISM FUNCTIONS 
def grashof_gcrr(link_list):
    s = min(link_list)
    l = max(link_list)

    p_q = link_list.copy()
    p_q.remove(s)
    p_q.remove(l)
    p, q = p_q

    return (s + l < p + q) and (s == link_list[0])


def mobility_4bar():
    n = 4
    j1 = 4
    j2 = 0
    return 3 * (n - 1) - 2 * j1 - j2


theta_1 = 0


def k_vals(a, b, c, d):
    k1 = d / a
    k2 = d / c
    k3 = (a**2 - b**2 + c**2 + d**2) / (2 * a * c)
    return k1, k2, k3


def intermediate_vals(theta_2, k1, k2, k3):
    theta_2_rad = math.radians(theta_2)

    a_inter = math.cos(theta_2_rad) - k1 - k2 * math.cos(theta_2_rad) + k3
    b_inter = -2 * math.sin(theta_2_rad)
    c_inter = k1 - (k2 + 1) * math.cos(theta_2_rad) + k3

    return a_inter, b_inter, c_inter


def theta_4(a_inter, b_inter, c_inter):
    discriminant = b_inter**2 - 4 * a_inter * c_inter

    if discriminant < 0:
        return None, None

    if abs(a_inter) < 1e-12:
        return None, None

    root_term = math.sqrt(discriminant)

    theta_4_open = math.degrees(
        2 * math.atan((-b_inter - root_term) / (2 * a_inter))
    )
    theta_4_crossed = math.degrees(
        2 * math.atan((-b_inter + root_term) / (2 * a_inter))
    )

    return theta_4_open, theta_4_crossed


def theta_3(theta_2, theta_4_open, theta_4_crossed, a, b, c, d):
    if theta_4_open is None or theta_4_crossed is None:
        return None, None

    theta_2_rad = math.radians(theta_2)
    theta_4_open_rad = math.radians(theta_4_open)
    theta_4_crossed_rad = math.radians(theta_4_crossed)

    open_arg = (-a * math.sin(theta_2_rad) + c * math.sin(theta_4_open_rad)) / b
    crossed_arg = (-a * math.cos(theta_2_rad) + c * math.cos(theta_4_crossed_rad) + d) / b

    if not (-1 <= open_arg <= 1 and -1 <= crossed_arg <= 1):
        return None, None

    theta_3_open = math.degrees(math.asin(open_arg))
    theta_3_crossed = -math.degrees(math.acos(crossed_arg))

    return theta_3_open, theta_3_crossed

def transmission_angle(theta_4_open, theta_4_crossed, theta_3_open, theta_3_crossed):
    if None in (theta_4_open, theta_4_crossed, theta_3_open, theta_3_crossed):
        return None, None

    def compute_mu(theta4, theta3):
        alpha = abs(theta4 - theta3) % 360   # wrap to [0,360)

        if alpha > 180:
            alpha = 360 - alpha             # now in [0,180]

        mu = alpha if alpha <= 90 else 180 - alpha
        return mu

    transmission_angle_open = compute_mu(theta_4_open, theta_3_open)
    transmission_angle_crossed = compute_mu(theta_4_crossed, theta_3_crossed)

    return transmission_angle_open, transmission_angle_crossed


def leg(link_list, theta_2):
    # [driving, ground, coupler, output]
    a = link_list[0]
    d = link_list[1]
    b = link_list[2]
    c = link_list[3]

    grashof_status = grashof_gcrr(link_list)
    mobility = mobility_4bar()

    k1, k2, k3 = k_vals(a, b, c, d)
    a_inter, b_inter, c_inter = intermediate_vals(theta_2, k1, k2, k3)
    theta_4_open, theta_4_crossed = theta_4(a_inter, b_inter, c_inter)
    theta_3_open, theta_3_crossed = theta_3(theta_2, theta_4_open, theta_4_crossed, a, b, c, d)
    transmission_angle_open, transmission_angle_crossed = transmission_angle(
        theta_4_open, theta_4_crossed, theta_3_open, theta_3_crossed
    )

    return {
        "grashof": grashof_status,
        "mobility": mobility,
        "theta_4_open": theta_4_open,
        "theta_4_crossed": theta_4_crossed,
        "theta_3_open": theta_3_open,
        "theta_3_crossed": theta_3_crossed,
        "transmission_angle_open": transmission_angle_open,
        "transmission_angle_crossed": transmission_angle_crossed
          }   


def solve_front_leg(theta_2, front_leg):
    return leg(front_leg, theta_2)


def solve_back_leg(theta_2, back_leg):
    return leg(back_leg, theta_2)

def p_position_foot(link_list, theta_a, theta_b, B_to_P, link_index):
    link_length = link_list[link_index]

    theta_a_rad = math.radians(theta_a)
    theta_b_rad = math.radians(theta_b)

    Bx = link_length * math.cos(theta_a_rad)
    By = link_length * math.sin(theta_a_rad)

    px = Bx - B_to_P * math.cos(theta_b_rad)
    py = By - B_to_P * math.sin(theta_b_rad)

    return px, py

def get_current_foot_positions(theta_2, front_leg, back_leg, B_to_P):
    theta_2 = theta_2 % 360

    front_results = solve_front_leg(theta_2, front_leg)
    back_results = solve_back_leg(theta_2, back_leg)

    if front_results["theta_3_crossed"] is None or back_results["theta_4_crossed"] is None:
        return None

    f_px, f_py = p_position_foot(
        front_leg,
        theta_2,
        front_results["theta_3_crossed"],
        B_to_P,
        0
    )

    b_px, b_py = p_position_foot(
        back_leg,
        theta_1,
        back_results["theta_4_crossed"],
        B_to_P,
        1
    )

    return f_px, f_py, b_px, b_py

def joints_B_C_positions(a, b, thet_2, thet_3,):
    #trajectory of joint joint, A -> B, 
    thet_2_rad = math.radians(thet_2)
    thet_3_rad = math.radians(thet_3)

    bx = a*math.cos(thet_2_rad)
    by = a*math.sin(thet_2_rad)

    cx = bx + b*math.cos(thet_3_rad)
    cy = by + b*math.sin(thet_3_rad)

    return (bx, by), (cx, cy)

def get_leg_joint_positions(link_list, theta_2, theta_3_or_4):
    a = link_list[0]
    d = link_list[1]
    b = link_list[2]

    A = (0.0, 0.0)
    D = (d, 0.0)
    B, C = joints_B_C_positions(a, b, theta_2, theta_3_or_4)

    return A, B, C, D

def generate_trajectory(front_leg, back_leg, B_to_P, step=0.25):
    front_px_list = []
    front_py_list = []
    back_px_list = []
    back_py_list = []

    theta_2 = 360.0

    while theta_2 >= 0:
        front_results = solve_front_leg(theta_2, front_leg)
        back_results = solve_back_leg(theta_2, back_leg)

        if front_results["theta_3_crossed"] is not None and back_results["theta_4_crossed"] is not None:
            
            f_px, f_py = p_position_foot( front_leg, theta_2,front_results["theta_3_crossed"], B_to_P, 0)

            b_px, b_py = p_position_foot( back_leg, theta_1, back_results["theta_4_crossed"], B_to_P, 1)

            front_px_list.append(f_px)
            front_py_list.append(f_py)
            back_px_list.append(b_px)
            back_py_list.append(b_py)

        theta_2 -= step

    return front_px_list, front_py_list, back_px_list, back_py_list


def mechanism_valid(front_leg, back_leg):
    if mobility_4bar() != 1:
        return False, "Invalid mechanism: mobility ≠ 1"

    if not grashof_gcrr(front_leg):
        return False, "Front leg is not Grashof crank-rocker"

    if not grashof_gcrr(back_leg):
        return False, "Back leg is not Grashof crank-rocker"

    for theta_2 in range(0, 361):
        front_results = solve_front_leg(theta_2, front_leg)
        back_results = solve_back_leg(theta_2, back_leg)

        if front_results["theta_3_crossed"] is None or back_results["theta_4_crossed"] is None:
            return False, f"Invalid configuration at theta_2 = {theta_2}°"

    return True, "Mechanism valid"


#UI
class GaitApp(QtWidgets.QWidget):
    def update_link_segments(self, f_px, f_py, b_px, b_py):
        front_results = solve_front_leg(self.theta_2, self.front_leg)
        back_results = solve_back_leg(self.theta_2, self.back_leg)

        theta_3 = front_results["theta_3_crossed"]
        theta_4 = back_results["theta_3_crossed"]

        if theta_3 is None or theta_4 is None:
            self.front_AB.setData([], [])
            self.front_BC.setData([], [])
            self.front_CD.setData([], [])
            self.back_AB.setData([], [])
            self.back_BC.setData([], [])
            self.back_CD.setData([], [])
            return

        fA, fB, fC, fD = get_leg_joint_positions(self.front_leg, self.theta_2, theta_3)
        bA, bB, bC, bD = get_leg_joint_positions(self.back_leg, self.theta_2, theta_4)

        self.front_AB.setData([fA[0], fB[0]], [fA[1], fB[1]])
        self.front_BC.setData([fB[0], fC[0]], [fB[1], fC[1]])
        self.front_CD.setData([fC[0], fD[0]], [fC[1], fD[1]])

        self.back_AB.setData([bA[0], bB[0]], [bA[1], bB[1]])
        self.back_BC.setData([bB[0], bC[0]], [bB[1], bC[1]])
        self.back_CD.setData([bC[0], bD[0]], [bC[1], bD[1]])

        self.front_BP.setData([fB[0], f_px], [fB[1], f_py])
        self.back_DP.setData([bD[0], b_px], [bD[1], b_py])

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gait Cycle Tool")
        self.resize(1300, 800)

        self.theta_2 = 360.0
        self.angle_step = 1.5
        self.is_playing = True

        self.build_ui()
        self.load_default_values()
        self.update_mechanism()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(8)

    def build_ui(self):
        main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(main_layout)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle("Animated Gait Cycle")
        self.plot_widget.setLabel("bottom", "x")
        self.plot_widget.setLabel("left", "y")
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.addLegend()
        self.plot_widget.setAspectLocked(True)
        self.plot_widget.getViewBox().invertY(True)

        main_layout.addWidget(self.plot_widget, 3)

        control_widget = QtWidgets.QWidget()
        control_layout = QtWidgets.QVBoxLayout()
        control_widget.setLayout(control_layout)
        main_layout.addWidget(control_widget, 1)

        form = QtWidgets.QFormLayout()
        control_layout.addLayout(form)

        self.a_input = self.make_spinbox()
        self.d_input = self.make_spinbox()
        self.b_input = self.make_spinbox()
        self.c_input = self.make_spinbox()
        self.m_input = self.make_spinbox()
        self.l_input = self.make_spinbox()
        self.out_b_input = self.make_spinbox()
        self.bp_input = self.make_spinbox()

        form.addRow("Shared driving link a", self.a_input)
        form.addRow("Front ground link d", self.d_input)
        form.addRow("Front coupler link b", self.b_input)
        form.addRow("Front output link c", self.c_input)
        form.addRow("Back ground link m", self.m_input)
        form.addRow("Back coupler link l", self.l_input)
        form.addRow("Back output link b", self.out_b_input)
        form.addRow("Foot offset B_to_P", self.bp_input)

        self.speed_input = self.make_spinbox()
        self.speed_input.setDecimals(2)
        self.speed_input.setSingleStep(0.1)
        self.speed_input.setValue(1.5)
        form.addRow("Animation speed", self.speed_input)

        self.status_label = QtWidgets.QLabel("Ready")
        control_layout.addWidget(self.status_label)

        self.update_button = QtWidgets.QPushButton("Update")
        self.update_button.clicked.connect(self.update_mechanism)
        control_layout.addWidget(self.update_button)

        self.play_button = QtWidgets.QPushButton("Pause")
        self.play_button.clicked.connect(self.toggle_play)
        control_layout.addWidget(self.play_button)

        control_layout.addStretch()

        self.front_curve = self.plot_widget.plot([], [], pen=pg.mkPen(width=2), name="Front foot path")
        self.back_curve = self.plot_widget.plot([], [], pen=pg.mkPen(width=2, style=QtCore.Qt.PenStyle.DashLine), name="Back foot path")

        self.front_glow = pg.ScatterPlotItem(size=18, brush=pg.mkBrush(255, 255, 255, 60), pen=None, name="Front foot")
        self.front_dot = pg.ScatterPlotItem(size=8, brush=pg.mkBrush(255, 255, 255, 220), pen=None)

        self.back_glow = pg.ScatterPlotItem(size=18, brush=pg.mkBrush(255, 255, 255, 60), pen=None, name="Back foot")
        self.back_dot = pg.ScatterPlotItem(size=8, brush=pg.mkBrush(255, 255, 255, 220), pen=None)

        line_pen_front = pg.mkPen(width=3)
        line_pen_back = pg.mkPen(width=3, style=QtCore.Qt.PenStyle.DashLine)

        self.front_AB = self.plot_widget.plot([], [], pen=line_pen_front, name="Front AB")
        self.front_BC = self.plot_widget.plot([], [], pen=line_pen_front, name="Front BC")
        self.front_CD = self.plot_widget.plot([], [], pen=line_pen_front, name="Front CD")

        self.back_AB = self.plot_widget.plot([], [], pen=line_pen_back, name="Back AB")
        self.back_BC = self.plot_widget.plot([], [], pen=line_pen_back, name="Back BC")
        self.back_CD = self.plot_widget.plot([], [], pen=line_pen_back, name="Back CD")
        
        self.front_BP = self.plot_widget.plot([], [], pen=line_pen_front, name="Front BP")
        self.back_DP = self.plot_widget.plot([], [], pen=line_pen_back, name="Back DP")

        self.plot_widget.addItem(self.front_glow)
        self.plot_widget.addItem(self.front_dot)
        self.plot_widget.addItem(self.back_glow)
        self.plot_widget.addItem(self.back_dot)

    def make_spinbox(self):
        box = QtWidgets.QDoubleSpinBox()
        box.setRange(0.001, 1000000.0)
        box.setDecimals(3)
        box.setSingleStep(0.1)
        return box

    def load_default_values(self):
        self.a_input.setValue(10.0)
        self.d_input.setValue(20.0)
        self.b_input.setValue(25.0)
        self.c_input.setValue(18.0)
        self.m_input.setValue(22.0)
        self.l_input.setValue(24.0)
        self.out_b_input.setValue(17.0)
        self.bp_input.setValue(8.0)

    def read_inputs(self):
        a = self.a_input.value()
        d = self.d_input.value()
        b = self.b_input.value()
        c = self.c_input.value()
        m = self.m_input.value()
        l = self.l_input.value()
        out_b = self.out_b_input.value()
        B_to_P = self.bp_input.value()
        self.angle_step = self.speed_input.value()

        front_leg = [a, d, b, c]
        back_leg = [a, m, l, out_b]

        return front_leg, back_leg, B_to_P

    def update_mechanism(self):
        front_leg, back_leg, B_to_P = self.read_inputs()

        valid, message = mechanism_valid(front_leg, back_leg)
        self.status_label.setText(message)

        if not valid:
            self.front_curve.setData([], [])
            self.back_curve.setData([], [])
            self.front_glow.setData([], [])
            self.front_dot.setData([], [])
            self.back_glow.setData([], [])
            self.back_dot.setData([], [])
            self.front_AB.setData([], [])
            self.front_BC.setData([], [])
            self.front_CD.setData([], [])
            self.back_AB.setData([], [])
            self.back_BC.setData([], [])
            self.back_CD.setData([], [])
            return

        self.front_leg = front_leg
        self.back_leg = back_leg
        self.B_to_P = B_to_P

        front_px_list, front_py_list, back_px_list, back_py_list = generate_trajectory(
            self.front_leg,
            self.back_leg,
            self.B_to_P,
            step=0.25
        )

        self.front_curve.setData(front_px_list, front_py_list)
        self.back_curve.setData(back_px_list, back_py_list)

        current = get_current_foot_positions(
            self.theta_2,
            self.front_leg,
            self.back_leg,
            self.B_to_P
        )

        if current is None:
            self.front_glow.setData([], [])
            self.front_dot.setData([], [])
            self.back_glow.setData([], [])
            self.back_dot.setData([], [])
            return

        f_px, f_py, b_px, b_py = current

        self.front_glow.setData([f_px], [f_py])
        self.front_dot.setData([f_px], [f_py])
        self.back_glow.setData([b_px], [b_py])
        self.back_dot.setData([b_px], [b_py])
        self.update_link_segments(f_px, f_py, b_px, b_py)
        front_results = solve_front_leg(self.theta_2, self.front_leg)
        back_results = solve_back_leg(self.theta_2, self.back_leg)

        mu_front = front_results["transmission_angle_crossed"]
        mu_back = back_results["transmission_angle_crossed"]
        self.plot_widget.setTitle(
            f"Animated Gait Cycle | theta_2 = {self.theta_2:.1f}° | "
            f"mu_front = {mu_front:.1f}° | mu_back = {mu_back:.1f}°"
        )

    def animate(self):
        if not self.is_playing:
            return

        if not hasattr(self, "front_leg"):
            return

        self.theta_2 = (self.theta_2 - self.angle_step) % 360

        current = get_current_foot_positions(
            self.theta_2,
            self.front_leg,
            self.back_leg,
            self.B_to_P
        )

        if current is None:
            return

        f_px, f_py, b_px, b_py = current

        self.front_glow.setData([f_px], [f_py])
        self.front_dot.setData([f_px], [f_py])
        self.back_glow.setData([b_px], [b_py])
        self.back_dot.setData([b_px], [b_py])
        self.update_link_segments(f_px, f_py, b_px, b_py)

        front_results = solve_front_leg(self.theta_2, self.front_leg)
        back_results = solve_back_leg(self.theta_2, self.back_leg)

        mu_front = front_results["transmission_angle_crossed"]
        mu_back = back_results["transmission_angle_crossed"]
        self.plot_widget.setTitle(
            f"Animated Gait Cycle | theta_2 = {self.theta_2:.1f}° | "
            f"mu_front = {mu_front:.1f}° | mu_back = {mu_back:.1f}°"
        )

    def toggle_play(self):
        self.is_playing = not self.is_playing

        if self.is_playing:
            self.play_button.setText("Pause")
        else:
            self.play_button.setText("Play")

def main():
    app = pg.mkQApp("Gait Cycle Tool")
    window = GaitApp()
    window.show()
    pg.exec()


main()