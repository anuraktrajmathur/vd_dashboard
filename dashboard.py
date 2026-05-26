# ============================================================
# VEHICLE DYNAMICS DASHBOARD
# ============================================================
#
# This Streamlit dashboard provides an interactive visualization platform for analyzing vehicle lateral dynamics, tire behaviour,
# and Electronic Stability Control (ESC) performance.

# The application integrates a nonlinear vehicle model with real-time simulation, allowing users to study yaw response,
# sideslip dynamics, tire force generation, stability envelopes, and controller intervention under varying driving conditions.
#
# Features include:
# - Real-time yaw stability analysis
# - Pacejka tire force visualization
# - ESC / YSC controller monitoring
# - Handling and stability assessment
# - Interactive scenario configuration
# - Dynamic vehicle response visualization
#
# REQUIREMENTS:
# - vehicle_model.py must be present in the same directory
# - Required libraries: streamlit, numpy, matplotlib, pandas
#
# RUN COMMAND:
# streamlit run dashboard.py
#
# Developed by Anurakt Raj Mathur, M.Sc.
# ============================================================

# ============================================================
# Import Libraries
# ============================================================

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import streamlit.components.v1 as components
import base64

from vehicle_model import (
    run_simulation,
    classify_stability,
    L,
    Fz1,
    Fz2
)

# ============================================================
# Page Configuration
# ============================================================
st.markdown(
    '<div id="top"></div>', unsafe_allow_html=True
)

st.set_page_config(
    layout="wide"
)

st.markdown(
    """
    <style>

    .block-container {

        padding-top: 2rem;

        padding-bottom: 1rem;
    }

    </style>
    """,

    unsafe_allow_html=True
)

# ========================================================
# Session State
# ========================================================

if "dashboard_entered" not in st.session_state:
    st.session_state.dashboard_entered = False

# ========================================================
# Welcome Page
# ========================================================

if not st.session_state.dashboard_entered:
    with open("assets/welcome_page.png", "rb") as f:

        welcome_base64 = base64.b64encode(
            f.read()
        ).decode()

    # ----------------------------------------------------
    # Page Styling
    # ----------------------------------------------------

    st.markdown(

        f"""
        <style>

        .stApp {{

            margin: 0;
            padding: 0;

            overflow: hidden;

            background-color: #01040D;
        }}

        [data-testid="stAppViewContainer"] {{

            background-color: #01040D;
        }}

        header {{

            visibility: hidden;
        }}

        .main .block-container {{

            padding: 0rem;

            max-width: 100%;
        }}

        .welcome-bg {{

            position: fixed;

            inset: 0;

            width: 100vw;
            height: 100vh;

            z-index: 1;

            background-image:
            url("data:image/png;base64,{welcome_base64}");

            background-size: 88%;

            background-position: center center;

            background-repeat: no-repeat;

            background-color: #01040D;

            filter: brightness(0.92);
            
            animation: fadeIn 1.2s ease-out;
        }}

        </style>

        <div class="welcome-bg"></div>

        """,

        unsafe_allow_html=True
    )

    # ----------------------------------------------------
    # Enter Dashboard Button
    # ----------------------------------------------------

    st.markdown(

        """
        <style>

        /* Button container */
        div.stButton {

            position: fixed;

            bottom: 7%;

            left: 73%;

            z-index: 1000002;
        }

        /* Actual button */
        div.stButton > button {

            width: 360px;

            height: 68px;

            border-radius: 999px;

            background:
            linear-gradient(
                180deg,
                rgba(5, 20, 38, 0.96),
                rgba(1, 6, 18, 0.98)
            ) !important;

            border: 1px solid rgba(59, 130, 246, 0.35) !important;

            color: #dbeafe !important;

            font-size: 18px !important;

            font-weight: 500 !important;

            letter-spacing: 2px !important;

            box-shadow:
                0 0 18px rgba(59,130,246,0.12);

            transition:
                all 0.25s ease !important;
        }

        div.stButton > button:hover {

            border: 1px solid rgba(59,130,246,0.8) !important;

            color: white !important;

            transform: translateY(-2px);

            box-shadow:
                0 0 26px rgba(59,130,246,0.22);
        }

        </style>
        """,

        unsafe_allow_html=True
    )

    enter_dashboard = st.button(

        "ENTER DASHBOARD  →",

        key="enter_dashboard"
    )

    if enter_dashboard:

        st.session_state.dashboard_entered = True

        st.rerun()

    st.stop()

# ============================================================
# Session State Defaults
# ============================================================

DEFAULTS = {

    "ysc_on": True,

    "K_r": 200,

    "K_beta": 500
}

for key, value in DEFAULTS.items():

    if key not in st.session_state:

        st.session_state[key] = value

# ============================================================
# ESC Settings Dialog Box
# ============================================================

@st.dialog("ESC Controller Settings")

def esc_settings_dialog():

    # --------------------------------------------------------
    # Temporary dialog variables
    # --------------------------------------------------------

    temp_ysc = st.toggle(

        "Enable ESC",

        value=st.session_state.ysc_on
    )

    temp_K_r = st.slider(

        "Yaw Gain (K_r)",

        0,
        1000,

        value=st.session_state.K_r,

        step=10
    )

    temp_K_beta = st.slider(

        "Sideslip Gain (K_beta)",

        0,
        2000,

        value=st.session_state.K_beta,

        step=10
    )

    st.markdown("---")

    # --------------------------------------------------------
    # Buttons
    # --------------------------------------------------------

    b1, b2, b3 = st.columns(3)

    # APPLY
    with b1:

        if st.button(
            "Apply",
            use_container_width=True
        ):

            st.session_state.ysc_on = temp_ysc

            st.session_state.K_r = temp_K_r

            st.session_state.K_beta = temp_K_beta

            st.rerun()

    # OK
    with b2:

        if st.button(
            "OK",
            use_container_width=True
        ):

            st.session_state.ysc_on = temp_ysc

            st.session_state.K_r = temp_K_r

            st.session_state.K_beta = temp_K_beta

            st.rerun()

    # CANCEL
    with b3:

        if st.button(
            "Cancel",
            use_container_width=True
        ):

            st.rerun()

# ============================================================
# Global CSS
# ============================================================
st.markdown(
    """
    <style>

    [data-testid="stSidebar"] [data-testid="stImage"] {

        text-align: center;
        display: block;
    }

    [data-testid="stSidebar"] [data-testid="stImage"] img {

        margin-left: auto;
        margin-right: auto;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>

    .status-banner {

        border-radius: 12px;

        padding: 10px;

        text-align: center;

        font-size: 22px;

        font-weight: 700;

        margin-top: 10px;

        margin-bottom: 18px;
    }

    .stable {

        background-color: #d1fae5;

        color: #065f46;

        border: 1px solid #6ee7b7;
    }

    .marginal {

        background-color: #fef3c7;

        color: #92400e;

        border: 1px solid #fcd34d;
    }

    .unstable {

        background-color: #fee2e2;

        color: #991b1b;

        border: 1px solid #fca5a5;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>

    /* =====================================================
       TAB TEXT
    ===================================================== */

    button[data-baseweb="tab"] p {

        font-size: 24px !important;

        font-weight: 600 !important;

        color: #374151 !important;
    }

    /* Active tab */

    button[data-baseweb="tab"][aria-selected="true"] p {

        color: #111827 !important;

        font-weight: 700 !important;
    }

    /* Tab spacing */

    button[data-baseweb="tab"] {

        padding-top: 14px !important;

        padding-bottom: 14px !important;

        padding-left: 22px !important;

        padding-right: 22px !important;

        margin-right: 16px !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# Sidebar
# ============================================================

# ------------------------------------------------------------
# Sidebar Header
# ------------------------------------------------------------

with st.sidebar:

    st.image(
        "assets/car_icon.png",
        width=250
    )

# ------------------------------------------------------------
# Driver Inputs
# ------------------------------------------------------------

st.sidebar.header(
    "Driver Inputs"
)

vehicle_speed = st.sidebar.slider(
    "Speed (km/h)",
    10,
    180,
    80
)

steering_deg = st.sidebar.slider(
    "Steering Angle (°)",
    1,
    10,
    4
)

steering_type = st.sidebar.selectbox(
    "Steering Input",
    ["ramp", "step", "sine"]
)

# ------------------------------------------------------------
# Driving Surface
# ------------------------------------------------------------

st.sidebar.header(
    "Driving Surface"
)

# ------------------------------------------------------------
# Surface Presets
# ------------------------------------------------------------

surface_options = {

    "🛣️ Dry Asphalt": 0.90,

    "🌧️ Wet Asphalt": 0.65,

    "🪨 Gravel": 0.55,

    "❄️ Snow": 0.30,

    "🧊 Ice": 0.10,

    "🏁 Track Surface": 1.10,

    "⚙️ Custom": None
}

selected_surface = st.sidebar.selectbox(

    "",

    list(surface_options.keys())
)

# ------------------------------------------------------------
# μ VALUE
# ------------------------------------------------------------

if selected_surface == "⚙️ Custom":

    mu = st.sidebar.number_input(

        "Custom μ",

        min_value=0.05,

        max_value=1.50,

        value=0.90,

        step=0.01,

        format="%.2f"
    )

else:

    mu = surface_options[selected_surface]

# ------------------------------------------------------------
# μ Display
# ------------------------------------------------------------

st.sidebar.caption(

    f"Current Friction Coefficient: μ = {mu:.2f}"
)

# ------------------------------------------------------------
# Grip Classification
# ------------------------------------------------------------

if mu >= 1.00:

    grip_text = "VERY HIGH GRIP"

    grip_bg = "#d1fae5"

    grip_color = "#065f46"

elif mu >= 0.80:

    grip_text = "HIGH GRIP"

    grip_bg = "#d1fae5"

    grip_color = "#065f46"

elif mu >= 0.60:

    grip_text = "MEDIUM GRIP"

    grip_bg = "#dbeafe"

    grip_color = "#1e3a8a"

elif mu >= 0.40:

    grip_text = "LOW GRIP"

    grip_bg = "#fef3c7"

    grip_color = "#92400e"

elif mu >= 0.20:

    grip_text = "VERY LOW GRIP"

    grip_bg = "#fde68a"

    grip_color = "#78350f"

else:

    grip_text = "EXTREMELY LOW GRIP"

    grip_bg = "#fee2e2"

    grip_color = "#991b1b"

# ------------------------------------------------------------
# Grip Pill Banner
# ------------------------------------------------------------

st.sidebar.markdown(

    f"""
    <div style="
        background-color: {grip_bg};
        color: {grip_color};
        padding: 10px 14px;
        border-radius: 999px;
        text-align: center;
        font-weight: 600;
        margin-top: 10px;
        margin-bottom: 8px;
        font-size: 14px;
    ">
        {grip_text}
    </div>
    """,

    unsafe_allow_html=True
)

# ------------------------------------------------------------
# Simulation
# ------------------------------------------------------------

st.sidebar.header(
    "Simulation"
)

sim_time = st.sidebar.slider(
    "Simulation Time (s)",
    3,
    30,
    10
)

compare_mode = st.sidebar.checkbox(
    "Compare ESC ON/OFF",
    value=False
)

sweep_mode = st.sidebar.checkbox(
    "Stability Envelope Sweep",
    value=False
)

# ------------------------------------------------------------
# ESC SETTINGS BUTTON
# ------------------------------------------------------------

if st.sidebar.button(
    "ESC Controller Settings ⚙️",
    use_container_width=True
):

    esc_settings_dialog()

# ============================================================
# RUN SIMULATION
# ============================================================

res = run_simulation(

    steering_deg=steering_deg,

    vehicle_speed=vehicle_speed,

    t_span=(0, sim_time),

    mu_scale=mu,

    steering_type=steering_type,

    ysc_on=st.session_state.ysc_on,

    K_r=st.session_state.K_r,

    K_beta=st.session_state.K_beta
)

# ============================================================
# Stability Envelope Sweep
# ============================================================

if sweep_mode:

    speed_range = np.arange(
        40,
        241,
        20
    )

    steer_range = np.arange(
        1,
        11,
        1
    )

    stability_map = np.full(
        (
            len(steer_range),
            len(speed_range)
        ),
        2
    )


    for i, steer in enumerate(
        steer_range
    ):

        for j, speed in enumerate(
            speed_range
        ):

            sweep_res = run_simulation(

                steering_deg=steer,

                vehicle_speed=speed,

                t_span=(0, sim_time),

                mu_scale=mu,

                steering_type="ramp",

                ysc_on=st.session_state.ysc_on,

                K_r=st.session_state.K_r,

                K_beta=st.session_state.K_beta
            )

            stability_map[i, j] = (
                classify_stability(
                    sweep_res["slip_angle"]
                )
            )

# ============================================================
# ESC Comparison Mode
# ============================================================

if compare_mode:

    # --------------------------------------------------------
    # ESC ON
    # --------------------------------------------------------

    res_on = run_simulation(

        steering_deg=steering_deg,

        vehicle_speed=vehicle_speed,

        t_span=(0, sim_time),

        mu_scale=mu,

        steering_type=steering_type,

        ysc_on=True,

        K_r=st.session_state.K_r,

        K_beta=st.session_state.K_beta
    )

    # --------------------------------------------------------
    # ESC OFF
    # --------------------------------------------------------

    res_off = run_simulation(

        steering_deg=steering_deg,

        vehicle_speed=vehicle_speed,

        t_span=(0, sim_time),

        mu_scale=mu,

        steering_type=steering_type,

        ysc_on=False,

        K_r=st.session_state.K_r,

        K_beta=st.session_state.K_beta
    )

    # --------------------------------------------------------
    # Stability Metrics
    # --------------------------------------------------------

    beta_peak_off = np.max(
        np.abs(
            res_off["slip_angle"]
        )
    )

    beta_peak_on = np.max(
        np.abs(
            res_on["slip_angle"]
        )
    )

    beta_reduction = (

        100 *

        (
            beta_peak_off
            - beta_peak_on
        )

        / max(beta_peak_off, 1e-6)
    )

    yaw_peak_off = np.max(
        np.abs(
            res_off["yaw_rate"]
        )
    )

    yaw_peak_on = np.max(
        np.abs(
            res_on["yaw_rate"]
        )
    )

    yaw_reduction = (

        100 *

        (
            yaw_peak_off
            - yaw_peak_on
        )

        / max(yaw_peak_off, 1e-6)
    )

# ============================================================
# Data
# ============================================================

t = np.array(
    res["t"]
)

yaw_rate = np.array(
    res["yaw_rate"]
)

yaw_rate_ref = np.array(
    res["yaw_rate_ref"]
)

beta = np.array(
    res["slip_angle"]
)

lat_accel = np.array(
    res["lat_accel"]
)

alpha_f = np.array(
    res["alpha_f"]
)

alpha_r = np.array(
    res["alpha_r"]
)

Fyf = np.array(
    res["Fyf"]
)

Fyr = np.array(
    res["Fyr"]
)

Mz = np.array(
    res["Mz"]
)

esc_gain = np.array(
    res["esc_gain"]
)

yaw_error = (
    yaw_rate_ref
    - yaw_rate
)

# ============================================================
# ESC Intervetion Statistics
# ============================================================

active_samples = np.sum(
    esc_gain > 0
)

mild_samples = np.sum(
    (esc_gain > 0)
    & (esc_gain < 1.0)
)

aggressive_samples = np.sum(
    esc_gain >= 1.0
)

esc_active_percent = (
    100 * active_samples / len(t)
)

mild_percent = (
    100 * mild_samples / len(t)
)

aggressive_percent = (
    100 * aggressive_samples / len(t)
)

max_yaw_moment = np.max(
    np.abs(Mz)
)

rms_yaw_error = np.sqrt(
    np.mean(
        yaw_error**2
    )
)

esc_energy = np.trapz(
    np.abs(Mz),
    t
)

# ============================================================
# KPI Styling
# ============================================================

st.markdown(
    """
    <style>

    div[data-testid="stMetric"] {

        background-color: white;

        border: 1px solid #d8dee9;

        padding: 16px;

        border-radius: 14px;

        box-shadow: 0 2px 6px rgba(0,0,0,0.04);

        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# Dashboard Title
# ============================================================

st.markdown(
    """
    <h1 style='
        text-align: center;
        font-size: 42px;
        margin-top: -70px;
        margin-bottom: 0px;
        color: #1f2937;
        font-weight: 800;
    '>
        Simulation Overview
    </h1>

    """,
    unsafe_allow_html=True
)

# ============================================================
# KPIs
# ============================================================

# ------------------------------------------------------------
# First Row
# ------------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Maximum Yaw Rate",
    f"{np.max(np.abs(yaw_rate)):.2f}°/s"
)

c2.metric(
    "Maximum Sideslip Angle (β)",
    f"{np.max(np.abs(beta)):.2f}°"
)

c3.metric(
    "Maximum Lateral Acceleration",
    f"{np.max(np.abs(lat_accel)):.2f} g"
)

c4.metric(
    "Maximum Yaw Moment",
    f"{np.max(np.abs(Mz)):.0f} Nm"
)

# ------------------------------------------------------------
# Second Row
# ------------------------------------------------------------

c5, c6, c7, c8 = st.columns(4)

c5.metric(
    "Peak Front Slip",
    f"{np.max(np.abs(alpha_f)):.2f}°"
)

c6.metric(
    "Peak Rear Slip",
    f"{np.max(np.abs(alpha_r)):.2f}°"
)

c7.metric(
    "Tracking Error",
    f"{np.max(np.abs(yaw_error)):.2f}°/s"
)

# ------------------------------------------------------------
# ESC Activity Status
# ------------------------------------------------------------

if aggressive_percent > 10:

    esc_status = "Aggressive"

elif esc_active_percent > 5:

    esc_status = "Mild"

else:

    esc_status = "Inactive"

c8.metric(
    "ESC Activity",
    esc_status
)

# ============================================================
# ESC Performance Metrics
# ============================================================

st.markdown("---")

with st.expander(
    "ESC Intervention Statistics",
    expanded=False
):

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "ESC Engagement",
        f"{esc_active_percent:.1f}%"
    )

    m2.metric(
        "Mild ESC",
        f"{mild_percent:.1f}%"
    )

    m3.metric(
        "Aggressive ESC",
        f"{aggressive_percent:.1f}%"
    )

    m4.metric(
        "Maximum Yaw Moment",
        f"{max_yaw_moment:.0f} Nm"
    )

    m5, m6 = st.columns(2)

    m5.metric(
        "RMS Yaw Error",
        f"{rms_yaw_error:.2f}°/s"
    )

    m6.metric(
        "Control Effort",
        f"{esc_energy:.0f} Nm·s"
    )

# ============================================================
# Stability Classification
# ============================================================

peak_beta = np.max(
    np.abs(beta)
)

rms_yaw_error = np.sqrt(
    np.mean(yaw_error**2)
)

rms_alpha_r = np.sqrt(
    np.mean(alpha_r**2)
)

rms_mz = np.sqrt(
    np.mean(Mz**2)
)

# ------------------------------------------------------------
# Stable
# ------------------------------------------------------------

if (

    peak_beta < 5

    and rms_yaw_error < 7

    and rms_alpha_r < 5

    and rms_mz < 300
):

    stability_state = "Stable"

# ------------------------------------------------------------
# Marginal
# ------------------------------------------------------------

elif (

    peak_beta < 7

    and rms_yaw_error < 11

    and rms_alpha_r < 7
):

    stability_state = "Marginal"

# ------------------------------------------------------------
# Unstable
# ------------------------------------------------------------

else:

    stability_state = "Unstable"

# ============================================================
# Stability Status Banner
# ============================================================

if stability_state == "Stable":

    status_class = "stable"

    banner_text = "VEHICLE STABLE"

elif stability_state == "Marginal":

    status_class = "marginal"

    banner_text = "VEHICLE AT LIMIT"

else:

    status_class = "unstable"

    banner_text = "LOSS OF STABILITY"

# ------------------------------------------------------------
# ESC Status
# ------------------------------------------------------------

if st.session_state.ysc_on:

    esc_text = "ESC ACTIVE"

else:

    esc_text = "ESC DISABLED"

# ------------------------------------------------------------
# Final Banner
# ------------------------------------------------------------

st.markdown(

    f"""
    <div class="status-banner {status_class}">
        {banner_text}
        &nbsp;&nbsp;•&nbsp;&nbsp;
        {esc_text}
    </div>
    """,

    unsafe_allow_html=True
)

# ============================================================
# Tabs
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([

    "Vehicle Response",

    "Tire Dynamics",
    
    "Handling Characteristics",

    "Controller",

    "Stability",

    "Stability Envelope"
])

# ============================================================
# Response Tab
# ============================================================

with tab1:

    fig, axs = plt.subplots(
        2,
        2,
        figsize=(14, 10)
    )

    # --------------------------------------------------------
    # Yaw Rate
    # --------------------------------------------------------

    axs[0,0].plot(
        t,
        yaw_rate,
        linewidth=2.5,
        label="Actual"
    )

    axs[0,0].plot(
        t,
        yaw_rate_ref,
        linestyle="--",
        linewidth=1.8,
        label="Reference"
    )
    
    axs[0,0].set_ylabel(
        "Yaw Rate (r) [°/sec]"
    )
    
    # --------------------------------------------------------
    # ESC Regions
    # --------------------------------------------------------

    mild_mask = (
        (esc_gain >= 0.4)
        & (esc_gain < 1.0)
    )

    aggressive_mask = (
        esc_gain >= 1.0
    )

    in_region = False
    start = None

    for i in range(len(t)):

        if mild_mask[i] and not in_region:

            start = t[i]
            in_region = True

        elif not mild_mask[i] and in_region:

            axs[0,0].axvspan(
                start,
                t[i],

                color="gold",

                alpha=0.05,

                label="Mild ESC"
            )

            in_region = False

    in_region = False
    start = None

    for i in range(len(t)):

        if aggressive_mask[i] and not in_region:

            start = t[i]
            in_region = True

        elif not aggressive_mask[i] and in_region:

            axs[0,0].axvspan(
                start,
                t[i],

                color="red",

                alpha=0.08,

                label="Aggressive ESC"
            )

            in_region = False

    axs[0,0].set_title(
        "Yaw Rate Tracking"
    )

    axs[0,0].grid(
        True,
        alpha=0.3
    )

    handles, labels = (
        axs[0,0]
        .get_legend_handles_labels()
    )

    unique = dict(
        zip(labels, handles)
    )

    axs[0,0].legend(
        unique.values(),
        unique.keys()
    )

    # --------------------------------------------------------
    # Sideslip
    # --------------------------------------------------------

    axs[0,1].plot(
        t,
        beta,
        linewidth=2
    )

    axs[0,1].set_title(
        "Sideslip Angle"
    )

    axs[0,1].grid(
        True,
        alpha=0.3
    )

    axs[0,1].set_ylabel(
        "Sideslip anngle (β) [°]"
    )

    # --------------------------------------------------------
    # Lateral Acceleration
    # --------------------------------------------------------

    axs[1,0].plot(
        t,
        lat_accel,
        linewidth=2
    )

    axs[1,0].set_title(
        "Lateral Acceleration"
    )

    axs[1,0].grid(
        True,
        alpha=0.3
    )

    axs[1,0].set_ylabel(
        "Lateral Acceleration (aᵧ) [m/s²]"
    )

    # --------------------------------------------------------
    # Yaw Moment
    # --------------------------------------------------------

    axs[1,1].plot(
        t,
        Mz,
        linewidth=2
    )

    axs[1,1].set_title(
        "Corrective Yaw Moment"
    )

    axs[1,1].grid(
        True,
        alpha=0.3
    )
    axs[1,1].set_ylabel(
        "Yaw Moment (Mz) [Nm]"
    )

    for ax in axs.flat:

        ax.set_xlabel(
            "Time (s)"
        )

    st.pyplot(fig)

    # ========================================================
    # ESC Comparison Mode
    # ========================================================

    if compare_mode:

        st.markdown("---")

        st.subheader(
            "ESC Effectiveness"
        )

        e1, e2 = st.columns(2)

        e1.metric(
            "Peak Sideslip (β) Reduction",
            f"{beta_reduction:.1f}%"
        )

        e2.metric(
            "Peak Yaw Reduction",
            f"{yaw_reduction:.1f}%"
        )

        # ----------------------------------------------------
        # Comparison Plots
        # ----------------------------------------------------

        fig2, axs2 = plt.subplots(
            2,
            1,
            figsize=(12, 8)
        )

        # ----------------------------------------------------
        # Yaw Rate Comparison
        # ----------------------------------------------------

        axs2[0].plot(

            res_off["t"],
            res_off["yaw_rate"],

            linestyle="--",
            linewidth=2,

            label="ESC OFF"
        )

        axs2[0].plot(

            res_on["t"],
            res_on["yaw_rate"],

            linewidth=2.5,

            label="ESC ON"
        )

        axs2[0].plot(

            res_on["t"],
            res_on["yaw_rate_ref"],

            linestyle=":",
            linewidth=1.5,

            label="Reference"
        )

        axs2[0].set_title(
            "Yaw Rate Comparison"
        )

        axs2[0].grid(
            True,
            alpha=0.3
        )

        axs2[0].set_ylabel(
            "Yaw Rate (r) [°/sec]"
        )

        axs2[0].legend()

        # ----------------------------------------------------
        # Sideslip Comparison
        # ----------------------------------------------------

        axs2[1].plot(

            res_off["t"],
            res_off["slip_angle"],

            linestyle="--",
            linewidth=2,

            label="ESC OFF"
        )

        axs2[1].plot(

            res_on["t"],
            res_on["slip_angle"],

            linewidth=2.5,

            label="ESC ON"
        )

        axs2[1].set_title(
            "Sideslip Comparison"
        )

        axs2[1].grid(
            True,
            alpha=0.3
        )

        axs2[1].legend()

        axs2[1].set_ylabel(
            "Sideslip Angle (β) [°]"
        )

        for ax in axs2:

            ax.set_xlabel(
                "Time (s)"
            )

        plt.tight_layout()
        st.pyplot(fig2)

        # ====================================================
        # Trajectory Comparison
        # ====================================================

        fig3, ax3 = plt.subplots(
            figsize=(10, 6)
        )

        ax3.plot(

            res_off["x"],
            res_off["y"],

            linestyle="--",
            linewidth=2,

            label="ESC OFF"
        )

        ax3.plot(

            res_on["x"],
            res_on["y"],

            linewidth=2.5,

            label="ESC ON"
        )

        # ----------------------------------------------------
        # Lane Boundaries
        # ----------------------------------------------------

        ax3.axhline(
            3.5,
            linestyle="--",
            alpha=0.5
        )

        ax3.axhline(
            -3.5,
            linestyle="--",
            alpha=0.5
        )

        # ----------------------------------------------------
        # Heading Arrows
        # ----------------------------------------------------

        skip = 40

        ax3.quiver(

            res_on["x"][::skip],
            res_on["y"][::skip],

            np.cos(
                np.deg2rad(
                    res_on["psi"][::skip]
                )
            ),

            np.sin(
                np.deg2rad(
                    res_on["psi"][::skip]
                )
            ),

            angles="xy",

            scale_units="xy",

            scale=0.2,

            width=0.003
        )

        ax3.quiver(

            res_off["x"][::skip],
            res_off["y"][::skip],

            np.cos(
                np.deg2rad(
                    res_off["psi"][::skip]
                )
            ),

            np.sin(
                np.deg2rad(
                    res_off["psi"][::skip]
                )
            ),

            angles="xy",

            scale_units="xy",

            scale=0.2,

            width=0.003,

            alpha=0.5
        )

        ax3.set_title(
            "Vehicle Trajectory"
        )

        ax3.set_xlabel(
            "Global X Position (m)"
        )

        ax3.set_ylabel(
            "Global Y Position (m)"
        )

        ax3.grid(
            True,
            alpha=0.3
        )

        ax3.axis("equal")

        ax3.legend()

        st.pyplot(fig3)

# ============================================================
# Tire Dynamics Tab
# ============================================================

with tab2:

    fig, axs = plt.subplots(
        2,
        2,
        figsize=(14, 10)
    )

    axs[0,0].plot(
        t,
        alpha_f,
        linewidth=2,
        label="Front ($α_f$)"
    )

    axs[0,0].plot(
        t,
        alpha_r,
        linewidth=2,
        label="Rear ($α_r$)"
    )

    axs[0,0].legend()

    axs[0,0].set_title(
        "Slip Angles"
    )

    axs[0,0].set_ylabel(
        "Slip Angle (α) [°]"
    )

    axs[0,0].set_xlabel(
        "Time (s)"
    )

    axs[0,1].plot(
        t,
        Fyf,
        linewidth=2,
        label="Front"
    )

    axs[0,1].plot(
        t,
        Fyr,
        linewidth=2,
        label="Rear"
    )

    axs[0,1].legend()

    axs[0,1].set_title(
        "Lateral Tire Forces"
    )

    axs[0,1].set_ylabel(
        "Lateral Force ($F_y$) [N]"
    )

    axs[0,1].set_xlabel(
        "Time (s)"
    )



    axs[1,0].plot(
        alpha_f,
        np.array(Fyf)/Fz1,
        linewidth=2,
        label="Front"
    )

    axs[1,0].plot(
        alpha_r,
        np.array(Fyr)/Fz2,
        linewidth=2,
        label="Rear"
    )

    axs[1,0].legend()

    axs[1,0].set_title(
        "Normalized Tire Force"
    )

    axs[1,0].set_ylabel(
        "Normalised Force ($F_y/F_z$)"
    )

    axs[1,0].set_xlabel(
        "Slip Angle (°)"
    )


    axs[1,1].plot(
        t,
        np.array(Fyf)/Fz1,
        linewidth=2,
        label="Front"
    )

    axs[1,1].plot(
        t,
        np.array(Fyr)/Fz2,
        linewidth=2,
        label="Rear"
    )

    axs[1,1].legend()

    axs[1,1].set_title(
        "Tire Utilization"
    )

    axs[1,1].set_ylabel(
        "Tire Utilization ($F_y/F_z$)"
    )

    axs[1,1].set_xlabel(
        "Time (s)"
    )

    for ax in axs.flat:

        ax.grid(
            True,
            alpha=0.3
        )

    plt.tight_layout()
    st.pyplot(fig)

    
# ============================================================
# Handling Characteristics Tab
# ============================================================

with tab3:

    # ========================================================
    # Handling Metrics
    # ========================================================

    delta = np.deg2rad(steering_deg)  # Steering Angle

    # --------------------------------------------------------
    # Understeer Gradient Approximation
    # --------------------------------------------------------

    ay_g = np.array(lat_accel) / 9.81

    steering_rad = np.deg2rad(steering_deg)

    yaw_rate_rad = np.deg2rad(yaw_rate)

    yaw_gain = np.max(np.abs(yaw_rate_rad)) / max(
        steering_rad,
        1e-3
    )

    Kus = steering_deg / max(
        np.max(np.abs(ay_g)),
        1e-3
    )

    # --------------------------------------------------------
    # Slip Angle Balance
    # --------------------------------------------------------

    alpha_balance = np.mean(
        np.array(alpha_f) - np.array(alpha_r)
    )

    # --------------------------------------------------------
    # Handling Classification
    # --------------------------------------------------------

    if stability_state == "Unstable":

        handling_text = "LIMIT UNDERSTEER"

    elif alpha_balance > 1.0:

        handling_text = "TOWARDS UNDERSTEER"

    elif alpha_balance > -0.5:

        handling_text = "NEUTRAL STEER"

    else:

        handling_text = "TOWARDS OVERSTEER"

    # ========================================================
    # KPI Row
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(

            "Understeer Gradient",

            f"{Kus:.2f} °/g"
        )

    # --------------------------------------------------------
    # Handling Balance Card Styling
    # --------------------------------------------------------

    if handling_text == "TOWARDS UNDERSTEER":

        handling_bg = "#d1fae5"

        handling_color = "#065f46"

    elif handling_text == "NEUTRAL STEER":

        handling_bg = "#e5e7eb"

        handling_color = "#374151"

    else:

        handling_bg = "#fee2e2"

        handling_color = "#991b1b"

    # --------------------------------------------------------
    # Custom KPI Card
    # --------------------------------------------------------

    with col2:

        st.markdown(
    f"""
    <div style="
        background-color: {handling_bg};
        color: {handling_color};
        padding: 20px 10px;
        min-height: 110px;
        border-radius: 16px;
        border: 1px solid rgba(0,0,0,0.08);
        display: flex;
        flex-direction: column;
        justify-content: center;
    ">

    <div style="
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 18px;
        text-align: left;
        color: #374151;
    ">
        Handling Characteristic
    </div>

    <div style="
        font-size: 22px;
        font-weight: 700;
        color: {handling_color};
        text-align: center;
    ">
        {handling_text}
    </div>

    </div>
    """,
            unsafe_allow_html=True
        )

    with col3:

        st.metric(

            "Peak Steering Demand",

            f"{steering_deg:.2f}°"
        )

    with col4:

        st.metric(

            "Yaw Gain",

            f"{yaw_gain:.1f} s⁻¹"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ========================================================
    # Handling Plots
    # ========================================================

    fig_handle, axs = plt.subplots(

        2,
        2,

        figsize=(15, 10)
    )

    # --------------------------------------------------------
    # Understeer Gradient Evolution
    # --------------------------------------------------------

    kus_dynamic = (
        np.array(alpha_f) - np.array(alpha_r)
    ) / np.maximum(
        ay_g,
        1e-3
    )

    axs[0,0].plot(

        ay_g,

        kus_dynamic,

        linewidth=2.5
    )

    axs[0,0].axhline(

        0,

        linestyle="--",

        linewidth=1.5,

        alpha=0.7
    )

    axs[0,0].set_title(

        "Understeer Gradient Evolution"
    )

    axs[0,0].set_xlabel(

        "Lateral Acceleration (g)"
    )

    axs[0,0].set_ylabel(

        "Dynamic Understeer Gradient [°/s]"
    )

    # --------------------------------------------------------
    # Slip Angle Balance
    # --------------------------------------------------------

    slip_balance = np.array(alpha_f) - np.array(alpha_r)

    axs[0,1].plot(

        ay_g,

        slip_balance,

        linewidth=2.5
    )

    axs[0,1].axhline(

        0,

        linestyle="--",

        linewidth=1.5,

        alpha=0.7
    )

    axs[0,1].set_title(

        "Handling Balance"
    )

    axs[0,1].set_xlabel(

        "Lateral Acceleration (g)"
    )

    axs[0,1].set_ylabel(

        "Slip Angle Difference ($α_f - α_r$) [°]"
    )

    # --------------------------------------------------------
    # Yaw Gain
    # --------------------------------------------------------

    yaw_gain_series = yaw_rate / max(
        steering_rad,
        1e-3
    )

    axs[1,0].plot(

        t,

        yaw_gain_series,

        linewidth=2.5
    )

    axs[1,0].set_title(

        "Yaw Gain"
    )

    axs[1,0].set_xlabel(

        "Time (s)"
    )

    axs[1,0].set_ylabel(

        "Yaw Gain (r/δ) [s⁻¹]"
    )

    # --------------------------------------------------------
    # Lateral Acceleration vs Sideslip
    # --------------------------------------------------------

    axs[1,1].plot(

        ay_g,

        beta,

        linewidth=2.5
    )

    axs[1,1].set_title(

        "Sideslip Response"
    )

    axs[1,1].set_xlabel(

        "Lateral Acceleration (g)"
    )

    axs[1,1].set_ylabel(

        "Sideslip Angle (β) [°]"
    )

    # --------------------------------------------------------
    # Grid
    # --------------------------------------------------------

    for ax in axs.flat:

        ax.grid(

            True,

            alpha=0.3
        )

    plt.tight_layout()

    st.pyplot(fig_handle)

# ============================================================
# Controller tab
# ============================================================

with tab4:

    fig, axs = plt.subplots(
        3,
        1,
        figsize=(12, 10)
    )

    axs[0].plot(
        t,
        Mz,
        linewidth=2
    )

    axs[0].set_title(
        "Corrective Yaw Moment"
    )

    axs[0].set_ylabel(
        "Yaw Moment ($M_z$) [Nm]"
    )

    axs[1].plot(
        t,
        yaw_error,
        linewidth=2
    )

    axs[1].set_title(
        "Yaw Rate Tracking Error"
    )
    axs[1].set_ylabel(
        "Yaw rate tracking error [°/s]"
    )

    axs[2].plot(
        t,
        esc_gain,
        linewidth=2
    )

    axs[2].set_ylim(
        -0.1,
        1.1
    )

    ax.set_yticks([0, 0.5, 1.0])

    ax.set_yticklabels([
        "OFF",
        "MILD",
        "AGGRESSIVE"
    ])

    axs[2].set_title(
        "ESC Intervention Level"
    )

    axs[2].set_ylabel(
        "ESC Intervention Gain [-]"
    )

    for ax in axs:

        ax.grid(
            True,
            alpha=0.3
        )

        ax.set_xlabel(
            "Time (s)"
        )

    plt.tight_layout()
    st.pyplot(fig)

# ============================================================
# Stability Tab
# ============================================================

with tab5:

    fig, axs = plt.subplots(
        1,
        2,
        figsize=(14, 6)
    )

    axs[0].plot(
        beta,
        yaw_rate,
        linewidth=2
    )

    axs[0].set_title(
        "Vehicle Stability Phase Portrait"
    )

    axs[0].set_xlabel(
        "Sideslip Angle (β) [°]"
    )

    axs[0].set_ylabel(
        "Yaw Rate (r) [°/s]"
    )

    axs[0].grid(
        True,
        alpha=0.3
    )

    axs[1].plot(
        t,
        beta,
        linewidth=2,
        label="Sideslip"
    )

    axs[1].axhline(
        3,
        linestyle="--"
    )

    axs[1].axhline(
        -3,
        linestyle="--"
    )

    axs[1].text(

        8.5,
        3.08,

        "Stable Limit",

        fontsize=10,

        color="#6b7280",

        alpha=0.8
    )

    axs[1].text(

        8.5,
        -2.92,

        "Stable Limit",

        fontsize=10,

        color="#6b7280",

        alpha=0.8
    )   

    axs[1].set_title(
        "Sideslip Stability Envelope"
    )

    axs[1].legend()

    axs[1].grid(
        True,
        alpha=0.3
    )

    axs[1].set_xlabel(
        "Time (s)"
    )

    axs[1].set_ylabel(
        "Sideslip Angle (β) [°]"
    )

    st.pyplot(fig)

# ============================================================
# Stability Envelope
# ============================================================

with tab6:

    if not sweep_mode:

        st.info(
            "Enable 'Stability Envelope Sweep' from the sidebar to generate the stability envelope."
        )

    else:

        fig_env, ax_env = plt.subplots(
            figsize=(10, 6)
        )

        # --------------------------------------------------------
        # Discrete Colormap
        # --------------------------------------------------------

        from matplotlib.colors import ListedColormap
        from matplotlib.colors import BoundaryNorm

        cmap = ListedColormap([

            "#a7dfb5",   # Stable → soft green

            "#fde68a",   # Marginal → soft amber

            "#f5b5b5"    # Unstable → soft red
        ])

        bounds = [-0.5, 0.5, 1.5, 2.5]

        norm = BoundaryNorm(
            bounds,
            cmap.N
        )

        # --------------------------------------------------------
        # Heatmap
        # --------------------------------------------------------

        im = ax_env.imshow(

            stability_map,

            origin="lower",

            cmap=cmap,

            norm=norm,

            aspect="auto",

            interpolation="bilinear",

            extent=[

                speed_range[0],
                speed_range[-1],

                steer_range[0],
                steer_range[-1]
            ]
        )

        # --------------------------------------------------------
        # Current Operating Point
        # --------------------------------------------------------

        ax_env.scatter(

            vehicle_speed,

            steering_deg,

            color="white",

            edgecolor="black",

            s=260,

            linewidth=2,

            zorder=5,

            label="Current Operating Point"
        )

        ax_env.set_xlabel(

            "Vehicle Speed (km/h)",

            fontsize=16
        )

        ax_env.set_ylabel(

            "Steering Angle (°)",

            fontsize=16
        )

        ax_env.set_xlim(
            40,
            240
        )

        ax_env.set_ylim(
            1,
            10
        )

        ax_env.tick_params(

            axis="both",

            labelsize=12
        )

        cbar = fig_env.colorbar(

            im,

            ax=ax_env,

            fraction=0.025,

            pad=0.03,

            ticks=[0, 1, 2]
        )

        cbar.ax.set_yticklabels([

            "Stable",
            "Marginal",
            "Unstable"
        ])

        cbar.ax.tick_params(

            labelsize=12
        )

        ax_env.legend(

            loc="upper left",

            fontsize=11,

            framealpha=0.95
        )

        st.pyplot(fig_env)

# ========================================================
# Back to Top Button
# ========================================================

st.markdown(

    """
    <style>

    .back-to-top {

        position: fixed;

        bottom: 20px;

        right: 20px;

        width: 44px;

        height: 44px;

        border-radius: 50%;

        background-color: rgba(31, 41, 55, 0.82);

        display: flex;

        align-items: center;

        justify-content: center;

        z-index: 99999;

        box-shadow: 0 4px 10px rgba(0,0,0,0.16);

        backdrop-filter: blur(6px);

        transition: all 0.25s ease;
    }

    .back-to-top:hover {

        background-color: rgba(17, 24, 39, 0.96);

        transform: translateY(-3px);

        box-shadow: 0 6px 16px rgba(0,0,0,0.24);
    }

    .back-to-top img {

        width: 18px;

        height: 18px;

        object-fit: contain;
    }

    html {

        scroll-behavior: smooth;
    }

    </style>

    <a href="#top" class="back-to-top">

        ⮝

    </a>

    """,

    unsafe_allow_html=True
)

# ========================================================
# Footer Watermark
# ========================================================

st.markdown(

    """
    <div style="
        text-align: center;
        margin-top: 60px;
        margin-bottom: 10px;
        color: #6b7280;
        font-size: 12px;
        opacity: 0.65;
        letter-spacing: 0.5px;
    ">

        Vehicle Dynamics Dashboard v1.0 |  Anurakt Raj Mathur, M.Sc.

    </div>
    """,

    unsafe_allow_html=True
)