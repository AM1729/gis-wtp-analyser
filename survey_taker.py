import streamlit as st
import requests
from streamlit_folium import st_folium
import folium
import h3
import os
from crud import CRUD, get_connection_pool
from data_downloader import DataDownloader
from folium.plugins import MousePosition

RESEARCH_ADMIN_USERNAME = "admin"
RESEARCH_ADMIN_PASSWORD = "secret"

parkH3Indexx = os.environ.get("PARK_H3_INDEX")

if not parkH3Indexx:
    raise ValueError("PARK_H3_INDEX environment variable not set.")


st.set_page_config(page_title="Willing to Pay Analysis for a Public Park in Trento, Italy", layout="wide")

st.title("Willingness to Pay for Public Park in Trento, Italy")
st.markdown("#### Select the Municipality and Optionally add a Postal Code to zoom into the map. \n" \
"Click on the map to select your home location.")

print("Starting SQL Connection Pool...")
get_connection_pool()  # Initialize the connection pool at app start

if st.button("Download Survey Responses (Admin Only)"):
    # Step 2: Ask for credentials
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    # Step 3: Check credentials
    if st.button("Login"):
        if username == RESEARCH_ADMIN_USERNAME and password == RESEARCH_ADMIN_PASSWORD:
            st.success("Login successful! You can download the CSV now.")
            csv_data = DataDownloader.get_data_as_csv()
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="survey_responses.csv",
                mime="text/csv"
            )
        else:
            st.error("Invalid credentials. Please get in touch with the Research Team for access")


if "point" not in st.session_state:
    st.session_state.point = {}

if "map_center" not in st.session_state:
    st.session_state.map_center = [41.8719, 12.5674] # Default to Italy center

if "map_bounds" not in st.session_state:
    st.session_state.map_bounds = None

st.session_state.resp = 0


with st.form("region_form"):
    region = st.text_input("Municipality [Required]", placeholder="e.g. Trento or Rovereto")
    postal = st.text_input("Postal Code [Required]", placeholder="e.g. 50100")
    searched = st.form_submit_button("Search")

if searched and region:
    query = f"{region}, {postal + ', ' if postal else ''} Trentino, Italy"
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    response = requests.get(url, params=params, headers={"User-Agent": "streamlit-region-app"})
    data = response.json()

    if data:
        result = data[0]
        bbox = result["boundingbox"]  # [south, north, west, east]
        south, north = float(bbox[0]), float(bbox[1])
        west, east = float(bbox[2]), float(bbox[3])
        lat, lon = float(result["lat"]), float(result["lon"])

        # Save to session state
        st.session_state.map_center = [lat, lon]
        st.session_state.map_bounds = [[south, west], [north, east]]

        st.success(f"Zoomed to {region}")
    else:
        st.warning("No results found. Try another region name.")

# --- Initialize map ---
m = folium.Map(location=st.session_state.map_center, zoom_start=15)

# --- Draw bounding box if present ---
if st.session_state.map_bounds:
    bounds = st.session_state.map_bounds
    folium.Rectangle(bounds=bounds, color="blue", fill=False).add_to(m)
    folium.Marker(
        st.session_state.map_center, popup="Selected Region"
    ).add_to(m)
    m.fit_bounds(bounds)

st.markdown("### 🗺️ Click on the map to select your approximate neighborhood")

MousePosition(
    position='topright',
    separator=' : ',
    empty_string='NaN',
    lng_first=False,
    num_digits=6,
    prefix='',
    lat_formatter=None,
    lng_formatter=None
).add_to(m)

clicked_data = st_folium(m, width=800, height=500)

if clicked_data and clicked_data.get("last_clicked"):
    clicked_point = clicked_data["last_clicked"]
    st.session_state.point = {"lat": round(clicked_point["lat"], 6), 
                                  "lng": round(clicked_point["lng"], 6)}
        
    st.info(f"📍Selected Home Location: Lat {clicked_point['lat']:.6f}, Lon {clicked_point['lng']:.6f}")
    h3Index = h3.latlng_to_cell(clicked_point['lat'], clicked_point['lng'], 9)
    st.session_state.resp += 1


st.markdown("#### Marital Status")
married = st.radio("mar", ["Yes", "No"], label_visibility="hidden", index= None)
if married:
    st.session_state.resp += 1

st.markdown("#### Level of Education")
eduStatus = st.radio("edu", ["No formal education", "High School", "Bachelor's Degree", "Master's Degree", "PhD"], label_visibility="hidden", index= None)
if eduStatus:
    st.session_state.resp += 1

st.markdown("#### Employment Status")
employee = st.radio("emp", ["Employed", "Unemployed", "Student", "Retired"], label_visibility="hidden", index= None)
if employee:
    st.session_state.resp += 1

st.markdown("#### Number of Kids")
numKids = st.radio("numkids", ["0", "1", "2", "3", "4", "5 or more"], label_visibility="hidden", index= None)
if numKids:
    st.session_state.resp += 1

st.markdown("#### Annual Income (€)")
income = st.number_input("inc", label_visibility="hidden", step=1, format="%d")
if income and income >= 0 and income <= 100000000000000:
    st.session_state.resp += 1


st.markdown("### Age (Years)")
age = st.number_input("age", label_visibility="hidden", step=1, format="%d")
if age and age > 0 and age <= 120:
    st.session_state.resp += 1


st.markdown("#### Weekly Hours at Work or Study")
hours_worked = st.number_input("hours", label_visibility="hidden", step=1, format="%d")
if hours_worked and hours_worked >= 0 and hours_worked <= 168:
    st.session_state.resp += 1

if st.button("✅ Submit Responses"):
    if st.session_state.resp < 1:
        st.warning("Please answer atleast 1 question in the survey.")
    else:
        ## If no points selected, take the center of the map based on region, and pincode
        if not clicked_data.get("last_clicked") and not st.session_state.point and region and postal:
            st.warning("Taking the Center of the Region as Home location")
            st.session_state.point = {"lat": round(st.session_state.map_center[0], 6), 
                                    "lng": round(st.session_state.map_center[1], 6)}
            h3Index = h3.latlng_to_cell(st.session_state.point['lat'], st.session_state.point['lng'], 9)

        payload = {
            "h3Index": h3Index,
            "municipality": region,
            "postalCode": postal,
            "hexDistanceToPark": h3.grid_distance(h3Index, parkH3Indexx),
            "married": married,
            "education": eduStatus,
            "employment": employee,
            "numKids": numKids,
            "income": income,
            "hoursWorkedPerWeek": hours_worked
        }

        try:
            CRUD.add_to_db(payload)
        except Exception as e:
            st.error(f"An error occurred while submitting your responses, Please try submitting again") 
        else:
            st.success(f"Response submitted successfully, Thank you for participating in the survey!.")