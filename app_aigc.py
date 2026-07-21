"""
AIGC Atlas — AI-Generated Art Style Trends
"""

from pathlib import Path

import pandas as pd
import plotly.express as px

from dash import (
    Dash,
    html,
    dcc,
    Input,
    Output,
    State,
    ctx,
)


# ------------------------------------------------------------
# DATA
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "ai_generated_art_trends_2024.csv"

df = pd.read_csv(DATA_FILE)

df["Creation_Date"] = pd.to_datetime(df["Creation_Date"])
df["Year"] = df["Creation_Date"].dt.year
df["Quarter"] = (
    df["Creation_Date"]
    .dt.to_period("Q")
    .astype(str)
)

ALL_STYLES = sorted(df["Art_Style"].dropna().unique())
ALL_REGIONS = sorted(df["Region"].dropna().unique())
ALL_YEARS = sorted(df["Year"].dropna().unique())
ALL_QUARTERS = sorted(df["Quarter"].dropna().unique())

PALETTE = px.colors.qualitative.Pastel


# ------------------------------------------------------------
# SHARED CHART STYLE
# ------------------------------------------------------------

def apply_style(fig):
    """
    Apply the shared light glass-dashboard style to Plotly charts.
    """

    fig.update_layout(
        template="plotly_white",

        font={
            "family": "Inter, Arial, sans-serif",
            "size": 12,
            "color": "#343242",
        },

        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(255, 255, 255, 0.10)",

        margin={
            "l": 55,
            "r": 30,
            "t": 64,
            "b": 50,
        },

        hovermode="x unified",

        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {
                "size": 10,
                "color": "#454252",
            },
            "bgcolor": "rgba(255, 255, 255, 0)",
        },

        hoverlabel={
            "bgcolor": "rgba(250, 250, 253, 0.96)",
            "bordercolor": "rgba(50, 50, 70, 0.14)",
            "font": {
                "color": "#292735",
                "family": "Inter, Arial, sans-serif",
            },
        },

        transition={
            "duration": 350,
            "easing": "cubic-in-out",
        },
    )

    fig.update_xaxes(
        gridcolor="rgba(44, 42, 61, 0.08)",
        linecolor="rgba(44, 42, 61, 0.14)",
        tickfont={
            "color": "#625f70",
            "size": 11,
        },
        title_font={
            "color": "#454252",
            "size": 12,
        },
        zeroline=False,
        showline=True,
    )

    fig.update_yaxes(
        gridcolor="rgba(44, 42, 61, 0.08)",
        linecolor="rgba(44, 42, 61, 0.14)",
        tickfont={
            "color": "#625f70",
            "size": 11,
        },
        title_font={
            "color": "#454252",
            "size": 12,
        },
        zeroline=False,
        showline=True,
    )

    return fig


# ------------------------------------------------------------
# FILTER DATA
# ------------------------------------------------------------

def get_filtered(year, region, style):
    """
    Return a filtered copy of the original dataset.
    """

    filtered_df = df.copy()

    if year and "All" not in year:
        filtered_df = filtered_df[
            filtered_df["Year"].isin(
                [int(y) for y in year]
            )
        ]

    if region and "All" not in region:
        filtered_df = filtered_df[
            filtered_df["Region"].isin(region)
        ]

    if style and "All" not in style:
        filtered_df = filtered_df[
            filtered_df["Art_Style"].isin(style)
        ]

    return filtered_df


# ------------------------------------------------------------
# EMPTY CHART
# ------------------------------------------------------------

def create_empty_chart(message="No data available for this selection."):
    """
    Create a blank chart when the selected filters return no rows.
    """

    fig = px.scatter()

    fig.update_layout(
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": message,
                "x": 0.5,
                "y": 0.5,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "family": "Inter, Arial, sans-serif",
                    "size": 18,
                    "color": "#5f5b6d",
                },
            }
        ],
        margin={
            "l": 20,
            "r": 20,
            "t": 20,
            "b": 20,
        },
    )

    return fig


# ------------------------------------------------------------
# CHART 1: STYLE TREND
# ------------------------------------------------------------

def create_style_trend(filtered_df, selected_styles):
    """
    Show the percentage share of each art style by year.
    """

    if filtered_df.empty:
        return create_empty_chart()

    style_year = (
        filtered_df
        .groupby(["Year", "Art_Style"])
        .size()
        .reset_index(name="Count")
    )

    if style_year.empty:
        return create_empty_chart()

    style_year["Percentage"] = (
        style_year
        .groupby("Year")["Count"]
        .transform(
            lambda values: values / values.sum() * 100
        )
        .round(1)
    )

    if selected_styles and "All" not in selected_styles:
        style_year = style_year[
            style_year["Art_Style"].isin(selected_styles)
        ]

    fig = px.line(
        style_year,
        x="Year",
        y="Percentage",
        color="Art_Style",
        markers=True,
        color_discrete_sequence=PALETTE,
    )

    fig.update_traces(
        line={
            "width": 2.8,
        },
        marker={
            "size": 8,
            "line": {
                "width": 1.5,
                "color": "rgba(255, 255, 255, 0.85)",
            },
        },
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Year: %{x}<br>"
            "Share: %{y:.1f}%"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        xaxis={
            "tickmode": "linear",
            "dtick": 1,
            "title": "Year",
        },
        yaxis={
            "title": "Share (%)",
            "ticksuffix": "%",
        },
        legend_title_text="Style",
    )

    return apply_style(fig)


# ------------------------------------------------------------
# CHART 2: STYLE POPULARITY
# ------------------------------------------------------------

def create_style_popularity(filtered_df, selected_styles):
    """
    Show average popularity score for each art style.
    """

    if filtered_df.empty:
        return create_empty_chart()

    style_popularity = (
        filtered_df
        .groupby("Art_Style")["Popularity_Score"]
        .mean()
        .round(1)
        .reset_index()
        .sort_values(
            "Popularity_Score",
            ascending=True,
        )
    )

    if selected_styles and "All" not in selected_styles:
        style_popularity = style_popularity[
            style_popularity["Art_Style"].isin(selected_styles)
        ]

    if style_popularity.empty:
        return create_empty_chart()

    fig = px.bar(
        style_popularity,
        x="Popularity_Score",
        y="Art_Style",
        orientation="h",
        color="Popularity_Score",
        color_continuous_scale=[
            "#dfe8f8",
            "#c9c2e8",
            "#aa8bd4",
            "#7255a8",
        ],
    )

    fig.update_traces(
        marker_line_width=0,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Average score: %{x:.1f}"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        coloraxis_showscale=False,
        yaxis_title="",
        xaxis_title="Average Popularity Score",
        bargap=0.28,
    )

    return apply_style(fig)


# ------------------------------------------------------------
# CHART 3: REGION BAR
# ------------------------------------------------------------

def create_region_bar(filtered_df, selected_regions):
    """
    Show artwork volume and average popularity by region.
    """

    if filtered_df.empty:
        return create_empty_chart()

    region_data = (
        filtered_df
        .groupby("Region")
        .agg(
            Count=("Artwork_ID", "count"),
            Avg_Score=("Popularity_Score", "mean"),
        )
        .round(1)
        .reset_index()
        .sort_values(
            "Count",
            ascending=False,
        )
    )

    if selected_regions and "All" not in selected_regions:
        region_data = region_data[
            region_data["Region"].isin(selected_regions)
        ]

    if region_data.empty:
        return create_empty_chart()

    fig = px.bar(
        region_data,
        x="Region",
        y="Count",
        color="Avg_Score",
        color_continuous_scale=[
            "#d9eff2",
            "#a8d6d8",
            "#70b0b4",
            "#397b85",
        ],
        hover_data={
            "Avg_Score": True,
            "Count": True,
        },
    )

    fig.update_traces(
        marker_line_width=0,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Artworks: %{y:,}<br>"
            "Average score: %{marker.color:.1f}"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        xaxis_title="Region",
        yaxis_title="Number of Artworks",
        bargap=0.24,
        coloraxis_colorbar={
            "title": "Avg Score",
            "thickness": 10,
            "len": 0.65,
            "outlinewidth": 0,
            "tickfont": {
                "color": "#5f5b6d",
            },
            "title_font": {
                "color": "#454252",
            },
        },
    )

    return apply_style(fig)


# ------------------------------------------------------------
# CHART 4: HEATMAP
# ------------------------------------------------------------

def create_heatmap(filtered_df):
    """
    Show the relationship between region and art style.
    """

    if filtered_df.empty:
        return create_empty_chart()

    heatmap_data = (
        filtered_df
        .groupby(["Region", "Art_Style"])
        .size()
        .reset_index(name="Count")
    )

    if heatmap_data.empty:
        return create_empty_chart()

    pivot_table = heatmap_data.pivot(
        index="Region",
        columns="Art_Style",
        values="Count",
    ).fillna(0)

    fig = px.imshow(
        pivot_table,
        color_continuous_scale=[
            "#edf3fb",
            "#d2ddf3",
            "#aebce2",
            "#8279bc",
            "#584982",
        ],
        aspect="auto",
        text_auto=False,
    )

    fig.update_traces(
        hovertemplate=(
            "<b>Region:</b> %{y}<br>"
            "<b>Style:</b> %{x}<br>"
            "<b>Artworks:</b> %{z:,}"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        xaxis_title="Art Style",
        yaxis_title="Region",
        coloraxis_colorbar={
            "title": "Count",
            "thickness": 10,
            "len": 0.65,
            "outlinewidth": 0,
            "tickfont": {
                "color": "#5f5b6d",
            },
            "title_font": {
                "color": "#454252",
            },
        },
    )

    styled_fig = apply_style(fig)

    styled_fig.update_xaxes(
        tickangle=-28,
    )

    return styled_fig


# ------------------------------------------------------------
# CHART 5: WORLD MAP
# ------------------------------------------------------------

def create_bubble_map(filtered_df, selected_regions):
    """
    Show artwork count and average popularity on a global map.
    """

    if filtered_df.empty:
        return create_empty_chart()

    coordinates = {
        "Africa": {
            "lat": 2.0,
            "lon": 21.0,
        },
        "Asia": {
            "lat": 34.0,
            "lon": 90.0,
        },
        "Europe": {
            "lat": 54.0,
            "lon": 15.0,
        },
        "North America": {
            "lat": 45.0,
            "lon": -95.0,
        },
        "Oceania": {
            "lat": -25.0,
            "lon": 135.0,
        },
        "South America": {
            "lat": -15.0,
            "lon": -55.0,
        },
    }

    map_data = (
        filtered_df
        .groupby("Region")
        .agg(
            Count=("Artwork_ID", "count"),
            Avg_Score=("Popularity_Score", "mean"),
        )
        .round(1)
        .reset_index()
    )

    if selected_regions and "All" not in selected_regions:
        map_data = map_data[
            map_data["Region"].isin(selected_regions)
        ]

    if map_data.empty:
        return create_empty_chart()

    map_data["lat"] = map_data["Region"].map(
        lambda region: coordinates.get(
            region,
            {},
        ).get(
            "lat",
            0,
        )
    )

    map_data["lon"] = map_data["Region"].map(
        lambda region: coordinates.get(
            region,
            {},
        ).get(
            "lon",
            0,
        )
    )

    fig = px.scatter_geo(
        map_data,
        lat="lat",
        lon="lon",
        size="Count",
        color="Avg_Score",
        hover_name="Region",
        hover_data={
            "Count": True,
            "Avg_Score": True,
            "lat": False,
            "lon": False,
        },
        color_continuous_scale=[
            "#d9eff2",
            "#9bcdd0",
            "#61a7ac",
            "#397780",
        ],
        size_max=66,
        projection="natural earth",
    )

    fig.update_traces(
        marker={
            "line": {
                "width": 2,
                "color": "rgba(255, 255, 255, 0.8)",
            },
            "opacity": 0.9,
        },
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Artworks: %{customdata[0]:,}<br>"
            "Average score: %{customdata[1]:.1f}"
            "<extra></extra>"
        ),
    )

    fig.update_geos(
        showland=True,
        landcolor="rgba(222, 228, 239, 0.82)",

        showocean=True,
        oceancolor="rgba(196, 216, 240, 0.42)",

        showcountries=True,
        countrycolor="rgba(76, 78, 98, 0.20)",

        showcoastlines=True,
        coastlinecolor="rgba(76, 78, 98, 0.18)",

        showframe=False,
        bgcolor="rgba(0, 0, 0, 0)",

        lataxis={
            "showgrid": False,
        },

        lonaxis={
            "showgrid": False,
        },
    )

    fig.update_layout(
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",

        margin={
            "l": 0,
            "r": 0,
            "t": 25,
            "b": 0,
        },

        font={
            "family": "Inter, Arial, sans-serif",
            "size": 12,
            "color": "#343242",
        },

        coloraxis_colorbar={
            "title": "Avg Score",
            "thickness": 10,
            "len": 0.65,
            "outlinewidth": 0,
            "tickfont": {
                "color": "#5f5b6d",
            },
            "title_font": {
                "color": "#454252",
            },
        },

        hoverlabel={
            "bgcolor": "rgba(250, 250, 253, 0.96)",
            "bordercolor": "rgba(50, 50, 70, 0.14)",
            "font": {
                "color": "#292735",
                "family": "Inter, Arial, sans-serif",
            },
        },
    )

    return fig


# ------------------------------------------------------------
# CHART 6: PLATFORM BAR
# ------------------------------------------------------------

def create_platform_bar(filtered_df):
    """
    Show artwork volume and popularity by platform.
    """

    if filtered_df.empty:
        return create_empty_chart()

    platform_data = (
        filtered_df
        .groupby("Platform")
        .agg(
            Count=("Artwork_ID", "count"),
            Avg_Score=("Popularity_Score", "mean"),
        )
        .round(1)
        .reset_index()
        .sort_values(
            "Count",
            ascending=False,
        )
    )

    if platform_data.empty:
        return create_empty_chart()

    fig = px.bar(
        platform_data,
        x="Platform",
        y="Count",
        color="Avg_Score",
        color_continuous_scale=[
            "#eee8f7",
            "#d1bee6",
            "#aa8bd0",
            "#74519d",
        ],
        hover_data={
            "Avg_Score": True,
            "Count": True,
        },
    )

    fig.update_traces(
        marker_line_width=0,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Artworks: %{y:,}<br>"
            "Average score: %{marker.color:.1f}"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        xaxis_title="Platform",
        yaxis_title="Number of Artworks",
        bargap=0.24,
        coloraxis_colorbar={
            "title": "Avg Score",
            "thickness": 10,
            "len": 0.65,
            "outlinewidth": 0,
        },
    )

    return apply_style(fig)


# ------------------------------------------------------------
# CHART 7: TOOLS BAR
# ------------------------------------------------------------

def create_tools_bar(filtered_df):
    """
    Show artwork volume and average popularity by AI tool.
    """

    if filtered_df.empty:
        return create_empty_chart()

    tool_data = (
        filtered_df
        .groupby("Tools_Used")
        .agg(
            Count=("Artwork_ID", "count"),
            Avg_Score=("Popularity_Score", "mean"),
        )
        .round(1)
        .reset_index()
        .sort_values(
            "Count",
            ascending=False,
        )
    )

    if tool_data.empty:
        return create_empty_chart()

    fig = px.bar(
        tool_data,
        x="Tools_Used",
        y="Count",
        color="Avg_Score",
        color_continuous_scale=[
            "#d9eff2",
            "#acd6d6",
            "#73afb1",
            "#3e7e86",
        ],
        hover_data={
            "Avg_Score": True,
            "Count": True,
        },
    )

    fig.update_traces(
        marker_line_width=0,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Artworks: %{y:,}<br>"
            "Average score: %{marker.color:.1f}"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        xaxis_title="AI Tool",
        yaxis_title="Number of Artworks",
        bargap=0.24,
        coloraxis_colorbar={
            "title": "Avg Score",
            "thickness": 10,
            "len": 0.65,
            "outlinewidth": 0,
        },
    )

    styled_fig = apply_style(fig)

    styled_fig.update_xaxes(
        tickangle=-20,
    )

    return styled_fig


# ------------------------------------------------------------
# APP
# ------------------------------------------------------------

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
)

server = app.server


# ------------------------------------------------------------
# NAVIGATION DATA
# ------------------------------------------------------------

NAV_ITEMS = [
    {
        "id": "style-trend",
        "icon": "↗",
        "label": "Style Trend",
    },
    {
        "id": "style-pop",
        "icon": "★",
        "label": "Popularity",
    },
    {
        "id": "region-bar",
        "icon": "◎",
        "label": "By Region",
    },
    {
        "id": "heatmap",
        "icon": "▦",
        "label": "Heatmap",
    },
    {
        "id": "world-map",
        "icon": "◉",
        "label": "World Map",
    },
    {
        "id": "platform",
        "icon": "▯",
        "label": "Platforms",
    },
    {
        "id": "tools",
        "icon": "✦",
        "label": "Tools",
    },
]


CHART_DESC = {
    "style-trend": (
        "Style share over time — see which visual styles are "
        "rising or fading across 2022–2024."
    ),

    "style-pop": (
        "Average popularity score by style — revealing which "
        "aesthetics resonate most strongly with audiences."
    ),

    "region-bar": (
        "Artwork volume by region — compare where AI-generated "
        "art is being produced and how strongly audiences engage."
    ),

    "heatmap": (
        "Region and style matrix — uncover whether different "
        "parts of the world favor different visual aesthetics."
    ),

    "world-map": (
        "Global bubble map — bubble size represents artwork "
        "volume while color represents average popularity."
    ),

    "platform": (
        "Platform distribution — explore where AI artwork is "
        "shared and which platforms generate the most reach."
    ),

    "tools": (
        "AI tool landscape — compare the generative tools used "
        "by artists and the engagement associated with each one."
    ),
}


CHART_TITLES = {
    "style-trend": "Style Trend",
    "style-pop": "Popularity",
    "region-bar": "By Region",
    "heatmap": "Style Heatmap",
    "world-map": "World Map",
    "platform": "Platforms",
    "tools": "Creative Tools",
}
# ------------------------------------------------------------
# LAYOUT
# ------------------------------------------------------------

app.layout = html.Div(
    id="page-shell",
    children=[
        html.Div(
            dcc.Location(
                id="url",
                refresh=False,
            ),

            html.Div(
                id="resize-trigger",
                style={"display": "none"},
            ),
            id="root",
            children=[
                # Background
                html.Div(
                    id="bg",
                    n_clicks=0,
                    children=[
                        html.Img(
                            src="/assets/hero-bg.jpg",
                            id="bg-dark",
                            style={"opacity":1},
                        ),

                        html.Img(
                            src="/assets/brightbg.png",
                            id="bg-light",
                            style={"opacity":0},
                        ),
                    ],
                ),

                # Decorative background glow
                html.Div(className="ambient-glow ambient-glow-one"),
                html.Div(className="ambient-glow ambient-glow-two"),

                # --------------------------------------------------
                # TOP NAVIGATION
                # --------------------------------------------------
                html.Div(
                    id="topnav",
                    children=[
                        html.A(
                            [
                                html.Span("AIGC Atlas"),
                            ],
                            id="nav-brand",
                            href="#",
                        ),

                        html.Div(
                            id="nav-filters",
                            children=[

                                html.Div(
                                    className="nav-filter-item",
                                    children=[
                                        html.Div(
                                            className="filter-heading",
                                            children=[
                                                html.Span(
                                                    "Year",
                                                    className="filter-label",
                                                ),
                                            ],
                                        ),
                                        dcc.Dropdown(
                                            id="filter-year",
                                            options=[
                                                {"label": "All Years", "value": "All"}
                                            ] + [
                                                {
                                                    "label": str(year),
                                                    "value": str(year),
                                                }
                                                for year in ALL_YEARS
                                            ],
                                            value=["All"],
                                            multi=True,
                                            closeOnSelect=False,
                                            clearable=False,
                                            searchable=False,
                                            className="nav-dropdown",
                                        ),
                                    ],
                                ),

                                html.Div(
                                    className="nav-filter-item",
                                    children=[
                                        html.Div(
                                            className="filter-heading",
                                            children=[
                                                html.Span(
                                                    "Region",
                                                    className="filter-label",
                                                ),
                                            ],
                                        ),
                                        dcc.Dropdown(
                                            id="filter-region",
                                            options=[
                                                {"label": "All Regions", "value": "All"}
                                            ] + [
                                                {
                                                    "label": region,
                                                    "value": region,
                                                }
                                                for region in ALL_REGIONS
                                            ],
                                            value=["All"],
                                            multi=True,
                                            closeOnSelect=False,
                                            clearable=False,
                                            searchable=False,
                                            className="nav-dropdown",
                                        ),
                                    ],
                                ),

                                html.Div(
                                    className="nav-filter-item",
                                    children=[
                                        html.Div(
                                            className="filter-heading",
                                            children=[
                                                html.Span(
                                                    "Style",
                                                    className="filter-label",
                                                ),
                                            ],
                                        ),
                                        dcc.Dropdown(
                                            id="filter-style",
                                            options=[
                                                {"label": "All Styles", "value": "All"}
                                            ] + [
                                                {
                                                    "label": style,
                                                    "value": style,
                                                }
                                                for style in ALL_STYLES
                                            ],
                                            value=["All"],
                                            multi=True,
                                            closeOnSelect=False,
                                            clearable=False,
                                            searchable=False,
                                            className="nav-dropdown",
                                        ),
                                    ],
                                ),

                            ],
                        ),

                        html.A(
                            [
                                html.Span("Portfolio"),
                                html.Span("↗", className="top-button-arrow"),
                            ],
                            id="nav-portfolio",
                            href=(
                                "https://portfolio-website-english-"
                                "nvxa.vercel.app"
                            ),
                            target="_blank",
                            rel="noopener noreferrer",
                        ),
                    ],
                ),

                # --------------------------------------------------
                # LEFT NAVIGATION
                # --------------------------------------------------
                html.Div(
                    id="leftnav",
                    children=[
                        html.Div(
                            className="leftnav-primary-group",
                            children=[
                                html.Button(
                                    children=[
                                        html.Span(
                                            item["icon"],
                                            className="nav-icon",
                                        ),
                                        html.Span(
                                            item["label"],
                                            className="nav-tooltip",
                                        ),
                                    ],
                                    id={
                                        "type": "nav-btn",
                                        "index": item["id"],
                                    },
                                    className="nav-btn",
                                    n_clicks=0,
                                )
                                for index, item in enumerate(NAV_ITEMS)
                            ],
                        ),

                        html.Div(
                            className="leftnav-secondary-group",
                            children=[
                                html.Button(
                                    "☾",
                                    id="dark-mode-btn",
                                    className="utility-btn",
                                    type="button",
                                    title="Dark mode",
                                    n_clicks=0,
                                ),
                                html.Button(
                                    "☀",
                                    id="light-mode-btn",
                                    className="utility-btn",
                                    type="button",
                                    title="Light mode",
                                    n_clicks=0,
                                ),
                            ],
                        ),
                    ],
                ),

                # --------------------------------------------------
                # HERO
                # --------------------------------------------------
                html.Div(
                    id="main-title",
                    style={
                        "opacity": "1",
                        "pointerEvents": "none",
                        "transform": "translateY(0)",
                    },
                    children=[
                        html.Div(
                            "GENERATIVE ART EXPLORATION",
                            className="hero-eyebrow",
                        ),
                        html.H1(
                            [
                                html.Span(
                                    "A New Way Of",
                                    className="hero-line",
                                ),
                                html.Span(
                                    "Seeing AI Art",
                                    className=(
                                        "hero-line hero-line-indent"
                                    ),
                                ),
                            ],
                            id="hero-title",
                        ),
                        html.P(
                            (
                                "Explore visual patterns, cultural "
                                "preferences, platform trends, and the "
                                "tools shaping AI-generated art across "
                                "the world."
                            ),
                            id="hero-sub",
                        ),
                    ],
                ),

                # --------------------------------------------------
                # BOTTOM LEFT INTRO CARD
                # --------------------------------------------------
                html.Div(
                    id="intro-card",
                    style={
                        "opacity": "1",
                        "pointerEvents": "auto",
                        "transform": "translateY(0)",
                    },
                    children=[
                        html.P(
                            "DISCOVER THE DATA",
                            className="card-eyebrow",
                        ),
                        html.H2("Find The Pattern"),
                        html.P(
                            (
                                "Navigate the atlas using the icons on "
                                "the left. Filter by year, region, or "
                                "visual style to reveal new "
                                "relationships across the dataset."
                            ),
                            className="intro-copy",
                        ),
                        html.Div(
                            className="intro-stat-row",
                            children=[
                                html.Div(
                                    [
                                        html.Strong("10K+"),
                                        html.Span("Artworks"),
                                    ],
                                    className="intro-stat",
                                ),
                                html.Div(
                                    className="mini-art-stack",
                                    children=[
                                        html.Div(
                                            className=(
                                                "mini-art mini-art-one"
                                            )
                                        ),
                                        html.Div(
                                            className=(
                                                "mini-art mini-art-two"
                                            )
                                        ),
                                        html.Div(
                                            className=(
                                                "mini-art mini-art-three"
                                            )
                                        ),
                                    ],
                                ),
                                html.Div(
                                    "⋯",
                                    className="intro-arrow",
                                ),
                            ],
                        ),
                    ],
                ),

                # --------------------------------------------------
                # CHART
                # --------------------------------------------------
                html.Div(
                    id="chart-area",
                    style={
                        "opacity": "0",
                        "pointerEvents": "none",
                        "transform": "scale(0.98)",
                    },
                ),

                html.Div(
                    id="chart-desc",
                    style={
                        "opacity": "0",
                    },
                ),

                # --------------------------------------------------
                # RIGHT PANEL
                # --------------------------------------------------
                html.Div(
                    id="right-panel",
                    children=[
                        html.Div(
                            id="desc-card",
                            children=[],
                            style={
                                "maxHeight": "0",
                                "opacity": "0",
                                "overflow": "hidden",
                                "marginBottom": "0",
                                "transition": (
                                    "max-height 0.4s ease, "
                                    "opacity 0.3s ease, "
                                    "margin-bottom 0.4s ease"
                                ),
                            },
                        ),

                        html.Div(
                            id="info-card-wrapper",
                            children=[
                                html.Div(
                                    id="info-card",
                                    children=[
                                        html.Div(
                                            className="info-card-header",
                                            children=[
                                                html.Div(
                                                    [
                                                        html.P(
                                                            "FEATURED DATASET",
                                                            className="card-eyebrow",
                                                        ),
                                                        html.H3("AIGC Atlas"),
                                                    ]
                                                ),
                                                html.A(
                                                    "↗",
                                                    className="info-arrow",
                                                    href="https://www.kaggle.com/datasets/waqi786/ai-generated-art-trends",
                                                    target="_blank",
                                                    rel="noopener noreferrer",
                                                ),
                                            ],
                                        ),

                                        html.P(
                                            (
                                                "A visual atlas of 10,000 "
                                                "AI-generated artworks created "
                                                "between 2022 and 2024. Explore "
                                                "styles, regions, platforms, "
                                                "engagement, and creative tools."
                                            ),
                                            className="info-copy",
                                        ),

                                        html.Div(
                                            id="kpi-row",
                                            children=[
                                                html.Div(
                                                    [
                                                        html.H4("10K"),
                                                        html.P("ARTWORKS"),
                                                    ],
                                                    className="kpi-pill",
                                                ),
                                                html.Div(
                                                    [
                                                        html.H4("10"),
                                                        html.P("STYLES"),
                                                    ],
                                                    className="kpi-pill",
                                                ),
                                                html.Div(
                                                    [
                                                        html.H4("6"),
                                                        html.P("REGIONS"),
                                                    ],
                                                    className="kpi-pill",
                                                ),
                                                html.Div(
                                                    [
                                                        html.H4("3YR"),
                                                        html.P("SPAN"),
                                                    ],
                                                    className="kpi-pill",
                                                ),
                                            ],
                                        ),

                                        html.Div(
                                            className="info-actions",
                                            children=[
                                                html.Button(
                                                    "♡",
                                                    id="favorite-btn",
                                                    className="info-action",
                                                    type="button",
                                                    title="Save",
                                                    n_clicks=0,
                                                )
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),

                dcc.Store(
                    id="active-chart",
                    data=None,
                ),

                dcc.Store(
                    id="theme-mode",
                    data="dark",
                ),

                dcc.Store(
                    id="favorite-state",
                    data=False,
                ),

                dcc.Store(
                    id="filter-memory",
                    data={
                        "year": ["All"],
                        "region": ["All"],
                        "style": ["All"],
                    },
                ),
            ],
        ),
    ],
)

app.clientside_callback(
    """
    function(pathname) {
        setTimeout(function() {
            window.dispatchEvent(new Event("resize"));
        }, 300);

        setTimeout(function() {
            window.dispatchEvent(new Event("resize"));
        }, 1000);

        return "";
    }
    """,
    Output("resize-trigger", "children"),
    Input("url", "pathname"),
)

# ------------------------------------------------------------
# CALLBACK: ACTIVE CHART
# ------------------------------------------------------------

@app.callback(
    Output("active-chart", "data"),
    [
        Input(
            {
                "type": "nav-btn",
                "index": item["id"],
            },
            "n_clicks",
        )
        for item in NAV_ITEMS
    ]
    + [
        Input("bg", "n_clicks"),
    ],
    State("active-chart", "data"),
)
def set_active_chart(*args):
    """
    Open a chart from the left navigation.

    Clicking the active chart again, or clicking the background,
    returns the interface to the landing view.
    """

    current_chart = args[-1]

    if not ctx.triggered:
        return current_chart

    triggered_id = ctx.triggered_id

    if triggered_id == "bg":
        return None

    if isinstance(triggered_id, dict):
        selected_chart = triggered_id.get("index")

        if current_chart == selected_chart:
            return None

        return selected_chart

    return current_chart


# ------------------------------------------------------------
# CALLBACK: RENDER CHART
# ------------------------------------------------------------

@app.callback(
    Output("chart-area", "children"),
    Output("chart-desc", "children"),
    Output("main-title", "style"),
    Output("intro-card", "style"),
    Output("chart-area", "style"),
    Output("chart-desc", "style"),
    Output("desc-card", "children"),
    Output("desc-card", "style"),
    Input("active-chart", "data"),
    Input("filter-year", "value"),
    Input("filter-region", "value"),
    Input("filter-style", "value"),
)
def render_chart(active_chart, year, region, style):
    """
    Render the selected visualization and update the interface state.
    """

    df_all = get_filtered(
        year=year,
        region=region,
        style=style,
    )

    df_without_style = get_filtered(
        year=year,
        region=region,
        style=["All"],
    )

    df_without_region = get_filtered(
        year=year,
        region=["All"],
        style=style,
    )

    df_without_year = get_filtered(
        year=["All"],
        region=region,
        style=style,
    )

    hidden_description_style = {
        "maxHeight": "0",
        "opacity": "0",
        "overflow": "hidden",
        "marginBottom": "0",
        "transition": (
            "max-height 0.4s ease, "
            "opacity 0.3s ease, "
            "margin-bottom 0.4s ease"
        ),
    }

    visible_description_style = {
        "maxHeight": "300px",
        "opacity": "1",
        "overflow": "hidden",
        "marginBottom": "12px",
        "transition": (
            "max-height 0.4s ease, "
            "opacity 0.3s ease, "
            "margin-bottom 0.4s ease"
        ),
    }

    if not active_chart:
        return (
            None,
            None,

            # Main title
            {
                "opacity": "1",
                "pointerEvents": "none",
                "transform": "translateY(0)",
                "transition": (
                    "opacity 0.35s ease, "
                    "transform 0.35s ease"
                ),
            },

            # Intro card
            {
                "opacity": "1",
                "pointerEvents": "auto",
                "transform": "translateY(0)",
                "transition": (
                    "opacity 0.35s ease, "
                    "transform 0.35s ease"
                ),
            },

            # Chart area
            {
                "opacity": "0",
                "pointerEvents": "none",
                "transform": "scale(0.98)",
                "transition": (
                    "opacity 0.4s ease, "
                    "transform 0.4s ease"
                ),
            },

            # Chart description
            {
                "opacity": "0",
                "transition": "opacity 0.3s ease",
            },

            [],
            hidden_description_style,
        )

    chart_functions = {
        "style-trend": create_style_trend,
        "style-pop": create_style_popularity,
        "region-bar": create_region_bar,
        "heatmap": create_heatmap,
        "world-map": create_bubble_map,
        "platform": create_platform_bar,
        "tools": create_tools_bar,
    }

    chart_function = chart_functions.get(active_chart)

    if chart_function is None:
        figure = create_empty_chart(
            "The selected visualization could not be loaded."
        )

    elif active_chart == "style-trend":
        figure = create_style_trend(
            df_without_style,
            style,
        )

    elif active_chart == "style-pop":
        figure = create_style_popularity(
            df_without_style,
            style,
        )

    elif active_chart == "region-bar":
        figure = create_region_bar(
            df_without_region,
            region,
        )

    elif active_chart == "world-map":
        figure = create_bubble_map(
            df_without_region,
            region,
        )

    elif active_chart == "heatmap":
        figure = create_heatmap(df_all)

    elif active_chart == "platform":
        figure = create_platform_bar(df_all)

    elif active_chart == "tools":
        figure = create_tools_bar(df_all)

    else:
        figure = create_empty_chart(
            "The selected visualization could not be loaded."
        )

    chart = dcc.Graph(
        figure=figure,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
        style={
            "width": "100%",
            "height": "100%",
        },
    )

    chart_description = CHART_DESC.get(active_chart, "")

    description_content = [
        html.P(
            "ACTIVE VIEW",
            className="card-eyebrow",
        ),
        html.H3(
            CHART_TITLES.get(
                active_chart,
                active_chart,
            )
        ),
        html.P(chart_description),
    ]

    return (
        chart,
        html.P(chart_description),

        # Main title
        {
            "opacity": "0",
            "pointerEvents": "none",
            "transform": "translateY(-18px)",
            "transition": (
                "opacity 0.35s ease, "
                "transform 0.35s ease"
            ),
        },

        # Intro card
        {
            "opacity": "0",
            "pointerEvents": "none",
            "transform": "translateY(24px)",
            "transition": (
                "opacity 0.35s ease, "
                "transform 0.35s ease"
            ),
        },

        # Chart area
        {
            "opacity": "1",
            "pointerEvents": "all",
            "transform": "scale(1)",
            "transition": (
                "opacity 0.4s ease, "
                "transform 0.4s ease"
            ),
        },

        # Chart description
        {
            "opacity": "1",
            "transition": "opacity 0.4s ease 0.18s",
        },

        description_content,
        visible_description_style,
    )

@app.callback(
    Output("theme-mode", "data"),
    Input("dark-mode-btn", "n_clicks"),
    Input("light-mode-btn", "n_clicks"),
    prevent_initial_call=True,
)
def switch_theme(dark, light):

    if ctx.triggered_id == "light-mode-btn":
        return "light"

    if ctx.triggered_id == "dark-mode-btn":
        return "dark"

    return "dark"

@app.callback(
    Output("bg-dark", "style"),
    Output("bg-light", "style"),
    Input("theme-mode", "data"),
)
def update_background(theme):

    common = {
        "position":"absolute",
        "inset":"0",
        "width":"100%",
        "height":"100%",
        "objectFit":"cover",
        "transition":"opacity .8s ease",
    }

    if theme == "light":

        return (
            {**common, "opacity":0},
            {**common, "opacity":1},
        )

    return (
        {**common, "opacity":1},
        {**common, "opacity":0},
    )

@app.callback(
    [Output({"type": "nav-btn", "index": item["id"]}, "className")
     for item in NAV_ITEMS]
    + [
        Output("dark-mode-btn", "className"),
        Output("light-mode-btn", "className"),
    ],
    Input("active-chart", "data"),
    Input("theme-mode", "data"),
)
def update_button_states(active_chart, theme):

    nav_classes = []

    for item in NAV_ITEMS:
        if item["id"] == active_chart:
            nav_classes.append("nav-btn nav-btn-primary")
        else:
            nav_classes.append("nav-btn")

    dark_class = (
        "utility-btn utility-btn-active"
        if theme == "dark"
        else "utility-btn"
    )

    light_class = (
        "utility-btn utility-btn-active"
        if theme == "light"
        else "utility-btn"
    )

    return nav_classes + [dark_class, light_class]

@app.callback(
    Output("favorite-state", "data"),
    Input("favorite-btn", "n_clicks"),
    State("favorite-state", "data"),
    prevent_initial_call=True,
)
def toggle_favorite(n, current):
    return not current

@app.callback(
    Output("favorite-btn", "children"),
    Output("favorite-btn", "className"),
    Input("favorite-state", "data"),
)
def update_favorite_button(favorite):

    if favorite:
        return (
            "♥",
            "info-action info-action-liked",
        )

    return (
        "♡",
        "info-action",
    )

@app.callback(
    Output("filter-year", "value"),
    Output("filter-region", "value"),
    Output("filter-style", "value"),
    Output("filter-memory", "data"),

    Input("filter-year", "value"),
    Input("filter-region", "value"),
    Input("filter-style", "value"),

    State("filter-memory", "data"),
)
def clean_all(year, region, style, memory):

    trigger = ctx.triggered_id

    if memory is None:
        memory = {
            "year": ["All"],
            "region": ["All"],
            "style": ["All"],
        }

    def fix(current, previous):

        current = current or []
        previous = previous or ["All"]

        if not isinstance(current, list):
            current = [current]

        # 什么都没选
        if len(current) == 0:
            return ["All"]

        # 上一次是 All，现在点了其它
        if previous == ["All"]:

            if "All" in current and len(current) > 1:
                current.remove("All")

            return current

        # 已经不是 All

        # 用户重新点了 All
        if "All" in current:
            return ["All"]

        # 普通多选
        return current

    new_year = memory["year"]
    new_region = memory["region"]
    new_style = memory["style"]

    if trigger == "filter-year":
        new_year = fix(year, memory["year"])

    elif trigger == "filter-region":
        new_region = fix(region, memory["region"])

    elif trigger == "filter-style":
        new_style = fix(style, memory["style"])

    new_memory = {
        "year": new_year,
        "region": new_region,
        "style": new_style,
    }

    return (
        new_year,
        new_region,
        new_style,
        new_memory,
    )

# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
