import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go

def load_data():
    # Load the dataset
    df = pd.read_csv("trash.csv")
    return df

def filter_data(df, neighborhood, street=""):
    neighborhood_filter = df["mailing_neighborhood"] == neighborhood
    street_filter = df["full_address"].str.contains(street, case=False)
    filtered_data = df[neighborhood_filter & street_filter]
    return filtered_data

def create_pydeck_map(filtered_data):
    map = pdk.Deck(
        map_style="mapbox://styles/mapbox/streets-v11",
        initial_view_state=pdk.ViewState(
            latitude=filtered_data["y_coord"].mean(),
            longitude=filtered_data["x_coord"].mean(),
            zoom=14,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=filtered_data,
                get_position=["x_coord", "y_coord"],
                auto_highlight=True,
                radius=50,
                extruded=True,
                pickable=True,
                elevation_scale=4,
                elevation_range=[0, 1000],
                get_fill_color="[255, (1 - count / 100) * 255, 0]",
                get_line_color=[0, 0, 0],
                tooltip={"text": "Trash Locations: {count}"}
            ),
        ],
    )
    return map

def create_scatterplot(filtered_data):
    scatterplot = go.Figure()
    for day in filtered_data["trashday"].unique():
        day_data = filtered_data[filtered_data["trashday"] == day]
        scatterplot.add_trace(go.Scatter(
            x=day_data["full_address"],
            y=[day] * len(day_data),
            mode='markers',
            marker=dict(size=10),
            name=day
        ))

    scatterplot.update_layout(
        xaxis=dict(title="Street Name"),
        yaxis=dict(title="Trash Pick Up Day"),
        title="Scatterplot: Trash Pick Up Day by Street Name",
        xaxis_tickangle=-45,
    )
    return scatterplot

def create_bar_chart(df):
    trash_pick_up_count = df.groupby("mailing_neighborhood")["sam_address_id"].count().reset_index()
    fig = go.Figure(data=[go.Bar(x=trash_pick_up_count["mailing_neighborhood"], y=trash_pick_up_count["sam_address_id"])])
    fig.update_layout(
        xaxis=dict(title="Neighborhood"),
        yaxis=dict(title="Count of Trash Pick Ups"),
        title="Frequency of Trash Pick Ups by Neighborhood"
    )
    return fig

def create_pie_chart(trash_days_distribution):
    fig = go.Figure(data=[go.Pie(labels=trash_days_distribution.index, values=trash_days_distribution.values)])
    fig.update_layout(title="Distribution of Trash Days")
    return fig


def set_custom_theme():
    custom_theme = '''
        <style>
        [theme]
        primaryColor="#5acb6b"
        backgroundColor="#22870b"
        secondaryBackgroundColor="#181818"
        textColor="#f0f1f3"

        </style>
    '''
    st.markdown(custom_theme, unsafe_allow_html=True)
def main():
    # Set the custom theme
    set_custom_theme()

    # Load the dataset
    df = load_data()

    # Create a sidebar with some widgets
    st.sidebar.title("Trash Schedule Options")
    neighborhood = st.sidebar.selectbox("Select your preferred neighborhood", df["mailing_neighborhood"].unique())
    street = st.sidebar.text_input("Enter the street name (e.g., A St)")

    # Filter data by neighborhood and street name
    filtered_data = filter_data(df, neighborhood, street)

    # Display the title and the dataset on the main page
    st.title("Trash Schedule of Boston Neighborhoods")
    st.write("Welcome! This app displays the trash pickup schedule of neighborhoods in Boston ")

    # Display the filtered data
    if not filtered_data.empty:
        st.subheader(f"Data of {neighborhood} Neighborhood and {street} Street")
        st.write(filtered_data)

        # Create and display the PyDeck map
        st.subheader("Density of Trash Pick Up")
        map = create_pydeck_map(filtered_data)
        st.pydeck_chart(map)

        # Create and display the Scatterplot
        st.subheader("Trash Pick Up Day by Street Name")
        scatterplot = create_scatterplot(filtered_data)
        st.plotly_chart(scatterplot)

        # Create and display the Bar Chart
        st.subheader("Frequency of Trash Pick Ups by Neighborhood")
        bar_chart = create_bar_chart(df)
        st.plotly_chart(bar_chart)

        # Create and display the Pie Chart
        st.subheader("Distribution of Trash Days")
        trash_days_distribution = filtered_data["trashday"].value_counts()
        pie_chart = create_pie_chart(trash_days_distribution)
        st.plotly_chart(pie_chart)

    else:
        st.info("No data available for the selected neighborhood and street.")



if __name__ == "__main__":
    main()
