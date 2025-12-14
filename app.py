import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd

# ----------------------------------------------------
# Pasquill–Gifford sigma functions
# ----------------------------------------------------
def sigma_y(x, S):
    return {
        "A": 0.22 * x * ((1 + 0.0001 * x) ** -0.5),
        "B": 0.16 * x * ((1 + 0.0001 * x) ** -0.5),
        "C": 0.11 * x * ((1 + 0.0001 * x) ** -0.5),
        "D": 0.08 * x * ((1 + 0.0001 * x) ** -0.5),
        "E": 0.06 * x * ((1 + 0.0001 * x) ** -0.5),
        "F": 0.04 * x * ((1 + 0.0001 * x) ** -0.5),
    }[S]


def sigma_z(x, S):
    return {
        "A": 0.20 * x,
        "B": 0.12 * x,
        "C": 0.08 * x,
        "D": 0.06 * x,
        "E": 0.03 * x,
        "F": 0.016 * x,
    }[S]


# ----------------------------------------------------
# Gaussian plume equation
# ----------------------------------------------------
def gaussian(Q, u, H, x, y, sy, sz):
    return (Q / (2 * math.pi * u * sy * sz)) * \
           math.exp(-(y ** 2) / (2 * sy ** 2)) * \
           math.exp(-(H ** 2) / (2 * sz ** 2))


# ----------------------------------------------------
# Stability class (Turner – simplified)
# ----------------------------------------------------
def compute_stability_class(wind_speed, cloud_cover):
    if wind_speed < 2:
        return "A" if cloud_cover < 40 else "B"
    elif 2 <= wind_speed < 3:
        return "B" if cloud_cover < 40 else "C"
    elif 3 <= wind_speed < 5:
        return "C" if cloud_cover < 40 else "D"
    elif 5 <= wind_speed < 6:
        return "D"
    else:
        return "E"


# ----------------------------------------------------
# UI
# ----------------------------------------------------
st.set_page_config(page_title="Gaussian Plume Model", layout="centered")
st.title("🌏 Gaussian Plume Model")

# ----------------------------------------------------
# City selection (REFERENCE ONLY)
# ----------------------------------------------------
st.header("📍 Select City (Reference Only)")

city_list = {
    "Select City": (0.0, 0.0),

    # Metro Cities
    "Delhi": (28.61, 77.20),
    "Mumbai": (19.07, 72.87),
    "Chennai": (13.08, 80.27),
    "Kolkata": (22.57, 88.36),
    "Bengaluru": (12.97, 77.59),
    "Hyderabad": (17.38, 78.48),

    # Major Cities
    "Pune": (18.52, 73.85),
    "Ahmedabad": (23.03, 72.58),
    "Jaipur": (26.91, 75.79),
    "Lucknow": (26.85, 80.95),
    "Kanpur": (26.45, 80.33),
    "Nagpur": (21.15, 79.09),
    "Indore": (22.72, 75.86),
    "Bhopal": (23.26, 77.41),
    "Patna": (25.59, 85.14),
    "Ranchi": (23.34, 85.31),

    # South India
    "Visakhapatnam": (17.68, 83.21),
    "Vijayawada": (16.51, 80.64),
    "Tirupati": (13.63, 79.42),
    "Coimbatore": (11.01, 76.96),
    "Madurai": (9.93, 78.12),
    "Salem": (11.66, 78.14),
    "Trichy": (10.79, 78.70),
    "Warangal": (17.98, 79.60),

    # West India
    "Surat": (21.17, 72.83),
    "Vadodara": (22.30, 73.20),
    "Rajkot": (22.30, 70.80),
    "Udaipur": (24.58, 73.68),
    "Jodhpur": (26.24, 73.02),

    # North India
    "Amritsar": (31.63, 74.87),
    "Chandigarh": (30.74, 76.79),
    "Dehradun": (30.31, 78.03),
    "Shimla": (31.10, 77.17),
    "Jammu": (32.73, 74.87),

    # East & North-East
    "Bhubaneswar": (20.30, 85.82),
    "Cuttack": (20.46, 85.88),
    "Durgapur": (23.55, 87.29),
    "Siliguri": (26.72, 88.43),
    "Guwahati": (26.14, 91.74),
    "Shillong": (25.57, 91.88),

    # Kerala
    "Kochi": (9.97, 76.28),
    "Thiruvananthapuram": (8.52, 76.93),
    "Kozhikode": (11.26, 75.78)
}

city = st.selectbox("Choose City (type to search)", city_list.keys())
lat, lon = city_list[city]

if city != "Select City":
    st.info(f"Latitude: {lat}, Longitude: {lon}")

# ----------------------------------------------------
# Meteorological inputs
# ----------------------------------------------------
st.header("🌤️ Meteorological Parameters (Manual)")

wind_speed = st.number_input("Wind Speed u (m/s)", min_value=0.0, value=0.0)
cloud_cover = st.number_input("Cloud Cover (%)", min_value=0.0, max_value=100.0, value=0.0)

# ----------------------------------------------------
# Emission & stack inputs
# ----------------------------------------------------
st.header("🏭 Emission & Stack Parameters (Manual)")

Q = st.number_input("Emission Rate Q (g/s)", min_value=0.0, value=0.0)
H = st.number_input("Effective Stack Height H (m)", min_value=0.0, value=0.0)
x = st.number_input("Downwind Distance x (m)", min_value=0.0, value=0.0)
y = st.number_input("Crosswind Distance y (m)", min_value=0.0, value=0.0)

calculate = st.button("🔍 Calculate")

# ----------------------------------------------------
# Calculations
# ----------------------------------------------------
if calculate:
    if wind_speed == 0 or Q == 0 or H == 0 or x == 0:
        st.error("❌ Please enter all required values.")
    else:
        S_class = compute_stability_class(wind_speed, cloud_cover)

        sy = sigma_y(x, S_class)
        sz = sigma_z(x, S_class)
        C = gaussian(Q, wind_speed, H, x, y, sy, sz)

        st.header("📌 Computed Results")
        st.info(f"**Computed Stability Class: {S_class}**")
        st.write(f"σᵧ = {sy:.2f} m")
        st.write(f"σz = {sz:.2f} m")
        st.success(f"Ground Level Concentration = {C:.6e} g/m³")

        # ------------------------------------------------
        # Table for all classes
        # ------------------------------------------------
        st.header("📊 σᵧ and σz for All Stability Classes")

        stability_desc = {
            "A": "Very Unstable",
            "B": "Unstable",
            "C": "Slightly Unstable",
            "D": "Neutral",
            "E": "Slightly Stable",
            "F": "Stable"
        }

        df = pd.DataFrame([
            {
                "Class": S,
                "Condition": stability_desc[S],
                "σᵧ (m)": round(sigma_y(x, S), 2),
                "σz (m)": round(sigma_z(x, S), 2)
            }
            for S in ["A", "B", "C", "D", "E", "F"]
        ])

        st.dataframe(df, use_container_width=True)

        # ------------------------------------------------
        # Graphs
        # ------------------------------------------------
        x_vals = np.logspace(2, 5, 200)

        st.subheader("📈 σᵧ vs Distance")
        fig1, ax1 = plt.subplots()
        for S in ["A", "B", "C", "D", "E", "F"]:
            ax1.plot(x_vals, [sigma_y(i, S) for i in x_vals], label=f"Class {S}")
        ax1.set_xscale("log")
        ax1.set_yscale("log")
        ax1.set_xlabel("Distance (m)")
        ax1.set_ylabel("σᵧ (m)")
        ax1.legend()
        ax1.grid(True, which="both")
        st.pyplot(fig1)

        st.subheader("📈 σz vs Distance")
        fig2, ax2 = plt.subplots()
        for S in ["A", "B", "C", "D", "E", "F"]:
            ax2.plot(x_vals, [sigma_z(i, S) for i in x_vals], label=f"Class {S}")
        ax2.set_xscale("log")
        ax2.set_yscale("log")
        ax2.set_xlabel("Distance (m)")
        ax2.set_ylabel("σz (m)")
        ax2.legend()
        ax2.grid(True, which="both")
        st.pyplot(fig2)
