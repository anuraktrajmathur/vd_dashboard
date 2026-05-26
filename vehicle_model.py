# ============================================================
# VEHICLE DYNAMICS & YAW STABILITY CONTROL MODEL
# ============================================================
#
# This script implements a nonlinear 2-DOF vehicle dynamics
# model with Pacejka tire dynamics and an Electronic Stability
# Control (ESC) / Yaw Stability Control (YSC) system.
#
# The simulation evaluates vehicle handling behaviour under
# various steering inputs, road friction conditions, and ESC
# intervention strategies while tracking yaw rate, sideslip,
# tire forces, and stability characteristics in real time.
#
# Developed by Anurakt Raj Mathur, M.Sc.
# ============================================================


# ============================================================
# Import Libraries
# ============================================================

import numpy as np

# ============================================================
# Vehicle Parameters
# ============================================================

m = 1150.0      # Mass [kg]
g = 9.81        # Acceleration due to gravity

L = 2.66        # Wheelbase
a = 1.06        # Distance of CG from front axle
b = L - a       # Distace of CG from rear axle

J = 1850.0      # Yaw moment of inertia [kg.m^2]

# Understeer tuning parameter
Ku = 0.003

# Static normal load

Fz1 = m * g * b / L # Front [N]
Fz2 = m * g * a / L # Rear [N]

# ============================================================
# Pacejka Tire Parameters
# ============================================================

mu1 = mu2 = 0.9

C1 = C2 = 1.19

Fz0 = 8000.0

dFz1 = (Fz1 - Fz0) / Fz0
dFz2 = (Fz2 - Fz0) / Fz0

D1 = mu1 * (-0.145 * dFz1 + 0.99) * Fz1
D2 = mu2 * (-0.145 * dFz2 + 0.99) * Fz2

K1 = 14.95 * Fz0 * np.sin(
    2 * np.arctan(Fz1 / (2.13 * Fz0))
)

K2 = Fz2 * K1 / (Fz1 - 0.03 * K1)

E1 = -1.003 - 0.537 * dFz1
E2 = -1.003 - 0.537 * dFz2

B1 = K1 / (C1 * D1)
B2 = K2 / (C2 * D2)

# ============================================================
# Pacejka Tire Model
# ============================================================

def pacejka(alpha, B, C, D, E):

    return D * np.sin(
        C * np.arctan(
            B * alpha
            - E * (
                B * alpha
                - np.arctan(B * alpha)
            )
        )
    )

# ============================================================
# Reference Yaw Rate Model
# ============================================================

def reference_yaw_rate(delta, Vx, mu_scale):

    # Understeer reference model
    r_ref = (
        Vx / (L + Ku * Vx**2)
    ) * delta

    # Physical yaw-rate saturation
    r_ref_max = (
        0.8 * mu_scale * g / Vx
    )

    r_ref = np.clip(
        r_ref,
        -r_ref_max,
        r_ref_max
    )

    return r_ref

# ============================================================
# Simulation
# ============================================================

def run_simulation(

    steering_deg=4,
    vehicle_speed=80,

    t_span=(0, 10),

    mu_scale=1.0,

    steering_type="ramp",

    ysc_on=True,

    K_r=200,
    K_beta=500

):

    # Time
    #     
    t_eval = np.linspace(
        t_span[0],
        t_span[1],
        int(200 * t_span[1])
    )

    dt = t_eval[1] - t_eval[0]

    # Vehicle Speed
    
    Vx = max(vehicle_speed / 3.6, 0.1)

    # Speed scheduling factor
    speed_factor = Vx / 20.0

    # Steering input

    def delta_func(t):

        if steering_type == "step":

            return (
                np.deg2rad(steering_deg)
                if t > 1 else 0
            )

        elif steering_type == "sine":

            return (
                np.deg2rad(steering_deg)
                * np.sin(2 * np.pi * 0.5 * t)
            )

        else:

            # Ramp steering

            if t < 1:

                return 0

            elif t < 1.2:

                return (
                    np.deg2rad(steering_deg)
                    * (t - 1) / 0.2
                )

            else:

                return np.deg2rad(
                    steering_deg
                )
            
    # States

    v = 0.0
    r = 0.0

    x = 0.0
    y = 0.0
    psi = 0.0

    # Previous yaw moment
    Mz_prev = 0.0

    # Logging

    v_list = []
    r_list = []

    beta_list = []

    alpha_f_list = []
    alpha_r_list = []

    Fyf_list = []
    Fyr_list = []

    delta_list = []

    r_ref_list = []

    Mz_list = []

    x_list = []
    y_list = []
    psi_list = []

    esc_gain_list = []

    # ========================================================
    # Main simulation loop
    # ========================================================

    for t in t_eval:

        # Steering Input
     
        delta = delta_func(t)

        # Reference Yaw Rate

        r_ref = reference_yaw_rate(
            delta,
            Vx,
            mu_scale
        )

        # Vehicle States

        beta = np.arctan2(v, Vx)

        # Slip angles
  
        alpha_f = (
            delta
            - (v + a * r) / Vx
        )

        alpha_r = (
            -(v - b * r) / Vx
        )

        # ESC CONTROLLER

        if ysc_on:

            # ------------------------------------------------
            # Predictive ESC Threshold
            # ------------------------------------------------

            rear_slip_threshold = np.deg2rad(7)

            # ------------------------------------------------
            # Gain Scheduling
            # ------------------------------------------------

            K_r_eff = (
                K_r /
                (1 + 4.0 * speed_factor)
            )

            K_beta_eff = (
                K_beta *
                (1 + 2.0 * speed_factor)
            )

            if abs(alpha_r) > np.deg2rad(4):

                K_beta_eff *= 1.8

            # ------------------------------------------------
            # Yaw Error
            # ------------------------------------------------

            yaw_error = r_ref - r

            # ------------------------------------------------
            # ESC Activation Thresholds
            # ------------------------------------------------

            beta_low = np.deg2rad(1.0)
            beta_high = np.deg2rad(3.0)

            yaw_low = np.deg2rad(2.0)
            yaw_high = np.deg2rad(5.0)

            # ------------------------------------------------
            # Nonlinear Beta Amplification
            # ------------------------------------------------

            beta_term = (

                K_beta_eff

                * beta

                * (
                    1 + 8 * abs(beta)
                )
            )

            # ------------------------------------------------
            # Raw Controller
            # ------------------------------------------------

            Mz_cmd = (

                K_r_eff * yaw_error

                + beta_term
            )

            # ESC ACTIVATION LOGIC
   
            # Normal driving
            if (
                abs(beta) < beta_low
                and abs(yaw_error) < yaw_low
            ):

                intervention_gain = 0.0

            # Mild instability
            elif (
                abs(beta) < beta_high
                and abs(yaw_error) < yaw_high
            ):

                intervention_gain = 0.5

            # Severe instability
            else:

                intervention_gain = 1.0

            # PREDICTIVE ESC ESCALATION

            if abs(alpha_r) > rear_slip_threshold:

                intervention_gain = max(
                    intervention_gain,
                    0.75
                )

            # ------------------------------------------------
            # Apply Intervention
            # ------------------------------------------------

            Mz = (
                intervention_gain
                * Mz_cmd
            )

            # ACTUATOR SATURATION

            Mz = np.clip(
                Mz,
                -2000,
                2000
            )

            # YAW MOMENT RATE LIMITER
    
            Mz_rate_limit = 4000 * dt

            Mz = np.clip(

                Mz,

                Mz_prev - Mz_rate_limit,

                Mz_prev + Mz_rate_limit
            )

            # FINAL SAFETY SATURATION

            Mz = np.clip(
                Mz,
                -500,
                500
            )

            # Update actuator memory
            Mz_prev = Mz

        else:

            Mz = 0.0

            intervention_gain = 0.0

            Mz_prev = 0.0

        # ====================================================
        # TIRE FORCES
        # ====================================================

        Fyf = (
            mu_scale *
            pacejka(
                alpha_f,
                B1, C1, D1, E1
            )
        )

        Fyr = (
            mu_scale *
            pacejka(
                alpha_r,
                B2, C2, D2, E2
            )
        )

        # ====================================================
        # VEHICLE DYNAMICS
        # ====================================================

        v_dot = (
            (Fyf + Fyr) / m
            - Vx * r
        )

        r_dot = (
            (
                a * Fyf
                - b * Fyr
                + Mz
            ) / J
        )

        # ----------------------------------------------------
        # Integrate
        # ----------------------------------------------------

        v += v_dot * dt
        r += r_dot * dt
        psi += r * dt

        x_dot = (
            Vx * np.cos(psi)
            - v * np.sin(psi)
        )

        y_dot = (
            Vx * np.sin(psi)
            + v * np.cos(psi)
        )

        x += x_dot * dt
        y += y_dot * dt

        # ====================================================
        # LOGGING
        # ====================================================

        v_list.append(v)

        r_list.append(r)

        beta_list.append(
            np.rad2deg(beta)
        )

        alpha_f_list.append(
            np.rad2deg(alpha_f)
        )

        alpha_r_list.append(
            np.rad2deg(alpha_r)
        )

        Fyf_list.append(Fyf)

        Fyr_list.append(Fyr)

        delta_list.append(
            np.rad2deg(delta)
        )

        r_ref_list.append(
            np.rad2deg(r_ref)
        )

        Mz_list.append(Mz)

        x_list.append(x)
        y_list.append(y)
        psi_list.append(
            np.rad2deg(psi)
        )

        esc_gain_list.append(
            intervention_gain
        )

    # ========================================================
    # OUTPUT
    # ========================================================

    return {

        "t":
            t_eval,

        "yaw_rate":
            np.rad2deg(r_list),

        "yaw_rate_ref":
            r_ref_list,

        "slip_angle":
            beta_list,

        "lat_accel":
            (
                np.gradient(v_list, t_eval)
                + Vx * np.array(r_list)
            ) / g,

        "alpha_f":
            alpha_f_list,

        "alpha_r":
            alpha_r_list,

        "Fyf":
            Fyf_list,

        "Fyr":
            Fyr_list,

        "Fz1":
            Fz1,

        "Fz2":
            Fz2,

        "delta":
            delta_list,

        "Mz":
            Mz_list,

        "x":
            x_list,
        
        "y":
            y_list,

        "psi":
            psi_list,

        "esc_gain":
            esc_gain_list
    }

# ============================================================
# STABILITY CLASSIFICATION
# ============================================================

def classify_stability(beta_history):

    max_beta = np.max(
        np.abs(beta_history)
    )

    # Stable
    if max_beta < 4:

        return 0

    # Marginal
    elif max_beta < 8:

        return 1

    # Unstable
    else:

        return 2