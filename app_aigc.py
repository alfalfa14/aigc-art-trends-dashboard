# The making of this project used app.py from Week 7 of DIGS 20004 as a main reference for the structure.
# I was in charge of all the decision-making of the contents to present, and AI was consulted with to achieve the visualizations I could not figure out myself.
"""
AI Art Style Trends Dashboard
------------------------------

This app visualizes how AI-generated art styles have shifted from 2022 to 2024, using the ai_generated_art_trends_2024.csv dataset.

Run with:
    python3 app_aigc.py

Then open:
    http://127.0.0.1:8050/
"""

# ------------------------------------------------------------
# 1. IMPORT LIBRARIES
# ------------------------------------------------------------
from pathlib import Path
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px


# ------------------------------------------------------------
# 2. DEFINE PROJECT PATHS
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "ai_generated_art_trends_2024.csv"


# ------------------------------------------------------------
# 3. LOAD DATA
# ------------------------------------------------------------
# Consulted with by showing the "load data" section from the app.py from Week 7 Module, and learned the formating logistics.
df = pd.read_csv(DATA_FILE)
df["Creation_Date"] = pd.to_datetime(df["Creation_Date"])
df["Year"] = df["Creation_Date"].dt.year
# I needed quarterly labels so consulted with AI to use dt.to_period("Q").astype(str) to convert dates into strings like "2022Q3" for the RangeSlider marks.
df["Quarter"] = df["Creation_Date"].dt.to_period("Q").astype(str)

ALL_STYLES = sorted(df["Art_Style"].unique())
ALL_REGIONS = sorted(df["Region"].unique())
ALL_QUARTERS = sorted(df["Quarter"].unique())
QUARTER_MARKS = {i: q for i, q in enumerate(ALL_QUARTERS) if i % 2 == 0 or i == len(ALL_QUARTERS) - 1}


# ------------------------------------------------------------
# 4. CHART FUNCTIONS
# ------------------------------------------------------------
def create_style_trend_figure(filtered, selected_styles):
    """
    Line chart: share of each selected style per year within the filtered period.
    """
    sub = filtered[filtered["Art_Style"].isin(selected_styles)]

    style_year = (
        # Consulted with AI on how to count artworks per Year x Art_Style combination.
        # AI suggested groupby(）to summarize artwork counts by year and style as a way to get a clean count table without writing a loop.
        sub.groupby(["Year", "Art_Style"])
        .size()
        .reset_index(name="Count")
    )

    style_year["Percentage"] = (
        # Consulted with AI on how to calculate each style's percentage share within each year. 
        # AI suggested transform(lambda x: x / x.sum() * 100) because it keeps the original row count while adding the percentage as a new column.
        style_year.groupby("Year")["Count"]
        .transform(lambda x: x / x.sum() * 100)
        .round(1)
    )

    fig = px.line(
        style_year,
        x="Year",
        y="Percentage",
        color="Art_Style",
        markers=True,
        title="Share of AI Artworks by Style per Year (%)",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )

    fig.update_traces(line={"width": 2.5}, marker={"size": 8})

    fig.update_layout(
        template="plotly_white",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.92)",
        margin={"l": 40, "r": 25, "t": 70, "b": 45},
        legend_title_text="Art Style",
        yaxis_title="Percentage (%)",
        xaxis={"tickmode": "linear", "dtick": 1, "title": "Year"},
        hovermode="x unified",
    )

    return fig

# Consulted with AI how to make a heatmap showing artwork count for each Region x Art_Style combination. 
# AI suggested using groupby to get the counts, pivot() to reshape the data into a matrix, and px.imshow() to render it as a heatmap with a blue color scale.
def create_heatmap_figure(filtered):
    """
    Heatmap: artwork count for each Region x Art_Style pair.
    """
    heat_data = (
        filtered.groupby(["Region", "Art_Style"])
        .size()
        .reset_index(name="Count")
    )
    # Consulted with AI on how to reshape the grouped data into a matrix for the heatmap.
    # AI suggested pivot(index="Region", columns="Art_Style", values="Count") followed by fillna(0) to fill missing combinations.
    heat_pivot = heat_data.pivot(
        index="Region", columns="Art_Style", values="Count"
    ).fillna(0)

    # Consulted with AI how to add a color scale legend to the heatmap.
    # AI suggested setting color_continuous_scale="Blues" in px.imshow() and adding coloraxis_colorbar with a title in update_layout().
    fig = px.imshow(
        heat_pivot,
        title="Artwork Count by Region and Style",
        color_continuous_scale="Blues",
        aspect="auto",
    )

    fig.update_layout(
        template="plotly_white",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        paper_bgcolor="rgba(0,0,0,0)",
        margin={"l": 40, "r": 25, "t": 70, "b": 45},
        xaxis_title="Art Style",
        yaxis_title="Region",
        coloraxis_colorbar={"title": "Count"},
    )

    return fig

# Consulted with AI how to build a bubble map showing artwork count and average popularity score by region. 
# AI suggested using px.scatter_geo() with manually defined lat/lon coordinates for each region, mapping bubble size to Count and color to Avg_Score, and using update_geos() to style the land, ocean, and country borders.
def create_bubble_map_figure(filtered):
    """
    Bubble map: one circle per region, sized by artwork count,
    colored by average Popularity_Score. Hover shows both values.
    """
    region_coords = {
        "Africa":        {"lat":  2.0, "lon":  21.0},
        "Asia":          {"lat": 34.0, "lon":  90.0},
        "Europe":        {"lat": 54.0, "lon":  15.0},
        "North America": {"lat": 45.0, "lon": -95.0},
        "Oceania":       {"lat": -25.0, "lon": 135.0},
        "South America": {"lat": -15.0, "lon": -55.0},
    }

    summary = (
        filtered.groupby("Region")
        .agg(
            Count=("Artwork_ID", "count"),
            Avg_Score=("Popularity_Score", "mean"),
        )
        .round(1)
        .reset_index()
    )

    summary["lat"] = summary["Region"].map(
        lambda r: region_coords.get(r, {}).get("lat", 0)
    )
    summary["lon"] = summary["Region"].map(
        lambda r: region_coords.get(r, {}).get("lon", 0)
    )

    fig = px.scatter_geo(
        summary,
        lat="lat",
        lon="lon",
        size="Count",
        color="Avg_Score",
        hover_name="Region",
        hover_data={"Count": True, "Avg_Score": True, "lat": False, "lon": False},
        title="AI Artwork Volume and Popularity by Region<br><sup>Bubble size = number of artworks · Color = average Popularity Score (0–5000)</sup>",
        color_continuous_scale="Teal",
        size_max=60,
        projection="natural earth",
    )

    fig.update_geos(
        showland=True,
        landcolor="rgb(244, 238, 224)",
        showocean=True,
        oceancolor="rgb(216, 231, 239)",
        showcountries=True,
        countrycolor="rgb(180, 180, 180)",
        showcoastlines=True,
        coastlinecolor="rgb(120, 120, 120)",
    )

    fig.update_layout(
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        paper_bgcolor="rgba(0,0,0,0)",
        margin={"l": 0, "r": 0, "t": 60, "b": 0},
        height=500,
        coloraxis_colorbar={"title": "Avg Score"},
    )

    return fig


# ------------------------------------------------------------
# 5. DASH APP CREATION
# ------------------------------------------------------------
# Consulted with AI on how to prevent callback errors when components inside tabs are not yet visible on the page.
# AI suggested adding suppress_callback_exceptions=True to Dash(__name__).
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server


# ------------------------------------------------------------
# 6. APP LAYOUT
# ------------------------------------------------------------
app.layout = html.Div(
    id="app-shell",
    className="app-shell theme-light",
    children=[
        html.Div(
            className="hero",
            children=[
                html.P("DIGS 20004 Final Project", className="eyebrow"),
                #Consulted with AI for the method of letter-spacing.
                html.H1("AI-Generated Art Style Trends", style={"letterSpacing": "0.01em"}),
                html.P(
                    "How have different AI-generated art styles evolved from 2022 to 2024?",
                    className="hero-subtitle",
                ),
            ],
        ),
        html.Div(
            className="main-grid",
            children=[
                # ------------------------------------------------
                # LEFT CONTROL PANEL
                # ------------------------------------------------
                html.Aside(
                    className="control-panel",
                    children=[
                        html.H2("Controls"),
                        html.P(
                            "Drag the slider to filter all charts "
                            "by a quarter range."
                        ),
                        html.Label("Time range (by quarter)", className="control-label"),
                        dcc.RangeSlider(
                            id="quarter-range",
                            min=0,
                            max=len(ALL_QUARTERS) - 1,
                            step=1,
                            value=[0, len(ALL_QUARTERS) - 1],
                            marks=QUARTER_MARKS,
                            allowCross=False,
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                        html.Div(
                            className="tip-card",
                            children=[
                                html.H3("About this dashboard"),
                                html.P(
                                    "The time range above filters all charts. "
                                    "Inside the first chart, use the style checklist "
                                    "to show or hide individual art styles."
                                ),
                            ],
                        ),
                    ],
                ),
                # ------------------------------------------------
                # MAIN CONTENT AREA
                # ------------------------------------------------
                html.Main(
                    className="content-panel",
                    children=[
                        html.Section(
                            className="narrative-card",
                            children=[
                                html.H2("Background"),
                                dcc.Markdown(
                                    """
                                    This dashboard visualizes a dataset of AI-generated artworks
                                    collected between 2022 and 2024. Each record represents one
                                    artwork tagged with a style, a region of origin, and a
                                    popularity score.

                                    Three questions guide the visualizations below:

                                    - **Which styles grew or declined** across the period you selected?
                                    - **How are styles distributed** across regions?
                                    - **How popular are AI artworks** across the regions?
                                    """
                                ),
                            ],
                        ),
                        html.Section(
                            className="folder-card",
                            children=[
                                html.Div(
                                    className="folder-heading",
                                    children=[
                                        html.H2("Visualizations"),
                                        html.P("Choose a tab to switch between charts."),
                                    ],
                                ),
                                dcc.Tabs(
                                    id="plot-tabs",
                                    value="trend",
                                    className="folder-tabs",
                                    children=[
                                        dcc.Tab(
                                            label="Style trend",
                                            value="trend",
                                            className="folder-tab",
                                            selected_className="folder-tab--selected",
                                        ),
                                        dcc.Tab(
                                            label="Region × Style",
                                            value="heatmap",
                                            className="folder-tab",
                                            selected_className="folder-tab--selected",
                                        ),
                                        dcc.Tab(
                                            label="World map",
                                            value="worldmap",
                                            className="folder-tab",
                                            selected_className="folder-tab--selected",
                                        ),
                                    ],
                                ),
                                html.Div(id="tab-content", className="tab-content"),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


# ------------------------------------------------------------
# 7. CALLBACK: RENDER TAB CONTENT
# ------------------------------------------------------------


@app.callback(Output("tab-content", "children"), Input("plot-tabs", "value"), Input("quarter-range", "value"))
def render_tab(active_tab, quarter_range):
    start_q = ALL_QUARTERS[quarter_range[0]]
    end_q = ALL_QUARTERS[quarter_range[1]]
    filtered = df[(df["Quarter"] >= start_q) & (df["Quarter"] <= end_q)]

    if active_tab == "trend":
        return html.Div(
            [
                dcc.Markdown(
                    """
                    ### Style share over time

                    Each line shows what percentage of that year's total artworks
                    belonged to a given style. Use the checklist on the right to
                    add or remove styles from the chart.
                    """,
                    className="plot-narrative",
                ),
                html.Div(
                    # Consulted with AI how to put the checklist and the chart side by side so the checklist takes up less space and the chart stretches to fill the remaining width
                    style={"display": "flex", "gap": "16px", "alignItems": "flex-start"},
                    children=[
                        html.Div(
                            style={"minWidth": "150px"},
                            children=[
                                #Consulted with AI how to place the style checklist inside the chart tab rather than the left panel, so it only appears when the trend chart is active.
                                html.Label("Art styles", className="control-label"),
                                dcc.Checklist(
                                    id="style-selector",
                                    options=[{"label": s, "value": s} for s in ALL_STYLES],
                                    value=ALL_STYLES[:5],
                                    inputStyle={"marginRight": "6px"},
                                    labelStyle={
                                        "display": "block",
                                        "marginBottom": "4px",
                                        "fontSize": "13px",
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            style={"flex": "1", "minWidth": "0"},
                            children=[
                                dcc.Graph(
                                    id="style-trend-chart",
                                    className="plot-frame",
                                ),
                            ],
                        ),
                    ],
                ),
                dcc.Markdown(
                    "**Reading the chart:** a rising line means the style became more "
                    "prominent relative to others over the selected period.",
                    className="plot-narrative after",
                ),
            ]
        )


    if active_tab == "heatmap":
        return html.Div(
            [
                dcc.Markdown(
                    """
                    ### Artwork count by region and style

                    Each cell shows how many artworks from that region belong to
                    that style. Darker blue means more artworks.
                    """,
                    className="plot-narrative",
                ),
                dcc.Graph(
                    figure=create_heatmap_figure(filtered),
                    className="plot-frame",
                ),
                dcc.Markdown(
                    "**Reading the chart:** look across a row to see which styles "
                    "a region favors, or down a column to see which regions produce "
                    "the most of a given style.",
                    className="plot-narrative after",
                ),
            ]
        )

    if active_tab == "worldmap":
        return html.Div(
            [
                dcc.Markdown(
                    """
                    ### AI artwork distribution across regions

                    Each bubble represents one region. Bubble size shows the number
                    of artworks produced in that region during the selected period.
                    Color shows the average Popularity Score — a composite measure of
                    likes, shares, and views recorded on the platform where the artwork
                    was posted. Scores range from 0 to 5000; higher means more engagement.
                    Darker bubbles indicate higher average scores.
                    Hover over a bubble to see the exact values.
                    """,
                    className="plot-narrative",
                ),
                dcc.Graph(
                    figure=create_bubble_map_figure(filtered),
                    className="plot-frame map-frame",
                ),
                dcc.Markdown(
                    "**Reading the map:** larger bubbles mean more artworks from that region. "
                    "Darker color means higher average popularity score.",
                    className="plot-narrative after",
                ),
            ]
        )

    return html.P("Select a tab.")


# ------------------------------------------------------------
# 8. CALLBACK: UPDATE TREND CHART
# ------------------------------------------------------------
@app.callback(Output("style-trend-chart", "figure"),Input("style-selector", "value"), Input("quarter-range", "value"))
def update_trend_chart(selected_styles, quarter_range):
    if not selected_styles:
        return {}
    start_q = ALL_QUARTERS[quarter_range[0]]
    end_q = ALL_QUARTERS[quarter_range[1]]
    filtered = df[(df["Quarter"] >= start_q) & (df["Quarter"] <= end_q)]
    return create_style_trend_figure(filtered, selected_styles)


# ------------------------------------------------------------
# 9. RUN THE APP
# ------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)