import reactpy
from reactpy import component, html, run, utils, use_state
import pandas as pd
import numpy as np
import plotly.express as px
from reactpy.backend.fastapi import configure, Options
from fastapi import FastAPI
from reactpy_router import route, simple, link
from reactpy_router.core import use_params

app = FastAPI()


@component
def my_router():
    return simple.router(
        route("/".home()),
        route("/locations".locations()),
        route("/customers".customers()),
        route("/TimeSeries".time_series()),
        route("/Logistics".logistics()),
    )


# ----------------------------------------------------------------
data__path = r"Sample_Store.csv"

df = pd.read_csv(data__path, encoding="unicode_escape")

df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df["Ship_Date"] = pd.to_datetime(df["Ship_Date"])

df["Order_Month"] = df["Order_Date"].dt.month_name()
df["Order_Year"] = df["Order_Date"].dt.year


state_list = df["State"].unique().tolist()
state_list.insert(0, "All")

# Years
years_list = df["Order_Year"].unique().tolist()
years_list.insert(0, "All")

# Categoty
category_list = df["Category"].unique().tolist()
category_list.insert(0, "All")

# Main Function of Vizualizations


def create_chart_vizualization(the_data, chart_type="bar", xlabel="X_Label",
                               ylabel="Y_Label", the_title="Chart Title",
                               bar_colors=["#ADA2FF", "#C0DEFF",
                                           "#FCDDB0", "#FF9F9F"],
                               title_size=25, hover_html_template="", height=600, showlegend=False):
    if chart_type == "bar":
        fig = px.bar(the_data,
                     x=the_data.index,
                     y=the_data,
                     color=the_data.index,
                     color_discrete_sequence=bar_colors,
                     labels={"index": xlabel, "y": ylabel},
                     text_auto="0.3s",
                     title=the_title,
                     height=height,
                     template="plotly_dark"
                     )

        fig.update_traces(
            textfont={
                "family": "tahoma",
                "size": 17,
                "color": "white"
            },
            marker=dict(line=dict(color='#111', width=2)),
            hovertemplate=hover_html_template,

        )

    elif chart_type == "pie":
        fig = px.pie(names=the_data.index,
                     values=round(the_data),
                     title=the_title,
                     color_discrete_sequence=bar_colors,
                     height=height,
                     template="plotly_dark",
                     )

        fig.update_traces(
            textfont={
                "family": "tahoma",
                "size": 17,
                "color": "white"
            },
            textinfo="label+value",
            hovertemplate=hover_html_template,
            marker=dict(line=dict(color='#111', width=2)),
            pull=[0.0, 0.0, 0.15]

        )

    elif chart_type == "line":
        fig = px.line(the_data,
                      x=the_data.index.astype(str),
                      y=the_data,
                      color_discrete_sequence=["#ADA2FF"],
                      labels={"y": ylabel, "x": xlabel},
                      title=the_title,
                      markers="o",
                      height=height,
                      template="plotly_dark"

                      )

        fig.update_traces(
            marker=dict(size=12, line=dict(color='#111', width=1)),
            hovertemplate=hover_html_template,
        )

    fig.update_layout(
        showlegend=showlegend,
        title={
            "font": {
                "size": title_size,
                "family": "tahoma",
            }
        },
        hoverlabel={
            "bgcolor": "#123",
            "font_size": 17,
            "font_family": "tahoma"
        }
    )
    return fig


@component
def create_sales_category_chart(the_df):
    category_by_slaes = the_df.groupby("Category")["Sales"].sum()
    fig = px.pie(names=category_by_slaes.index,
                 values=category_by_slaes,
                 title="Total Sales By Category",
                 color_discrete_sequence=["#ADA2FF",
                                          "#C0DEFF", "#FCDDB0", "#FF9F9F"],
                 hole=0.43,
                 template="plotly_dark"
                 )

    fig.update_traces(
        textfont={
            "family": "tahoma",
            "size": 15,
        },
        textinfo="label+percent",
        hovertemplate="Category: %{label}<br>Sales: %{value:0.2s}",
        marker=dict(line=dict(color='#111', width=1)),
    )

    fig.update_layout(
        showlegend=False,
        title={
            "font": {
                "size": 25,
                "family": "tahoma",
            }
        },
        hoverlabel={
            "bgcolor": "#123",
            "font_size": 17,
            "font_family": "tahoma"
        }
    )
    return fig


state_filt = state_list[0]
years_filt = years_list[0]
category_filt = category_list[0]
form_data = {"state": "All", "year": "All", "category": "All"}


@component
def select_menu(the_state, the_year, the_category):
    global state_filt
    global years_filt
    global category_filt
    global form_data

    div_class = {
        "class": "flex max-full flex-col gap-y-1 p-2 rounded-md bg-black"
    }
    label_class = {
        "class": "block text-l font-md text-white text-left"
    }
    select_menu_class = "text-gray-300 mt-1 cursor-pointer block w-full py-2 px-3 bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"

    state_filt, set_state_filt = use_state(state_list[0])
    years_filt, set_years_filt = use_state(years_list[0])
    category_filt, set_category_filt = use_state(category_list[0])
    form_data, set_form_data = use_state(
        {"state": "All", "year": "All", "category": "All"})

    select_states_options = html.select({
        "id": "states-select",
        "name": "states",
        "value": the_state,
        "class": select_menu_class,
        "on_change": lambda e: set_state_filt(e["target"]["value"]),
    }, [html.option({"value": i, "class": "text-white"}, i) for i in state_list],
    )

    select_years_options = html.select({
        "id": "years-select",
        "name": "years",
        "value": the_year,
        "class": select_menu_class,
        "on_change": lambda e: set_years_filt(e["target"]["value"]),
    }, [html.option({"value": i, "class": "text-white"}, i) for i in years_list],
    )

    select_category_options = html.select({
        "id": "category-select",
        "name": "category",
        "value": the_category,
        "class": select_menu_class,
        "on_change": lambda e: set_category_filt(e["target"]["value"]),
    }, [html.option({"value": i, "class": "text-white"}, i) for i in category_list],
    )

    @reactpy.event(prevent_default=False)
    def handle_submit(event):
        data = {}
        data["state"] = event["target"]["elements"][0]["value"]
        data["year"] = event["target"]["elements"][1]["value"]
        data["category"] = event["target"]["elements"][2]["value"]

        set_form_data(data)

    menus = html.form(
        {"class": "text-black py-0 sm:py-1", "on_submit": handle_submit},
        html.div(
            {"class": "max-full max-w-7xl px-0 lg:px-0"},
            html.dl(
                {"class": "grid grid-cols-1 xs:grid-cols-1 gap-x-3 gap-y-2 text-center lg:grid-cols-1"},
                html.div(
                    div_class,
                    html.label(
                        label_class,
                        f'States: ',
                        html.span(
                            {"class": "text-blue-300 font-bold"}, the_state)
                    ),
                    select_states_options
                ),
                html.div(
                    div_class,
                    html.label(
                        label_class,
                        f'Years: ',
                        html.span(
                            {"class": "text-blue-300 font-bold"}, the_year)
                    ),
                    select_years_options
                ),
                html.div(
                    div_class,
                    html.label(
                        label_class,
                        f'Category: ',
                        html.span(
                            {"class": "text-blue-300 font-bold"}, the_category)
                    ),
                    select_category_options
                ),

            ),

            html.br(),

            html.div(
                div_class,
                html.button({
                    "id": "apply-filter",
                    "type": "submit",
                    "class": "h-16 w-full text-blue-400 hover:text-white border-2 border-blue-700 hover:bg-black focus:ring-4 focus:outline-none focus:ring-blue-300 font-bold rounded-lg text-lg px-5 py-2.5 text-center me-2 mb-2 dark:border-blue-500 dark:text-blue-500 dark:hover:text-white dark:hover:bg-blue-500 dark:focus:ring-blue-800"

                }, "Apply Filter"),

            ),
        ),
    )

    return menus


@component
def side_bar():

    side_bar = html.aside(
        {"id": "default-sidebar", "class": "relative bg-#0f1729 fixed top-0 left-0 z-40 w-full h-screen transition-transform -translate-x-full sm:translate-x-0",
         "aria-label": "Sidebar"},
        html.div(
            {"class": "h-full px-3 py-4 overflow-y-auto bg-gray-50 dark:bg-gray-800"},
            html.ul(
                {"class": "space-y-2 font-bold"},
                html.li(
                    html.a(
                        {
                            "class": "flex items-center p-2 text-white rounded-lg dark:text-white hover:bg-blue-100 hover:text-black group",
                            "href": "/",
                            "aria-current": "page"},

                        html.span(
                            {"class": "ms-3"},
                            "Sales"

                        )
                    )
                ),
                html.li(
                    html.a(
                        {
                            "class": "flex items-center p-2 text-white rounded-lg dark:text-white hover:bg-blue-100 hover:text-black group",
                            "href": "/locations",
                            "aria-current": "page"},

                        html.span(
                            {"class": "ms-3"},
                            "Locations"

                        )
                    )
                ),
                html.li(
                    html.a(
                        {
                            "class": "flex items-center p-2 text-white rounded-lg dark:text-white hover:bg-blue-100 hover:text-black group",
                            "href": "/customers",
                            "aria-current": "page"},

                        html.span(
                            {"class": "ms-3"},
                            "Customers"

                        )
                    )
                ),
                html.li(
                    html.a(
                        {
                            "class": "flex items-center p-2 text-white rounded-lg dark:text-white hover:bg-blue-100 hover:text-black group",
                            "href": "/TimeSeries",
                            "aria-current": "page"},

                        html.span(
                            {"class": "ms-3"},
                            "Time Series"

                        )
                    )
                ),
                html.li(
                    html.a(
                        {
                            "class": "flex items-center p-2 text-white rounded-lg dark:text-white hover:bg-blue-100 hover:text-black group",
                            "href": "/Logistics",
                            "aria-current": "page"},

                        html.span(
                            {"class": "ms-3"},
                            "Logistics"

                        )
                    )
                ),
                html.hr(),
                html.br(),




                html.li(
                    select_menu(form_data["state"], form_data["year"],
                                form_data["category"]),
                ),


            )

        )
    )

    return side_bar


# ==================== Start Home Page Components =======================
@component
def create_home_cards(the_df, page_title):
    div_class = {
        "class": "flex max-w-xs sm:max-w flex-col gap-y-4 border-2 border-blue-300 p-5 rounded-md bg-black transition "
                 "duration-300 ease-in-out hover:bg-gray-900"
    }

    dt_class = {
        "class": "ext-base leading-7 text-white font-tahoma font-bold"
    }

    dd_class = {
        "class": "order-first text-3xl font-tahoma font-bold tracking-tight text-white sm:text-3xl"
    }

    cards = html.section(
        {"class": "text-black py-2 sm:py-2"},
        html.div(
            {"class": "mx-auto max-w-7xl px-6 lg:px-8"},
            html.h2(
                {"class": "text-6xl font-bold mb-8 text-center text-white"},
                page_title
            ),
            html.dl(
                {"class": "grid grid-cols-2 xs:grid-cols-1 sm:grid-cols-1 gap-x-8 gap-y-16 text-center lg:grid-cols-4"},
                html.div(
                    div_class,
                    html.dt(
                        dt_class, "Total Sales"
                    ),
                    html.dd(
                        dd_class,
                        f'${the_df["Sales"].sum():,.0f}'
                    )
                ),

                html.div(
                    div_class,
                    html.dt(
                        dt_class, "Total Profit"
                    ),
                    html.dd(
                        dd_class,
                        f'${the_df["Profit"].sum():,.0f}'
                    )
                ),
                html.div(
                    div_class,
                    html.dt(
                        dt_class, "Total Volumes"
                    ),
                    html.dd(
                        dd_class,
                        f'{the_df["Quantity"].sum():,.0f}'
                    )
                ),

                html.div(
                    div_class,
                    html.dt(
                        dt_class, "Total Orders"
                    ),
                    html.dd(
                        dd_class,
                        f'{the_df["Customer_ID"].nunique():,.0f}'
                    )
                )

            )

        ),
    )
    return cards


@component
def create_shipping_segment_chart(the_df):
    div_class = {
        "class": "flex max-auto flex-col gap-y-1 border-1 border-gray-800 p-2 rounded-md bg-black"
    }
    # Shipping Mode Bar Chart
    regions_sales = the_df.groupby(
        "Region")["Sales"].sum().sort_values(ascending=False)

    fig_regions_sales = create_chart_vizualization(regions_sales, chart_type="bar", xlabel="Region",
                                                   ylabel="Sales",
                                                   the_title="Total Sales Via Regions",
                                                   bar_colors=[
                                                       "#067fd6", "#01B075", "#705DDF", "#FF625B"],

                                                   hover_html_template="Region: <b>%{x}</b><br># Total Sales: %{y:.3s}")

    fig_regions_sales = fig_regions_sales.to_html(include_plotlyjs='cdn', config={
        'displayModeBar': False})

    # Customers Segments Pie Chart
    segments = the_df.groupby("Segment")["Sales"].sum()

    fig_segments = create_chart_vizualization(segments, chart_type="pie",
                                              the_title="Sales By Customer Segmentation",
                                              bar_colors=[
                                                  "#067fd6", "#01B075", "#705DDF", "#FF625B"],
                                              hover_html_template="Customer Segment: %{label}<br>Frequency: %{value:,.0f}<br>Frequency PCT(%): %{percent}")
    fig_segments = fig_segments.to_html(include_plotlyjs='cdn', config={
        'displayModeBar': False})

    chart = html.section(
        {"class": "text-black py-2 sm:py-3"},
        html.div(
            {"class": "mx-auto max-w-7xl px-6 lg:px-8"},
            html.dl(
                {"class": "grid grid-cols-2 xs:grid-cols-1 sm:grid-cols-1 gap-x-1 gap-y-2 text-center lg:grid-cols-2"},
                html.div(
                    div_class,
                    utils.html_to_vdom(fig_regions_sales)
                ),

                html.div(
                    div_class,
                    utils.html_to_vdom(fig_segments)

                ),

            )
        ),
    )
    return chart


@component
def create_profit_year_chart(the_df):
    div_class = {
        "class": "flex max-auto flex-col gap-y-1 border-1 border-gray-800 p-2 rounded-md bg-black"
    }

    profit_via_year = round(the_df.groupby("Order_Year")["Profit"].sum())

    fig_profit_year = create_chart_vizualization(profit_via_year, chart_type="line", xlabel="Year",
                                                 ylabel="Total Profit",
                                                 the_title="Total Profit Via Years",
                                                 hover_html_template="Year: <b>%{x}</b><br>Total Profit: %{y:,}", height=550)

    fig_profit_year = fig_profit_year.to_html(include_plotlyjs='cdn', config={
        'displayModeBar': False})

    chart = html.section(
        {"class": "text-black py-2 sm:py-4"},
        html.div(
            {"class": "mx-auto max-w-7xl px-6 lg:px-8"},
            html.dl(
                {"class": "grid grid-cols-1 xs:grid-cols-1 gap-x-1 gap-y-2 text-center lg:grid-cols-1"},
                html.div(
                    div_class,
                    utils.html_to_vdom(fig_profit_year)
                ),
            )
        ),
    )
    return chart
# ==================== End Home Page Components =======================

# ==================== Start Locations Page Components =======================


@component
def select_menu_loc(the_state, the_year, the_category):
    global state_filt
    global years_filt
    global category_filt
    global form_data

    div_class = {
        "class": "flex max-full flex-col gap-y-1 p-2 rounded-md bg-black"
    }
    label_class = {
        "class": "block text-l font-md text-white text-left"
    }
    select_menu_class = "text-gray-300 mt-1 cursor-pointer block w-full py-2 px-3 bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"

    state_filt, set_state_filt = use_state(state_list[0])
    years_filt, set_years_filt = use_state(years_list[0])
    category_filt, set_category_filt = use_state(category_list[0])
    form_data, set_form_data = use_state(
        {"state": "All", "year": "All", "category": "All"})

    select_states_options = html.select({
        "id": "states-select",
        "name": "states",
        "value": the_state,
        "class": select_menu_class,
        "on_change": lambda e: set_state_filt(e["target"]["value"]),
    }, [html.option({"value": i, "class": "text-white"}, i) for i in state_list],
    )

    select_years_options = html.select({
        "id": "years-select",
        "name": "years",
        "value": the_year,
        "class": select_menu_class,
        "on_change": lambda e: set_years_filt(e["target"]["value"]),
    }, [html.option({"value": i, "class": "text-white"}, i) for i in years_list],
    )

    select_category_options = html.select({
        "id": "category-select",
        "name": "category",
        "value": the_category,
        "class": select_menu_class,
        "on_change": lambda e: set_category_filt(e["target"]["value"]),
    }, [html.option({"value": i, "class": "text-white"}, i) for i in category_list],
    )

    @reactpy.event(prevent_default=False)
    def handle_submit(event):
        data = {}
        data["state"] = event["target"]["elements"][0]["value"]
        data["year"] = event["target"]["elements"][1]["value"]
        data["category"] = event["target"]["elements"][2]["value"]

        set_form_data(data)

    menus = html.form(
        {"class": "text-black py-0 sm:py-1", "on_submit": handle_submit},
        html.div(
            {"class": "max-full max-w-7xl px-0 lg:px-0"},
            html.dl(
                {"class": "grid grid-cols-1 xs:grid-cols-1 gap-x-3 gap-y-2 text-center lg:grid-cols-1"},
                html.div(
                    {"style": {"display": "none"}},
                    html.label(
                        label_class,
                        f'States: ',

                    ),
                    select_states_options
                ),
                html.div(
                    div_class,
                    html.label(
                        label_class,
                        f'Years: ',
                        html.span(
                            {"class": "text-blue-300 font-bold"}, the_year)
                    ),
                    select_years_options
                ),
                html.div(
                    div_class,
                    html.label(
                        label_class,
                        f'Category: ',
                        html.span(
                            {"class": "text-blue-300 font-bold"}, the_category)
                    ),
                    select_category_options
                ),

            ),

            html.br(),

            html.div(
                div_class,
                html.button({
                    "id": "apply-filter",
                    "type": "submit",
                    "class": "h-16 w-full text-blue-400 hover:text-white border-2 border-blue-700 hover:bg-black focus:ring-4 focus:outline-none focus:ring-blue-300 font-bold rounded-lg text-lg px-5 py-2.5 text-center me-2 mb-2 dark:border-blue-500 dark:text-blue-500 dark:hover:text-white dark:hover:bg-blue-500 dark:focus:ring-blue-800"

                }, "Apply Filter"),

            ),
        ),
    )

    return menus


@component
def side_bar_loc():

    side_bar = html.aside(
        {"id": "default-sidebar", "class": "relative bg-#0f1729 fixed top-0 left-0 z-40 w-full h-screen transition-transform -translate-x-full sm:translate-x-0",
         "aria-label": "Sidebar"},
        html.div(
            {"class": "h-full px-3 py-4 overflow-y-auto bg-gray-50 dark:bg-gray-800"},
            html.ul(
                {"class": "space-y-2 font-bold"},
                html.li(
                    html.a(
                        {
                            "class": "flex items-center p-2 text-white rounded-lg dark:text-white hover:bg-blue-100 hover:text-black group",
                            "href": "/",
                            "aria-current": "page"},

                        html.span(
                            {"class": "ms-3"},
                            "Sales"

                        )
                    )
                ),
                html.li(
                    html.a(
                        {
                            "class": "flex items-center p-2 text-white rounded-lg dark:text-white hover:bg-blue-100 hover:text-black group",
                            "href": "/locations",
                            "aria-current": "page"},

                        html.span(
                            {"class": "ms-3"},
                            "Locations"

                        )
                    )
                ),
                html.li(
                    html.a(
                        {
                            "class": "flex items-center p-2 text-white rounded-lg dark:text-white hover:bg-blue-100 hover:text-black group",
                            "href": "/customers",
                            "aria-current": "page"},

                        html.span(
                            {"class": "ms-3"},
                            "Customers"

                        )
                    )
                ),
                html.li(
                    html.a(
                        {
                            "class": "flex items-center p-2 text-white rounded-lg dark:text-white hover:bg-blue-100 hover:text-black group",
                            "href": "/TimeSeries",
                            "aria-current": "page"},

                        html.span(
                            {"class": "ms-3"},
                            "Time Series"

                        )
                    )
                ),
                html.li(
                    html.a(
                        {
                            "class": "flex items-center p-2 text-white rounded-lg dark:text-white hover:bg-blue-100 hover:text-black group",
                            "href": "/Logistics",
                            "aria-current": "page"},

                        html.span(
                            {"class": "ms-3"},
                            "Logistics"

                        )
                    )
                ),
                html.hr(),
                html.br(),


                html.li(
                    select_menu_loc(form_data["state"], form_data["year"],
                                    form_data["category"]),
                ),


            )

        )
    )

    return side_bar


@component
def create_locations_cards(the_df, page_title):
    div_class = {
        "class": "flex max-w-xs sm:max-w flex-col gap-y-4 border-2 border-blue-300 p-5 rounded-md bg-black transition "
                 "duration-300 ease-in-out hover:bg-gray-900"
    }

    dt_class = {
        "class": "ext-base leading-7 text-white font-tahoma font-bold"
    }

    dd_class = {
        "class": "order-first text-3xl font-tahoma font-bold tracking-tight text-white sm:text-3xl"
    }

    cards = html.section(
        {"class": "text-black py-2 sm:py-2"},
        html.div(
            {"class": "mx-auto max-w-7xl px-6 lg:px-8"},
            html.h2(
                {"class": "text-5xl font-bold mb-8 text-center text-white"},
                page_title
            ),
            html.dl(
                {"class": "grid grid-cols-3 xs:grid-cols-1 gap-x-8 gap-y-16 text-center lg:grid-cols-3"},
                html.div(
                    div_class,
                    html.dt(
                        dt_class, "Regions"
                    ),
                    html.dd(
                        dd_class,
                        f'{the_df["Region"].nunique():,.0f}'
                    )
                ),

                html.div(
                    div_class,
                    html.dt(
                        dt_class, "States"
                    ),
                    html.dd(
                        dd_class,
                        f'{the_df["State"].nunique():,.0f}'
                    )
                ),


                html.div(
                    div_class,
                    html.dt(
                        dt_class, "Top Order State"
                    ),
                    html.dd(
                        dd_class,
                        the_df["State"].value_counts().idxmax()
                    )
                )

            )

        ),
    )
    return cards


def create_top_10_states(the_data, chart_type="bar", xlabel="X_Label",
                         ylabel="Y_Label", the_title="Chart Title",
                         bar_colors=[
                             "#067fd6", "#01B075", "#705DDF", "#FF625B"],
                         title_size=25, hover_html_template="", orientation="h"):

    if chart_type == "bar":
        fig = px.bar(the_data,
                     y=the_data.index,
                     x=the_data,
                     orientation=orientation,
                     color=the_data.index,
                     color_discrete_sequence=bar_colors,
                     labels={"x": xlabel, "y": ylabel},
                     text_auto="0.5s",
                     title=the_title,
                     height=600,
                     template="plotly_dark"
                     )

        fig.update_traces(
            textfont={
                "family": "tahoma",
                "size": 17,
                "color": "white"
            },
            marker=dict(line=dict(color='#111', width=2)),
            hovertemplate=hover_html_template,
        )

        fig.update_layout(
            showlegend=False,
            title={
                "font": {
                    "size": title_size,
                    "family": "tahoma",
                }
            },
            hoverlabel={
                "bgcolor": "#123",
                "font_size": 17,
                "font_family": "tahoma"
            }
        )
    return fig


def create_top_10_state_chart(the_df):
    div_class = {
        "class": "flex max-auto flex-col gap-y-1 border-1 border-gray-800 p-2 rounded-md bg-black"
    }
    # Shipping Mode Bar Chart
    top_10_states_sales = the_df.groupby("State")["Sales"].sum().nlargest(10)

    fig_top_10_states_sales = create_top_10_states(top_10_states_sales, chart_type="bar", orientation="h", xlabel="Total Sales",
                                                   ylabel="State",
                                                   the_title="Top 5 State Via Sales",
                                                   bar_colors=["#067fd6"],

                                                   hover_html_template="The State: <b>%{y}</b><br>Total Sales: %{x:.5s}")

    fig_top_10_states_sales = fig_top_10_states_sales.to_html(include_plotlyjs='cdn', config={
        'displayModeBar': False})

    chart = html.section(
        {"class": "text-black py-2 sm:py-3"},
        html.div(
            {"class": "mx-auto max-w-7xl px-6 lg:px-8"},
            html.dl(
                {"class": "grid grid-cols-1 xs:grid-cols-1 sm:grid-cols-1 gap-x-1 gap-y-2 text-center lg:grid-cols-1"},
                html.div(
                    div_class,
                    utils.html_to_vdom(fig_top_10_states_sales)
                ),

                # html.div(
                #     div_class,
                #     utils.html_to_vdom(fig_segments)

                # ),

            )
        ),
    )
    return chart
# ==================== End Locations Page Components =======================

# ==================== Start Customers Page Components =======================


@component
def create_customers_cards(the_df, page_title):
    div_class = {
        "class": "flex max-w-xs sm:max-w flex-col gap-y-4 border-2 border-blue-300 p-5 rounded-md bg-black transition "
                 "duration-300 ease-in-out hover:bg-gray-900"
    }

    dt_class = {
        "class": "ext-base leading-7 text-white font-tahoma font-bold"
    }

    dd_class = {
        "class": "order-first text-3xl font-tahoma font-bold tracking-tight text-white sm:text-3xl"
    }

    cards = html.section(
        {"class": "text-black py-2 sm:py-2"},
        html.div(
            {"class": "mx-auto max-w-7xl px-6 lg:px-8"},
            html.h2(
                {"class": "text-5xl font-bold mb-8 text-center text-white"},
                page_title
            ),
            html.dl(
                {"class": "grid grid-cols-3 xs:grid-cols-1 gap-x-8 gap-y-16 text-center lg:grid-cols-3"},
                html.div(
                    div_class,
                    html.dt(
                        dt_class, "AVG Sales Per Customer"
                    ),
                    html.dd(
                        dd_class,
                        f'${the_df.groupby("Customer_ID")["Sales"].sum().mean():,.2f}'
                    )
                ),

                html.div(
                    div_class,
                    html.dt(
                        dt_class, "AVG Profit Per Customer"
                    ),
                    html.dd(
                        dd_class,
                        f'${the_df.groupby("Customer_ID")["Profit"].sum().mean():,.2f}'
                    )
                ),

                html.div(
                    div_class,
                    html.dt(
                        dt_class, "Top Loyal Customers"
                    ),
                    html.dd(
                        dd_class,
                        the_df.drop_duplicates(subset="Order_ID")[
                            "Customer_Name"].value_counts().idxmax()
                    )
                )

            )

        ),
    )
    return cards


def create_customers_segment(the_df):
    the_df = the_df.drop_duplicates()

    customers_by_segemnt = the_df.drop_duplicates(
        "Customer_ID")["Segment"].value_counts()

    fig = px.pie(names=customers_by_segemnt.index,
                 values=customers_by_segemnt,
                 title="Customers Popularity Via Segments",
                 color_discrete_sequence=[
                     "#067fd6", "#01B075", "#705DDF", "#FF625B"],
                 hole=0.43,
                 template="plotly_dark",
                 height=500
                 )

    fig.update_traces(
        textfont={
            "family": "tahoma",
            "size": 16,
        },
        textinfo="label+percent",
        hovertemplate="Segment: %{label}<br>Popularity PCT(%): %{percent}<br># Customers %{value:.2s}",
        marker=dict(line=dict(color='#111', width=1)),
    )

    fig.update_layout(
        showlegend=False,
        title={
            "font": {
                "size": 25,
                "family": "tahoma",
            }
        },
        hoverlabel={
            "bgcolor": "#123",
            "font_size": 17,
            "font_family": "tahoma"
        }
    )
    return fig


@component
def create_customers_charts(the_df):
    div_class = {
        "class": "flex max-auto flex-col gap-y-1 border-1 border-gray-800 p-2 rounded-md bg-black"
    }

    customers_segment = create_customers_segment(the_df)

    fig_customers_segment = customers_segment.to_html(include_plotlyjs='cdn', config={
        'displayModeBar': False})

    # Customer Evolution
    customers_via_years = the_df.drop_duplicates(
        "Customer_ID")["Order_Year"].value_counts().sort_index()

    customers_via_years = create_chart_vizualization(customers_via_years, chart_type="line", xlabel="Year",
                                                     ylabel="Total Customer",
                                                     the_title="The Increasing of Customers Via Years",
                                                     hover_html_template="Year: <b>%{x}</b><br>Total Customer: %{y:,}", height=500)

    fig_customers_via_years = customers_via_years.to_html(include_plotlyjs='cdn', config={
        'displayModeBar': False})

    chart = html.section(
        {"class": "text-black py-2 sm:py-3"},
        html.div(
            {"class": "mx-auto max-w-7xl px-6 lg:px-8"},
            html.dl(
                {"class": "grid grid-cols-2 xs:grid-cols-1 sm:grid-cols-1 gap-x-1 gap-y-2 text-center lg:grid-cols-2"},
                html.div(
                    div_class,
                    utils.html_to_vdom(fig_customers_via_years)
                ),

                html.div(
                    div_class,
                    utils.html_to_vdom(fig_customers_segment)

                ),

            )
        ),
    )
    return chart
# ==================== End Customers Page Components =======================

# ==================== Start Time Series Page Components =======================


@component
def page_header(page_title):
    title = html.section(
        {"class": "text-black py-2 sm:py-2"},
        html.div(
            {"class": "mx-auto max-w-7xl px-6 lg:px-8"},
            html.h2(
                {"class": "text-5xl font-bold mb-8 text-center text-white"},
                page_title
            ),

        ),
    )
    return title


def create_line_chart(the_df, xlabel="X", ylabel="Y", title="Title", hover_html_template="Template"):
    fig = px.line(the_df,
                  color_discrete_sequence=[
                      "#067fd6", "#01B075", "#705DDF", "#FF625B"],
                  labels={"index": xlabel, "value": ylabel,
                          "Order_Year": "Year"},
                  title=title,
                  markers="o",
                  height=500,
                  template="plotly_dark",
                  )

    fig.update_traces(
        marker=dict(size=8, line=dict(color='#111', width=1)),
        hovertemplate=hover_html_template,
    )

    fig.update_layout(
        showlegend=True,
        title={
            "font": {
                "size": 25,
                "family": "tahoma",
            }
        },
        hoverlabel={
            "bgcolor": "#123",
            "font_size": 17,
            "font_family": "tahoma"
        }
    )
    return fig


@component
def create_slaes_via_months_charts(the_df):
    div_class = {
        "class": "flex max-auto flex-col gap-y-1 border-1 border-gray-800 p-2 rounded-md bg-black"
    }
    slaes_via_year_month = the_df.pivot_table(
        index=the_df["Order_Date"].dt.month, columns="Order_Year", values="Sales", aggfunc="sum")

    months_name = ["Jan", "Feb", "Mar", "Apr",
                   "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    x = slaes_via_year_month.index
    displayes_months_name = []

    for i in x:
        displayes_months_name.append(months_name[i-1])

    slaes_via_year_month.index = displayes_months_name

    slaes_via_year_month = create_line_chart(slaes_via_year_month, xlabel="Month", ylabel="Sales",
                                             title="Sales Via Month Per Each Year", hover_html_template="Month: <b>%{x}</b><br>Total Sales: %{y:.3s}")

    fig_slaes_via_year_month = slaes_via_year_month.to_html(include_plotlyjs='cdn', config={
        'displayModeBar': False})

    chart = html.section(
        {"class": "text-black py-2 sm:py-3"},
        html.div(
            {"class": "mx-auto max-w-7xl px-6 lg:px-8"},
            html.dl(
                {"class": "grid grid-cols-1 xs:grid-cols-1 sm:grid-cols-1 gap-x-1 gap-y-2 text-center lg:grid-cols-1"},
                html.div(
                    div_class,
                    utils.html_to_vdom(fig_slaes_via_year_month)
                )
            )
        ),
    )
    return chart


@component
def create_profit_via_months_charts(the_df):
    div_class = {
        "class": "flex max-auto flex-col gap-y-1 border-1 border-gray-800 p-2 rounded-md bg-black"
    }
    profit_via_year_month = the_df.pivot_table(
        index=the_df["Order_Date"].dt.month, columns="Order_Year", values="Profit", aggfunc="sum")

    months_name = ["Jan", "Feb", "Mar", "Apr",
                   "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    x = profit_via_year_month.index
    displayes_months_name = []

    for i in x:
        displayes_months_name.append(months_name[i-1])

    profit_via_year_month.index = displayes_months_name

    profit_via_year_month = create_line_chart(profit_via_year_month, xlabel="Month", ylabel="Profit",
                                              title="Profit Via Month Per Each Year", hover_html_template="Month: <b>%{x}</b><br>Total Profit: %{y:.3s}")

    fig_profit_via_year_month = profit_via_year_month.to_html(include_plotlyjs='cdn', config={
        'displayModeBar': False})

    chart = html.section(
        {"class": "text-black py-2 sm:py-3"},
        html.div(
            {"class": "mx-auto max-w-7xl px-6 lg:px-8"},
            html.dl(
                {"class": "grid grid-cols-1 xs:grid-cols-1 sm:grid-cols-1 gap-x-1 gap-y-2 text-center lg:grid-cols-1"},
                html.div(
                    div_class,
                    utils.html_to_vdom(fig_profit_via_year_month)
                )
            )
        ),
    )
    return chart
# ==================== End Time Series Page Components =======================


# ==================== Start Logistics Page Components =======================

@component
def create_logstics_cards(the_df, page_title):
    div_class = {
        "class": "flex max-w-xs sm:max-w flex-col gap-y-4 border-2 border-blue-300 p-5 rounded-md bg-black transition "
                 "duration-300 ease-in-out hover:bg-gray-900"
    }

    dt_class = {
        "class": "ext-base leading-7 text-white font-tahoma font-bold"
    }

    dd_class = {
        "class": "order-first text-3xl font-tahoma font-bold tracking-tight text-white sm:text-3xl"
    }

    cards = html.section(
        {"class": "text-black py-2 sm:py-2"},
        html.div(
            {"class": "mx-auto max-w-7xl px-6 lg:px-8"},
            html.h2(
                {"class": "text-5xl font-bold mb-8 text-center text-white"},
                page_title
            ),
            html.dl(
                {"class": "grid grid-cols-3 xs:grid-cols-1 gap-x-8 gap-y-16 text-center lg:grid-cols-3"},
                html.div(
                    div_class,
                    html.dt(
                        dt_class, "AVG Sales Per Order"
                    ),
                    html.dd(
                        dd_class,
                        f'${the_df.groupby("Order_ID")["Sales"].sum().mean():,.0f}'
                    )
                ),

                html.div(
                    div_class,
                    html.dt(
                        dt_class, "AVG Profit Per Order"
                    ),
                    html.dd(
                        dd_class,
                        f'${the_df.groupby("Order_ID")["Profit"].sum().mean():,.0f}'
                    )
                ),

                html.div(
                    div_class,
                    html.dt(
                        dt_class, "Total Orders"
                    ),
                    html.dd(
                        dd_class,
                        f'{the_df["Order_ID"].nunique():,.0f}'

                    )
                )

            )

        ),
    )
    return cards


def category_subcategory_quantity(the_df):
    category_subcategoty = the_df.groupby(
        ["Category", "Sub_Category"], as_index=False)["Quantity"].sum()

    fig = px.sunburst(category_subcategoty, path=["Category", "Sub_Category"],
                      values='Quantity',
                      color_discrete_sequence=[
                          "#067fd6", "#01B075", "#705DDF", "#FF625B"],
                      title="The Quantity of Category and its Sub-Categories",
                      template="plotly_dark",
                      height=530

                      )

    fig.update_layout(
        margin=dict(t=50, l=0, r=0, b=10),
        title={
            "font": {
                "size": 20,
                "family": "tahoma"
            }
        },
        hoverlabel={
            "bgcolor": "#222",
            "font_size": 14,
            "font_family": "tahoma"
        }
    )

    fig.update_traces(
        textfont={
            "family": "tahoma",
            "size": 13,
        },
        hovertemplate="%{label}<br>Quantity:  %{value:.3s}",
    )

    return fig


def year_over_year_chart(the_df):
    year_over_year = the_df.groupby("Order_Year", as_index=False)[
        "Profit"].sum()

    year_over_year["Prev_Year"] = 0

    year_over_year.loc[1:,
                       "Prev_Year"] = year_over_year.loc[0:2, "Profit"].tolist()

    year_over_year["Yoy_Growth"] = round(
        ((year_over_year["Profit"] - year_over_year["Prev_Year"]) / year_over_year["Prev_Year"]) * 100, 2)

    year_over_year.replace(np.inf, 0, inplace=True)

    fig = px.line(year_over_year, x=year_over_year["Order_Year"].astype(str), y="Yoy_Growth",
                  template="plotly_dark",
                  labels={
                      "Yoy_Growth": "Year-Over-Year Profit Growth (%)", "x": "Year"},
                  color_discrete_sequence=[
                  "#ADA2FF", "#C0DEFF", "#FCDDB0", "#FF0060", "#EDD2F3"],
                  title="The Year-Over-Year Profit Growth",
                  height=565,
                  markers="o",
                  )

    fig.update_layout(
        title={
            "font": {
                "size": 23,
                "family": "tahoma"
            }
        },        hoverlabel={
            "bgcolor": "#222",
            "font_size": 14,
            "font_family": "tahoma"
        })
    fig.update_traces(
        hovertemplate="%{x}<br>YOY PCT: %{y}%",
        marker_size=10)

    return fig


@component
def create_logistics_charts(the_df):
    div_class = {
        "class": "flex max-auto flex-col gap-y-1 border-1 border-gray-800 p-2 rounded-md bg-black"
    }

    ategory_subcategory = category_subcategory_quantity(the_df)

    fig_ategory_subcategory = ategory_subcategory.to_html(include_plotlyjs='cdn', config={
        'displayModeBar': False})

    # Year Over Year Growth
    year_over_year_growth = year_over_year_chart(the_df)

    fig_year_over_year_growth = year_over_year_growth.to_html(include_plotlyjs='cdn', config={
        'displayModeBar': False})

    chart = html.section(
        {"class": "text-black py-2 sm:py-3"},
        html.div(
            {"class": "mx-auto max-w-7xl px-6 lg:px-8"},
            html.dl(
                {"class": "grid grid-cols-2 xs:grid-cols-1 sm:grid-cols-1 gap-x-1 gap-y-2 text-center lg:grid-cols-2"},
                html.div(
                    div_class,
                    utils.html_to_vdom(fig_ategory_subcategory)
                ),

                html.div(
                    div_class,
                    utils.html_to_vdom(fig_year_over_year_growth)

                ),

            )
        ),
    )
    return chart
# ==================== End Locations Page Components =======================


@component
def home():
    if form_data["state"] == "All":
        dff = df.copy()

    else:
        dff = df[df["State"] == form_data["state"]].copy()

    if form_data["category"] == "All":
        dff = dff.copy()

    else:
        dff = dff[dff["Category"] == form_data["category"]].copy()

    if form_data["year"] == "All":
        dff = dff.copy()
    else:
        dff = dff[dff["Order_Year"] == int(form_data["year"])].copy()

    sidebar = html.nav(
        {"style": {"background-color": "#121212",
                   "height": "100%", "width": "19%",  "position": "fixed"}},
        side_bar()

    )
    layout = html.div(
        {"style": {"background-color": "#0f1729",
                   "height": "100%", "width": "81%", "position": "relative", "margin-left": "19%"},
         "class": "fixed top-0 left-0 z-40 w-64 h-screen transition-transform -translate-x-full sm:translate-x-0"},

        create_home_cards(dff, "Sales Dashboard"),
        create_shipping_segment_chart(dff),
    )

    return html.div(
        {"style": {"display": "flex",
                   "background-color": "#111"
                   }},
        sidebar, layout
    )


@component
def locations():
    if form_data["state"] == "All":
        dff = df.copy()

    else:
        dff = df[df["State"] == form_data["state"]].copy()

    if form_data["category"] == "All":
        dff = dff.copy()

    else:
        dff = dff[dff["Category"] == form_data["category"]].copy()

    if form_data["year"] == "All":
        dff = dff.copy()
    else:
        dff = dff[dff["Order_Year"] == int(form_data["year"])].copy()

    sidebar = html.nav(
        {"style": {"background-color": "#121212",
                   "height": "100%", "width": "19%",  "position": "fixed"}},
        side_bar_loc()

    )
    layout = html.div(
        {"style": {"background-color": "#0f1729",
                   "height": "100%", "width": "81%", "position": "relative", "margin-left": "19%"},
         "class": "fixed top-0 left-0 z-40 w-64 h-screen transition-transform -translate-x-full sm:translate-x-0"},

        create_locations_cards(dff, "Locations"),
        create_top_10_state_chart(dff),
    )

    return html.section(
        {"style": {"display": "flex",
                   "background-color": "#111"
                   }},
        sidebar, layout
    )


@component
def customers():
    if form_data["state"] == "All":
        dff = df.copy()

    else:
        dff = df[df["State"] == form_data["state"]].copy()

    if form_data["category"] == "All":
        dff = dff.copy()

    else:
        dff = dff[dff["Category"] == form_data["category"]].copy()

    if form_data["year"] == "All":
        dff = dff.copy()
    else:
        dff = dff[dff["Order_Year"] == int(form_data["year"])].copy()

    sidebar = html.nav(
        {"style": {"background-color": "#121212",
                   "height": "100%", "width": "19%",  "position": "fixed"}},
        side_bar()

    )
    layout = html.div(
        {"style": {"background-color": "#0f1729",
                   "height": "100%", "width": "81%", "position": "relative", "margin-left": "19%"},
         "class": "fixed top-0 left-0 z-40 w-64 h-screen transition-transform -translate-x-full sm:translate-x-0"},

        create_customers_cards(dff, "Customers"),
        create_customers_charts(dff),
    )

    return html.section(
        {"style": {"display": "flex",
                   "background-color": "#111"
                   }},
        sidebar, layout
    )


@component
def time_series():
    if form_data["state"] == "All":
        dff = df.copy()

    else:
        dff = df[df["State"] == form_data["state"]].copy()

    if form_data["category"] == "All":
        dff = dff.copy()

    else:
        dff = dff[dff["Category"] == form_data["category"]].copy()

    if form_data["year"] == "All":
        dff = dff.copy()
    else:
        dff = dff[dff["Order_Year"] == int(form_data["year"])].copy()

    sidebar = html.nav(
        {"style": {"background-color": "#121212",
                   "height": "100%", "width": "19%",  "position": "fixed"}},
        side_bar()

    )
    layout = html.div(
        {"style": {"background-color": "#0f1729",
                   "height": "100%", "width": "81%", "position": "relative", "margin-left": "19%"},
         "class": "fixed top-0 left-0 z-40 w-64 h-screen transition-transform -translate-x-full sm:translate-x-0"},

        page_header("Time Series"),
        create_slaes_via_months_charts(dff),
        create_profit_via_months_charts(dff)
    )

    return html.section(
        {"style": {"display": "flex",
                   "background-color": "#111"
                   }},
        sidebar, layout
    )


@component
def logistics():
    if form_data["state"] == "All":
        dff = df.copy()

    else:
        dff = df[df["State"] == form_data["state"]].copy()

    if form_data["category"] == "All":
        dff = dff.copy()

    else:
        dff = dff[dff["Category"] == form_data["category"]].copy()

    if form_data["year"] == "All":
        dff = dff.copy()
    else:
        dff = dff[dff["Order_Year"] == int(form_data["year"])].copy()

    sidebar = html.nav(
        {"style": {"background-color": "#121212",
                   "height": "100%", "width": "19%",  "position": "fixed"}},
        side_bar()

    )
    layout = html.div(
        {"style": {"background-color": "#0f1729",
                   "height": "100%", "width": "81%", "position": "relative", "margin-left": "19%"},
         "class": "fixed top-0 left-0 z-40 w-64 h-screen transition-transform -translate-x-full sm:translate-x-0"},

        create_logstics_cards(dff, "Logistics"),
        create_logistics_charts(dff),
    )

    return html.section(
        {"style": {"display": "flex",
                   "background-color": "#111"
                   }},
        sidebar, layout
    )


@component
def App():
    return simple.router(
        route("/", home()),
        route("/locations", locations()),
        route("/customers", customers()),
        route("/TimeSeries", time_series()),
        route("/Logistics", logistics()),
    )


# Create the app
configure(app, App, Options(head=html.head(
    html.link(
        {
            'rel': 'stylesheet',
            'href': 'https://unpkg.com/tailwindcss@^1.0/dist/tailwind.min.css',
        }
    ),
    html.script(
        {
            'src': "https://cdn.plot.ly/plotly-latest.min.js",

        }
    ),
    html.title("ReactPy Sales Dashboard")
)
)
)

# if __name__ == "__main__":
#     app.run()
