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
    if sy == 0 or sz == 0:
        return 0
    return (Q / (2 * math.pi * u * sy * sz)) * \
           math.exp(-(y**2) / (2*sy**2)) * \
           math.exp(-(H**2) / (2*sz**2))

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
# Fetch weather (Open-Meteo)
# ----------------------------------------------------
def get_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true&hourly="
        f"temperature_2m,relative_humidity_2m,pressure_msl,"
        f"cloud_cover,wind_speed_10m,boundary_layer_height"
    )
    response = requests.get(url).json()

    wind_speed = response["current_weather"]["windspeed"]
    cloud_cover = response["hourly"]["cloud_cover"][0]
    mixing_height = response["hourly"]["boundary_layer_height"][0]

    return wind_speed, cloud_cover, mixing_height


# ----------------------------------------------------
# STREAMLIT UI
# ----------------------------------------------------
st.title("🌏 Real-Time Gaussian Plume Model (Separate σᵧ & σ_z Graphs)")

st.header("📍 Select Location in India")

# Manual Location Input
city_list = {
    "Select City": (0, 0),
    "Delhi": (28.61, 77.20),
    "Mumbai": (19.07, 72.87),
    "Chennai": (13.08, 80.27),
    "Hyderabad": (17.38, 78.48),
    "Bengaluru": (12.97, 77.59),
    "Kolkata": (22.57, 88.36),
    "Pune": (18.52, 73.85),
    "Ahmedabad": (23.03, 72.58)
}

city = st.selectbox("Select City", city_list.keys())
lat, lon = city_list[city]

lat = st.number_input("Latitude", value=lat)
lon = st.number_input("Longitude", value=lon)

if lat != 0 and lon != 0:
    wind_speed, cloud_cover, mixing_height = get_weather(lat, lon)
    st.success(f"Wind Speed: {wind_speed} m/s")
    st.success(f"Cloud Cover: {cloud_cover}%")
    st.success(f"Mixing Height: {mixing_height} m")

    S_class = compute_stability_class(wind_speed, cloud_cover)
    st.info(f"Computed Stability Class: **{S_class}**")
else:
    st.warning("Please choose a valid city or enter correct coordinates.")

# ----------------------------------------------------
# Gaussian Inputs
# ----------------------------------------------------
Q = st.number_input("Emission Rate Q (g/s)", value=100.0)
H = st.number_input("Stack Height H (m)", value=50.0)
y = st.number_input("Crosswind Distance y (m)", value=0.0)
x_calc = st.number_input("Distance x for calculation (m)", value=1000.0)

calculate = st.button("Calculate")

# ----------------------------------------------------
# Run Model
# ----------------------------------------------------
if calculate:

    sy = sigma_y(x_calc, S_class)
    sz = sigma_z(x_calc, S_class)

    C = gaussian(Q, wind_speed, H, x_calc, y, sy, sz)

    st.header("📌 Computed Values")
    st.write(f"σᵧ = {sy:.2f} m")
    st.write(f"σ_z = {sz:.2f} m")
    st.success(f"Concentration at {x_calc} m = **{C:.6f} g/m³**")

    # Range for plotting
    x_vals = np.logspace(2, 5, 200)
    stabilities = ["A", "B", "C", "D", "E", "F"]
    colors = ["red", "orange", "green", "blue", "purple", "brown"]

    # -----------------------------------------------
    # GRAPH 1 — σᵧ vs Distance (A–F)
    # -----------------------------------------------
    st.subheader("📈 σᵧ vs Distance (All Stability Classes)")
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

    # -----------------------------------------------
    # GRAPH 2 — σ_z vs Distance (A–F)
    # -----------------------------------------------
    st.subheader("📉 σ_z vs Distance (All Stability Classes)")
    fig2, ax2 = plt.subplots()

    for S, c in zip(stabilities, colors):
        ax2.plot(x_vals, [sigma_z(x, S) for x in x_vals], label=f"Class {S}", color=c)

    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel("Distance (m)")
    ax2.set_ylabel("σ_z (m)")
    ax2.grid(True, which="both")
    ax2.legend()
    st.pyplot(fig2)

else:
    st.info("Press **Calculate** to generate graphs.")
