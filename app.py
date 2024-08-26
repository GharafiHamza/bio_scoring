import streamlit as st
import numpy as np
import pandas as pd
import math

# Set page config to wide mode
st.set_page_config(layout="wide")

# Initial data
if 'fish_species' not in st.session_state:
    st.session_state.fish_species = {}

if 'species_groups' not in st.session_state:
    st.session_state.species_groups = {}

# Function to calculate biodiversity indexes
def calculate_biodiversity_indexes(species_dict):
    species = list(species_dict.keys())
    counts = list(species_dict.values())
    total_count = sum(counts)
    S = len(species)
    
    # Simpson's Index
    p_i = [count / total_count for count in counts]
    simpsons_index = 1 - sum(p**2 for p in p_i)
    
    # Shannon-Wiener Index
    shannon_wiener_index = -sum(p * np.log(p) for p in p_i)
    
    # Pielou's Evenness Index
    pielou_evenness_index = shannon_wiener_index / np.log(S) if S > 1 else 0
    
    # Margalef Index
    margalef_index = (S - 1) / np.log(total_count) if total_count > 0 else 0
    
    return simpsons_index, shannon_wiener_index, pielou_evenness_index, margalef_index

# Function to calculate star rating for biodiversity
def biodiversity_star_rating(index, max_value, margalef):
    step = max_value / 5
    if margalef:
        star_value = math.ceil(index / step)
    else:
        star_value = index / step
    full_stars = int(star_value)
    fractional_part = star_value - full_stars

    # Generate the HTML for the stars
    star_html = ""
    for _ in range(full_stars):
        star_html += '<span style="font-size:20px;color:gold;">&#9733;</span>'
    
    if fractional_part > 0:
        # Overlay a partial gold star on a grey star
        star_html += f'''
        <span style="font-size:20px;position:relative;display:inline-block;">
            <span style="color:gold;position:absolute;width:{int(fractional_part * 100)}%;overflow:hidden;">&#9733;</span>
            <span style="color:lightgray;">&#9733;</span>
        </span>
        '''
    
    # Add empty grey stars for the remaining stars
    if fractional_part:
        star_html += '<span style="font-size:20px;color:lightgray;">&#9733;</span>' * (5 - full_stars - 1)
    else:
        star_html += '<span style="font-size:20px;color:lightgray;">&#9733;</span>' * (5 - full_stars)
    
    return star_value, star_html

def final_star_rating(index, max_value):
    step = max_value / 5
    star_value = index / step
    full_stars = int(star_value)
    fractional_part = star_value - full_stars

    # Generate the HTML for the stars
    star_html = ""
    for _ in range(full_stars):
        star_html += '<span style="font-size:50px;color:gold;">&#9733;</span>'
    
    if fractional_part:
        # Overlay a partial gold star on a grey star
        star_html += f'''
        <span style="font-size:50px;position:relative;display:inline-block;">
            <span style="color:gold;position:absolute;width:{int(fractional_part * 100)}%;overflow:hidden;">&#9733;</span>
            <span style="color:lightgray;">&#9733;</span>
        </span>
        '''
    
    # Add empty grey stars for the remaining stars
    if fractional_part > 0:
        star_html += '<span style="font-size:50px;color:lightgray;">&#9733;</span>' * (5 - full_stars - 1)
    else:
        star_html += '<span style="font-size:50px;color:lightgray;">&#9733;</span>' * (5 - full_stars)

    
    return star_value, star_html

# Function to calculate the final score based on star ratings
def calculate_final_star_score(margalef_stars, pielou_stars):
    weighted_score = (0.55 * margalef_stars) + (0.45 * pielou_stars)
    final_star_count = round(weighted_score, 2)
    return final_star_count, final_star_rating(final_star_count, 5)[1]

# Streamlit UI
st.title("Biodiversity and Water Quality Calculator")

# File upload section
st.subheader("Upload Data File")
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    if "Group" in df.columns and "Specie" in df.columns and "Count" in df.columns:
        # Convert the dataframe to a species dictionary
        species_dict = df.set_index('Specie')['Count'].to_dict()
        species_groups = df.set_index('Specie')['Group'].to_dict()
        st.session_state.fish_species = species_dict
        st.session_state.species_groups = species_groups

        st.write("Data uploaded successfully.")
    else:
        st.error("The file must contain 'Group', 'Specie', and 'Count' columns.")

# Ensure no calculations are done until data is available
if st.session_state.fish_species:
    # Calculate biodiversity indexes
    simpsons_index, shannon_wiener_index, pielou_evenness_index, margalef_index = calculate_biodiversity_indexes(st.session_state.fish_species)

    # Calculate star ratings
    simpsons_stars, simpsons_star_display = biodiversity_star_rating(simpsons_index, 1-1/len(st.session_state.fish_species), 0)
    shannon_stars, shannon_star_display = biodiversity_star_rating(shannon_wiener_index, np.log(len(st.session_state.fish_species)), 0)
    pielou_stars, pielou_star_display = biodiversity_star_rating(pielou_evenness_index, 1, 0)
    margalef_stars, margalef_star_display = biodiversity_star_rating(margalef_index, 5, 1)

    # Calculate final star score
    final_star_count, final_star_display = calculate_final_star_score(margalef_stars, pielou_stars)

    # Display final score at the top
    st.markdown(f"<h1 style='text-align: center; color: red;'>{final_star_display}</h1>", unsafe_allow_html=True)
else:
    st.warning("Please upload a file or add a species to begin calculations.")

# Filter by group
group_filter = st.multiselect("Filter by Group", options=list(set(st.session_state.species_groups.values())))

# (1,1): Fish species list - Retractable
with st.container():
    with st.expander("Fish Species Management", expanded=False):
        if group_filter:
            filtered_species = {k: v for k, v in st.session_state.fish_species.items() if st.session_state.species_groups[k] in group_filter}
        else:
            filtered_species = st.session_state.fish_species

        species = st.text_input("Add a new species:")
        group = st.selectbox("Select Group", options=list(set(st.session_state.species_groups.values())))
        count = st.number_input(f"Count for {species}", min_value=0, value=0, key="new_species_count")
        
        if st.button("Add Species"):
            if species:
                st.session_state.fish_species[species] = count
                st.session_state.species_groups[species] = group

        # Display and update species list
        for sp, cnt in filtered_species.items():
            cols = st.columns([1, 2, 1, 1])
            cols[0].write(st.session_state.species_groups[sp])
            cols[1].write(sp)
            st.session_state.fish_species[sp] = cols[2].number_input(f"Count for {sp}", min_value=0, value=cnt, key=f"num_{sp}")
            if cols[3].button("Remove", key=f"remove_{sp}"):
                del st.session_state.fish_species[sp]
                del st.session_state.species_groups[sp]
                st.experimental_rerun()  # Rerun to update the session state immediately

# (1,2): Biodiversity indexes
if st.session_state.fish_species:
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Biodiversity Indexes")
            st.write(f"Simpson's Index: {simpsons_index:.4f}")
            st.write(f"Shannon-Wiener Index: {shannon_wiener_index:.4f}")
            st.write(f"Pielou's Evenness Index: {pielou_evenness_index:.4f}")
            st.write(f"Margalef Index: {margalef_index:.4f}")
        
        with col2:
            st.subheader("Biodiversity Star Rating")
            st.markdown(f"{simpsons_star_display}", unsafe_allow_html=True)
            st.markdown(f"{shannon_star_display}", unsafe_allow_html=True)
            st.markdown(f"{pielou_star_display}", unsafe_allow_html=True)
            st.markdown(f"{margalef_star_display}", unsafe_allow_html=True)
