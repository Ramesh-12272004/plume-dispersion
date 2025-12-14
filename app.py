import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import requests
import pandas as pd

# ----------------------------------------------------
# Pasquill–Gifford sigma functions
# ----------------------------------------------------
def sigma_y(x, S):
    values = {
        "A": 0.22 * x * ((1 + 0.0001 * x) ** -0.5),
        "B": 0.16 * x * ((1 + 0.0001 * x) ** -0.5),
        "C": 0.11 * x * ((1 + 0.0001 * x) ** -0.5),
        "D": 0.08 * x * ((1 + 0.0001 * x) ** -0.5),
        "E": 0.06 * x * ((1 + 0.0001 * x) ** -0.5),
        "F": 0.04 * x * ((1 + 0.0001 * x) ** -0.5)
    }
    return values[S]


def sigma_z(x, S):
    values = {
        "A": 0.20 * x,
        "B": 0.12 * x,
        "C": 0.08 * x,
        "D": 0.06 * x,
        "E": 0.03 * x,
        "F": 0.016 * x
    }
    return values[S]


# ----------------------------------------------------
# Gaussian Equation
# ----------------------------------------------------
def gaussian(Q, u, H, x, y, sy, sz):
    if u == 0 or sy == 0 or sz == 0:
        return 0
    return (Q / (2 * math.pi * u * sy * sz)) * \
           math.exp(-(y ** 2) / (2 * sy ** 2)) * \
           math.exp(-(H ** 2) / (2 * sz ** 2))


# ----------------------------------------------------
# IMD-Based Stability Class (Turner Method)
# ----------------------------------------------------
def compute_stability_class(wind_speed, cloud_cover):
    if wind_speed < 2:
        return "A" if cloud_cover < 4 else "B"
    elif 2 <= wind_speed < 3:
        return "B" if cloud_cover < 4 else "C"
    elif 3 <= wind_speed < 5:
        return "C" if cloud_cover < 4 else "D"
    elif 5 <= wind_speed < 6:
        return "D"
    else:
        return "E"


# ----------------------------------------------------
# Fetch weather (Open-Meteo API)
# ----------------------------------------------------
def get_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true&hourly="
        f"cloud_cover,wind_speed_10m,boundary_layer_height"
    )
    data = requests.get(url).json()

    wind_speed = data["current_weather"]["windspeed"]
    cloud_cover = data["hourly"]["cloud_cover"][0]
    mixing_height = data["hourly"]["boundary_layer_height"][0]

    return wind_speed, cloud_cover, mixing_height


# ----------------------------------------------------
# STREAMLIT UI
# ----------------------------------------------------
st.set_page_config(page_title="Gaussian Plume Model", layout="centered")
st.title("🌏 Real-Time Gaussian Plume Model (σᵧ & σz)")
st.header("📍 Select Location in India")

# ----------------------------------------------------
# City list
# ----------------------------------------------------
city_list = {
    "Select City": (0.0, 0.0),
    "Delhi": (28.61, 77.20),
    "Mumbai": (19.07, 72.87),
    "Chennai": (13.08, 80.27),
    "Kolkata": (22.57, 88.36),
    "Bengaluru": (12.97, 77.59),
    "Hyderabad": (17.38, 78.48),
    "Pune": (18.52, 73.85),
    "Ahmedabad": (23.03, 72.58),
    "Jaipur": (26.91, 75.79),
    "Lucknow": (26.85, 80.95),
    "Visakhapatnam": (17.68, 83.21),
    "Kochi": (9.97, 76.28),
    "Guwahati": (26.14, 91.74),
    "Bhubaneswar": (20.30, 85.82)
}

city = st.selectbox("Select City (type to search)", city_list.keys())
lat, lon = city_list[city]

lat = st.number_input("Latitude", value=float(lat))
lon = st.number_input("Longitude", value=float(lon))

if lat != 0 and lon != 0:
    wind_speed, cloud_cover, mixing_height = get_weather(lat, lon)

    st.success(f"Wind Speed: {wind_speed:.2f} m/s")
    st.success(f"Cloud Cover: {cloud_cover:.0f} %")
    st.success(f"Mixing Height: {mixing_height:.0f} m")

    S_class = compute_stability_class(wind_speed, cloud_cover)
    st.info(f"Computed Stability Class: **{S_class}**")
else:
    st.warning("Please select a valid city.")

# ----------------------------------------------------
# Inputs
# ----------------------------------------------------
st.header("🧮 Emission & Stack Parameters")
Q = st.number_input("Emission Rate Q (g/s)", value=100.0)
H = st.number_input("Stack Height H (m)", value=50.0)
y = st.number_input("Crosswind Distance y (m)", value=0.0)
x_calc = st.number_input("Downwind Distance x (m)", value=1000.0)

calculate = st.button("🔍 Calculate")

# ----------------------------------------------------
# Run Model
# ----------------------------------------------------
if calculate and lat != 0 and lon != 0:

    sy = sigma_y(x_calc, S_class)
    sz = sigma_z(x_calc, S_class)
    C = gaussian(Q, wind_speed, H, x_calc, y, sy, sz)

    st.header("📌 Computed Results")
    st.write(f"σᵧ = **{sy:.2f} m**")
    st.write(f"σz = **{sz:.2f} m**")
    st.success(f"Ground Level Concentration = **{C:.6f} g/m³**")

    # ------------------------------------------------
    # TABLE: σᵧ and σz for ALL classes
    # ------------------------------------------------
    st.header("📊 σᵧ and σz Values for All Stability Classes")

    stability_desc = {
        "A": "Very Unstable",
        "B": "Unstable",
        "C": "Slightly Unstable",
        "D": "Neutral",
        "E": "Slightly Stable",
        "F": "Stable"
    }

    table_data = []
    for S in ["A", "B", "C", "D", "E", "F"]:
        table_data.append({
            "Stability Class": S,
            "Atmospheric Condition": stability_desc[S],
            "σᵧ (m)": round(sigma_y(x_calc, S), 2),
            "σz (m)": round(sigma_z(x_calc, S), 2)
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)

    # ------------------------------------------------
    # Graphs
    # ------------------------------------------------
    x_vals = np.logspace(2, 5, 200)
    stabilities = ["A", "B", "C", "D", "E", "F"]
    colors = ["red", "orange", "green", "blue", "purple", "brown"]

    st.subheader("📈 σᵧ vs Distance")
    fig1, ax1 = plt.subplots()
    for S, c in zip(stabilities, colors):
        ax1.plot(x_vals, [sigma_y(x, S) for x in x_vals], label=f"Class {S}", color=c)
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xlabel("Distance (m)")
    ax1.set_ylabel("σᵧ (m)")
    ax1.grid(True, which="both")
    ax1.legend()
    st.pyplot(fig1)

    st.subheader("📉 σz vs Distance")
    fig2, ax2 = plt.subplots()
    for S, c in zip(stabilities, colors):
        ax2.plot(x_vals, [sigma_z(x, S) for x in x_vals], label=f"Class {S}", color=c)
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel("Distance (m)")
    ax2.set_ylabel("σz (m)")
    ax2.grid(True, which="both")
    ax2.legend()
    st.pyplot(fig2)

else:
    st.info("Click **Calculate** after selecting a city.")
