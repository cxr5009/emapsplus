import streamlit as st
import folium
from folium.plugins import MarkerCluster, Fullscreen
from streamlit_folium import folium_static
import pandas as pd

# Settings | Default
st.set_page_config(layout="wide")

# Initialize | Intilize the session state
if 'layers' not in st.session_state:
    st.session_state['layers'] = {}

# Helper | Widgets | Function to create a highly probable unique widget key
def create_widget_key(parent, child, widget_type):
    parent = parent.replace(' ', '_').lower()
    child = child.replace(' ', '_').lower()
    widget_type = widget_type.replace(' ', '_').lower()
    return f"{parent}-{child}-{widget_type}"

# Modal | Widgets | Function to render radius modal with options form
@st.experimental_dialog("Radius options", width="large")
def render_radius_options(radius_name):
    radius_name = st.text_input('Radius name',
                                value=radius_name,
                                placeholder="Unique radius name",
                                help="Enter a unique name for the radius",
                                key=create_widget_key(radius_name, 'Radius name', 'text_input')
                                )
    radius_distance = st.slider('Radius distance',
                                min_value=1,
                                max_value=1000,
                                value=42,
                                step=1,
                                help="Select the radius distance for the circle",
                                key=create_widget_key(radius_name, 'Radius distance', 'slider')
                                )
    # Radius fill options
    row1 = st.columns([1, 1, 2])
    with row1[0]:
        radius_fill_toggle = st.toggle('Fill radius', 
                                        value=True, 
                                        help="Fill the radius circle", 
                                        key=create_widget_key(radius_name, 'Fill radius', 'toggle')
                                        )
    with row1[1]:
        radius_fill_color = st.color_picker('Radius fill color', 
                                            value="#3388ff", 
                                            help="Choose a fill color for the radius circle", 
                                            key=create_widget_key(radius_name, 'Radius fill color', 'color_picker')
                                            )
    with row1[2]:
        radius_fill_opacity = st.slider('Radius fill opacity', 
                                        min_value=0, 
                                        max_value=100, 
                                        value=100, 
                                        step=5, 
                                        help="Select the fill opacity for the radius circle", 
                                        key=create_widget_key(radius_name, 'Radius opacity', 'slider')
                                        )
    # Radius border options
    row2 = st.columns([1, 1, 2])
    with row2[0]:
        radius_border_weight = st.number_input('Radius border weight', 
                                            min_value=1, 
                                            max_value=10, 
                                            value=2, 
                                            step=1, 
                                            help="Select the border weight for the radius circle", 
                                            key=create_widget_key(radius_name, 'Radius border weight', 'number_input')
                                            )
    with row2[1]:
        radius_border_color = st.color_picker('Radius border color', 
                                                value="#3388ff", 
                                                help="Choose a border color for the radius circle", 
                                                key=create_widget_key(radius_name, 'Radius border color', 'color_picker')
                                                )
    with row2[2]:
        radius_border_opacity = st.slider('Radius border opacity', 
                                            min_value=0, 
                                            max_value=100, 
                                            value=100, 
                                            step=5, 
                                            help="Select the border opacity for the radius circle", 
                                            key=create_widget_key(radius_name, 'Radius border opacity', 'slider')
                                            )
    # Submit button
    submit_button = st.button('Add radius', key=create_widget_key(radius_name, 'Submit button', 'button'))
    if submit_button:
        st.toast(f"Added radius: {radius_name}", icon="➕")
        st.rerun()


# Sidebar | Function to add a new layer & expander
def add_layer(layer_name):
    with st.sidebar.expander(layer_name):
        layer_key_base = f"{layer_name.replace(' ', '_').lower()}"
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            color = st.color_picker('Marker color', 
                                value=st.session_state['layers'][layer_name]['color'],
                                help="Choose a color for the markers in this layer", 
                                key=f"{layer_key_base}-color-picker",
                                label_visibility="collapsed"
                                )
        with col2:
            new_name = st.text_input('Rename layer', 
                                    value=layer_name, 
                                    placeholder="Rename layer", 
                                    help="Enter a unique name for the layer", 
                                    key=f"{layer_key_base}-name-input", 
                                    label_visibility="collapsed"
                                    )
        cluster = st.toggle('Marker clustering', 
                            value=st.session_state['layers'][layer_name]['cluster'], 
                            help="Enable marker clustering for this layer",
                            key=f"{layer_key_base}-cluster-toggle"
                              )
        add_radius = st.button('➕ Add radius', key=f"{layer_key_base}-add-radius-button", 
                               help="Add a radius to the map", 
                               use_container_width=True
                               )
        if add_radius:
            render_radius_options(f"{layer_name}-Radius")

        col1, col2, col3 = st.columns([0.5, 0.2, 0.2])
        with col2:
            if st.button('🗑️', key=f"{layer_key_base}_remove_button"):
                remove_layer(layer_name)
                st.rerun()
        with col3:
            if st.button('🔃', key=f"{layer_key_base}-update-button", type="primary"):
                if new_name != layer_name and new_name in st.session_state['layers']:
                    st.warning("Layer name must be unique.")
                    return
                props = {'color': color, 'cluster': cluster}
                update_layer(layer_name, new_name, props)
                st.rerun()

# Sidebar | Function to update layer
def update_layer(layer_name, new_name, props):
    if new_name != layer_name:
        st.session_state['layers'][new_name] = st.session_state['layers'].pop(layer_name)
        st.toast(f"Updated layer: {layer_name} to {new_name}", icon="🔄")
    st.session_state['layers'][new_name].update(props)
    st.toast(f"Updated layer properties: {new_name}", icon="🔄")

# Sidebar | Function to remove a layer
def remove_layer(layer_name):
    del st.session_state['layers'][layer_name]
    st.toast(f"Deleted layer: {layer_name}", icon="🔄")

# Sidebar | Function to rerender sidebar layer expanders dynamically
def render_layer_expanders():
    for layer in st.session_state['layers'].keys():
        add_layer(layer)

# Sidebar | Render the sidebar
with st.sidebar:
    tab1, tab2 = st.tabs(["Add new layer", "Add new layer(s) from upload"])
    layer_name = tab1.text_input(label="Create new layer",
                                 key="new_layer_input",
                                 help="Enter a unique name for the layer",
                                 placeholder="Unique layer name",
                                 )
    if tab1.button("➕ Add layer", key="add_new_layer_button", type="primary", help="Add new layer", use_container_width=True):
        if layer_name is "":
            tab1.warning("Layer name cannot be empty.")
        elif layer_name in st.session_state['layers']:
            tab1.warning("Layer name must be unique.")
        else:
            st.session_state['layers'][layer_name] = {"markers": [], "color": "#3388ff", "cluster": False}
            st.toast(f"Added new layer: {layer_name}", icon="➕")

    if tab2.file_uploader("Add new layer(s) from upload", 
                          type=['csv'], 
                          accept_multiple_files=True, 
                          key="add_new_layers_upload", 
                          help="Upload CSV file(s) with columns 'name', 'latitude', and 'longitude' to add layers and markers to the map"
                          ):
        pass

    render_layer_expanders()


# Setting up the Folium map
m = folium.Map(location=[45.5236, -122.6750], zoom_start=5)
m.fit_bounds([[40, -130], [50, -60]])

# Adding markers to the map
for layer_name, layer_info in st.session_state['layers'].items():
    if layer_info['cluster']:
        marker_cluster = MarkerCluster().add_to(m)
        for marker in layer_info['markers']:
            folium.Marker(
                location=[marker[1], marker[2]],
                popup=marker[0],
                icon=folium.Icon(color=layer_info['color'])
            ).add_to(marker_cluster)
    else:
        for marker in layer_info['markers']:
            folium.Marker(
                location=[marker[1], marker[2]],
                popup=marker[0],
                icon=folium.Icon(color=layer_info['color'])
            ).add_to(m)

# Display the map

with st.container():
    st.markdown("""
        <style>
            iframe {
                width: 100%;
                min-height: 750px;
                height: 100%;
            }
        </style>
        """, unsafe_allow_html=True)
    Fullscreen().add_to(m)
    folium_static(m)

# # Main | Session State Expander - Render the current state of the session state for debugging
# with st.expander("session_state"):
#     st.write(st.session_state)