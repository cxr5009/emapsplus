import streamlit as st
import folium
from folium.plugins import MarkerCluster, Fullscreen
from streamlit_folium import folium_static
import pandas as pd

# Settings | Default
st.set_page_config(layout="wide")

# Helper | Initialize | Routine to itialize the session state
if 'intialized' not in st.session_state:
    st.session_state.layers = {}
    st.session_state.toast = []
    st.session_state.intialized = True

# Helper | Widgets | Function to create a highly probable unique widget key
def create_widget_key(parent, child, widget_type):
    parent = parent.replace(' ', '_').lower()
    child = child.replace(' ', '_').lower()
    widget_type = widget_type.replace(' ', '_').lower()
    return f"{parent}-{child}-{widget_type}"

# Helper | Toasts | Function to add toast message and icon to session state
def add_toast(message, icon):
    st.session_state.toast.append({'message': message, 'icon': icon})

# Helper | Toasts | Function to remove toast message and icon from session state
def remove_toast(index):
    st.session_state.toast.pop(index)

# Helper | Radius | Function to add a radius to a layer
def add_radius(layer_name, radius_name, props):
    if 'radii' not in st.session_state['layers'][layer_name]:
        st.session_state['layers'][layer_name]['radii'] = {}
    st.session_state['layers'][layer_name]['radii'][radius_name] = props
    return add_toast(f"Added radius: {radius_name}", icon="➕")

# Helper | Radius | Get next default radius name
def get_next_radius_name(layer_name):
    if 'radii' in st.session_state['layers'][layer_name]:
        radius_count = len(st.session_state['layers'][layer_name]['radii'])
        return f"{layer_name}-Radius{radius_count + 1}"
    else:
        return f"{layer_name}-Radius1"
    
# Helper | Radius | Function to update a radius in a layer
def update_radius(layer_name, radius_name, new_radius_name, props):
    if st.session_state['layers'][layer_name]['radii'][radius_name]:
        st.session_state['layers'][layer_name]['radii'][radius_name] = props
    return add_toast(f"Updated radius: {radius_name}", icon="🔄")

# Helper | Radius | Function to remove a radius from a layer
def remove_radius(layer_name, radius_name):
    if st.session_state['layers'][layer_name]['radii'][radius_name]:
        st.session_state['layers'][layer_name]['radii'].pop(radius_name)
    return add_toast(f"Removed radius: {radius_name}", icon="✖️")



# Modal | Widgets | Function to render radius modal with options form
@st.experimental_dialog("Radius options", width="large")
def render_radius_options(layer_name, radius_name=None):
    if not radius_name:
        action = "Add"
        radius_name = get_next_radius_name(layer_name)
        radius_props = {'distance': 42,
                        'fill': True,
                        'fill_color': "#3388ff",
                        'fill_opacity': 100,
                        'border_weight': 2,
                        'border_color': "#3388ff",
                        'border_opacity': 100
                        }
    else:
        action = "Update"
        radius_props = st.session_state['layers'][layer_name]['radii'][radius_name]
    new_radius_name = st.text_input('Radius name',
                                value=radius_name, 
                                placeholder="Unique radius name", 
                                help="Enter a unique name for the radius", 
                                key=create_widget_key(radius_name, 'Radius name', 'text_input')
                                )
    radius_distance = st.slider('Radius distance',
                                min_value=1, 
                                max_value=1000, 
                                value=radius_props['distance'], 
                                step=1, 
                                help="Select the radius distance for the circle", 
                                key=create_widget_key(radius_name, 'Radius distance', 'slider')
                                )
    # Radius fill options
    row1 = st.columns([1, 1, 2])
    with row1[0]:
        radius_fill = st.toggle('Fill radius', 
                                value=radius_props['fill'], 
                                help="Fill the radius circle", 
                                key=create_widget_key(radius_name, 'Fill radius', 'toggle')
                                )
    with row1[1]:
        radius_fill_color = st.color_picker('Radius fill color', 
                                            value=radius_props['fill_color'], 
                                            help="Choose a fill color for the radius circle", 
                                            key=create_widget_key(radius_name, 'Radius fill color', 'color_picker')
                                            )
    with row1[2]:
        radius_fill_opacity = st.slider('Radius fill opacity', 
                                        min_value=0, 
                                        max_value=100, 
                                        value=radius_props['fill_opacity'], 
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
                                               value=radius_props['border_weight'], 
                                               step=1, 
                                               help="Select the border weight for the radius circle", 
                                               key=create_widget_key(radius_name, 'Radius border weight', 'number_input')
                                               )
    with row2[1]:
        radius_border_color = st.color_picker('Radius border color', 
                                              value=radius_props['border_color'], 
                                              help="Choose a border color for the radius circle", 
                                              key=create_widget_key(radius_name, 'Radius border color', 'color_picker')
                                              )
    with row2[2]:
        radius_border_opacity = st.slider('Radius border opacity', 
                                          min_value=0, 
                                          max_value=100, 
                                          value=radius_props['border_opacity'], 
                                          step=5, 
                                          help="Select the border opacity for the radius circle", 
                                          key=create_widget_key(radius_name, 'Radius border opacity', 'slider')
                                          )
    # Submit button
    submit_button = st.button('Add radius', key=create_widget_key(radius_name, 'Submit button', 'button'))
    if submit_button:
        props = {'distance': radius_distance,
                 'fill': radius_fill,
                 'fill_color': radius_fill_color,
                 'fill_opacity': radius_fill_opacity,
                 'border_weight': radius_border_weight,
                 'border_color': radius_border_color,
                 'border_opacity': radius_border_opacity
                 }
        if new_radius_name != radius_name and new_radius_name in st.session_state['layers'][layer_name]['radii']:
            st.warning("Radius name must be unique.")
            return
        if action == "Add":
            add_radius(layer_name, radius_name, props)
            st.rerun()
        else:        
            update_radius(layer_name, radius_name, new_radius_name, props)
            st.rerun()

# Sidebar | Layer | Function to add a new layer & expander
def add_layer(layer_name):
    with st.sidebar.expander(layer_name):
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            layer_marker_color = st.color_picker('Marker color', 
                                                 value=st.session_state['layers'][layer_name]['color'],
                                                 help="Choose a color for the markers in this layer", 
                                                 key=create_widget_key(layer_name, 'Marker color', 'color_picker'),
                                                 label_visibility="collapsed"
                                                 )
        with col2:
            layer_rename_layer = st.text_input('Rename layer', 
                                               value=layer_name, 
                                               placeholder="Rename layer", 
                                               help="Enter a unique name for the layer", 
                                               key=create_widget_key(layer_name, 'Rename layer', 'text_input'),
                                               label_visibility="collapsed"
                                               )
        layer_marker_clustering = st.toggle('Marker clustering', 
                                            value=st.session_state['layers'][layer_name]['cluster'], 
                                            help="Enable marker clustering for this layer",
                                            key=create_widget_key(layer_name, 'Marker clustering', 'toggle')
                                            )
        for radius in st.session_state['layers'][layer_name].get('radii', {}):
            col1, col2, col3 = st.columns([0.8, 0.15, 0.15])
            with col1:
                radius_subheader = st.subheader(radius, anchor=False)
            with col2:
                radius_update_radius = st.button('✏️', key=create_widget_key(radius, 'Update radius', 'button'))
                if radius_update_radius:
                    render_radius_options(layer_name, radius)
            with col3:
                radius_remove_radius = st.button('✖️', key=create_widget_key(radius, 'Remove radius', 'button'))
                if radius_remove_radius:
                    remove_radius(layer_name, radius)
                    st.rerun()
        layer_add_radius = st.button('➕ Add radius',
                                     help="Add a radius to the map", 
                                     key=create_widget_key(layer_name, 'Add radius', 'button'),
                                     use_container_width=True
                                     )
        if layer_add_radius:
            render_radius_options(layer_name)

        col1, col2, col3 = st.columns([0.5, 0.2, 0.2])
        with col2:
            layer_remove_radius = st.button('🗑️', key=create_widget_key(layer_name, 'Remove radius', 'button'))
            if layer_remove_radius:
                remove_layer(layer_name)
                st.rerun()
        with col3:
            layer_update_radius = st.button('🔃', key=create_widget_key(layer_name, 'Update radius', 'button'))
            if layer_update_radius:
                if layer_rename_layer != layer_name and layer_rename_layer in st.session_state['layers']:
                    st.warning("Layer name must be unique.")
                    return
                props = {'color': layer_marker_color, 'cluster': layer_marker_clustering}
                update_layer(layer_name, layer_rename_layer, props)
                st.rerun()

# Sidebar | Function to update layer
def update_layer(layer_name, new_name, props):
    if new_name != layer_name:
        st.session_state['layers'][new_name] = st.session_state['layers'].pop(layer_name)
        add_toast(f"Renamed layer: {layer_name} to {new_name}", icon="🔄")
    st.session_state['layers'][new_name].update(props)
    add_toast(f"Updated layer properties: {new_name}", icon="🔄")

# Sidebar | Function to remove a layer
def remove_layer(layer_name):
    del st.session_state['layers'][layer_name]
    add_toast(f"Deleted layer: {layer_name}", icon="🔄")

# Sidebar | Function to rerender sidebar layer expanders dynamically
def render_layer_expanders():
    for layer in st.session_state['layers'].keys():
        add_layer(layer)

# Sidebar | Render | Render the sidebar
with st.sidebar:
    tab1, tab2 = st.tabs(["Add new layer", "Add new layer(s) from upload"])
    layer_name = tab1.text_input(label="Create new layer",
                                 key="new_layer_input",
                                 help="Enter a unique name for the layer",
                                 placeholder="Unique layer name",
                                 )
    if tab1.button("➕ Add layer", key="add_new_layer_button", type="primary", help="Add new layer", use_container_width=True):
        if layer_name == "":
            tab1.warning("Layer name cannot be empty.")
        elif layer_name in st.session_state['layers']:
            tab1.warning("Layer name must be unique.")
        else:
            st.session_state['layers'][layer_name] = {"markers": [], "color": "#3388ff", "cluster": False}
            add_toast(f"Added new layer: {layer_name}", icon="➕")

    if tab2.file_uploader("Add new layer(s) from upload", 
                          type=['csv'], 
                          accept_multiple_files=True, 
                          key="add_new_layers_upload", 
                          help="Upload CSV file(s) with columns 'name', 'latitude', and 'longitude' to add layers and markers to the map"
                          ):
        pass

    render_layer_expanders()

# Main | Toasts | Render any toast messages
if st.session_state.toast:
    # Loop through any toasts in the session state, display, then remove them
    for index, toast in enumerate(st.session_state.toast):
        st.toast(toast['message'], icon=toast['icon'])
        remove_toast(index)


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

# Main | Session State Expander - Render the current state of the session state for debugging
with st.expander("session_state"):
    st.write(st.session_state)