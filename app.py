## Python - Ontario Schools COVID-19 Data set App

# Required Libraries:

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Import the Data sets:

### Summary of COVID-19 Cases in Ontario Schools ***

url = "https://data.ontario.ca/dataset/b1fef838-8784-4338-8ef9-ae7cfd405b41/resource/7fbdbb48-d074-45d9-93cb-f7de58950418/download/schoolcovidsummary.csv"
df_sum = pd.read_csv(url)

## Change the 'reported_date' column to a datetime object and drop 'collected_date'
df_sum["reported_date"] = pd.to_datetime(df_sum["reported_date"])
df_sum.drop("collected_date", axis=1, inplace=True)


### Ontario Schols with Active Case Data set
url = "https://data.ontario.ca/dataset/b1fef838-8784-4338-8ef9-ae7cfd405b41/resource/8b6d22e2-7065-4b0f-966f-02640be366f2/download/schoolsactivecovid.csv"
df_active = pd.read_csv(url, encoding='latin-1')
df_active["reported_date"] = pd.to_datetime(df_active["reported_date"])

## Drop collected_date from Active data set
df_active.drop("collected_date", axis=1, inplace=True)

## Filter the Active Cases Data set for the last_reported date
df_active_now = df_active[df_active.reported_date == max(df_active.reported_date)]


## Group the active_now data set by municipality
df_municiaplity_now = df_active_now.groupby("municipality")['total_confirmed_cases'].sum().reset_index().sort_values(by=["total_confirmed_cases"], ascending=False).head(30)


## Set the index of the summary data set to the reported_date column
## Average the cases per week: Week Starting Sunday
datetime_index = pd.DatetimeIndex(df_sum.reported_date.values)
df_weekly = df_sum.set_index(datetime_index)
df_weekly.drop('reported_date', axis=1, inplace = True)

## Add week number to weekly data set
df_weekly['week_num'] = df_weekly.index.isocalendar().week

## Ontario Schools COVID-19 Cases Summary data set - Weekly Average
df_weekly = df_weekly.new_total_school_related_cases.resample("W").mean().round()
df_weekly = df_weekly.reset_index()

### FINDING THE NEW CASES TOTALS OF THE DAY FOR STUDENTS, STAFF and TOTAL ###
# Latest Total School Case Number
value_t  = df_sum.loc[df_sum.index[-1], 'new_total_school_related_cases']

# Previous Day School Total
reference_t = df_sum.loc[df_sum.index[-2], 'new_total_school_related_cases']
# Latest Total School Case Number
value_student  = df_sum.loc[df_sum.index[-1], 'new_school_related_student_cases']

# Previous Day School Total
reference_student = df_sum.loc[df_sum.index[-2], 'new_school_related_student_cases']

# Latest Total School Case Number
value_staff  = df_sum.loc[df_sum.index[-1], 'new_school_related_staff_cases']

# Previous Day School Total
reference_staff = df_sum.loc[df_sum.index[-2], 'new_school_related_staff_cases']

# Schools with 5 or more cases
df_schools_total_active_now = df_active_now.groupby(["municipality","school"])['total_confirmed_cases'].sum().reset_index().sort_values(by = "total_confirmed_cases", ascending = False)
schools_w_five_or_more = df_schools_total_active_now[df_schools_total_active_now.total_confirmed_cases >= 5].school.count()


#### CREATE THE DASHBOARD ####
fig = make_subplots(
        rows = 5, cols = 6,
        specs = [
                    [ {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type" : "indicator"}, {"type" : "indicator"}, {"type" : "indicator"} ],
                    [ {"type" : "scatter", "rowspan": 2, "colspan" : 3}, None, None, {"type" : "bar", "rowspan" : 2, "colspan" : 3}, None, None],
                    [  None, None, None, None, None, None],
                    [{"type" : "bar", "rowspan": 2, "colspan" : 4}, None, None, None, None, None],
                    [  None, None, None, None, {"type": "indicator", "rowspan" : 1, "colspan" : 2}, None],
                ]
)

last_reported_date = max(df_sum.reported_date)
first_reported_date = min(df_sum.reported_date).date()

fig.add_trace(
       go.Scatter(
        x = df_sum['reported_date'],
        y = df_sum['cumulative_school_related_cases'],
        mode = 'lines+markers',
        marker = dict(color = '#5DADE2')
       ),
        row = 2, col = 1
     )

fig.add_annotation(x = max(df_sum.reported_date), y = max(df_sum.cumulative_school_related_cases),
                  text = max(df_sum.cumulative_school_related_cases),
                  showarrow = True,
                  arrowhead = 2,
                  font = dict(
                      size = 16,
                      color = "white"
                  ),
                  arrowcolor = "darkred",
                  bordercolor = 'darkred')

#fig.update_layout(
#        title = f"Cumulative COVID-19 Cases in Students, Staff & Total <br> Report Updated: {first_reported_date }",
#)

fig.add_trace(
    go.Indicator(
        value = value_t,
        delta = {'reference': reference_t},
        mode = "number+delta",
        title = {"text" : " <br><span style = 'font-size: 0.8em; color:#5DADE2'>Total Cases</span>"},
        domain = {'row': 0, 'column': 0}
    ),
    row = 1, col = 1
)

fig.add_trace(
    go.Indicator(
        value = value_student,
        delta = {'reference': reference_student, 'relative': False},
        mode = "number+delta",
        title = {"text" : " <br><span style = 'font-size: 0.8em; color:#5DADE2'>Student Cases</span>"},
        domain = {'row': 0, 'column': 2}),
     row = 1, col = 2
)

fig.add_trace(
    go.Indicator(
        mode = "number+delta",
        value = value_staff,
        delta = {"reference": reference_staff},
        title = {"text" : " <br><span style = 'font-size: 0.8em; color:#5DADE2'>Staff cases</span>"},
        domain = {'row': 0, 'column': 1}),
    row = 1, col = 3
)

schools_w_cases = df_sum.current_schools_w_cases[df_sum.reported_date == max(df_sum.reported_date)].values[0]
y_schools_w_cases = df_sum.loc[df_sum.index[-2], 'current_schools_w_cases']

fig.add_trace(
    go.Indicator(
        mode = 'number+delta',
        value = schools_w_cases,
        delta = {'reference' : y_schools_w_cases},
        title = {"text" : " <br><span style = 'font-size: 0.8em; color:#5DADE2'>Schools with Cases</span>"}),
    row = 1, col = 4
)


value = df_sum.loc[df_sum.index[-1], 'current_schools_closed']
value_yest = df_sum.loc[df_sum.index[-2], 'current_schools_closed']

fig.add_trace(
    go.Indicator(
        mode = 'number+delta',
        delta = {'reference' : value_yest},
        value = value,
        title = {"text" : " <br><span style = 'font-size: 0.8em; color:#5DADE2'>Schools Closed</span>"}),
    row = 1, col = 5)


fig.add_trace(
    go.Indicator(
        mode = "gauge+number",
        value = df_sum.reported_date.count(),
        title = {'text': "<span style='font-size:0.8em; color:#5DADE2'> Schools Days Completed vs <br> Days in School Year</span>"},
        gauge = {'axis' : { 'range' : [0, 195]},
                    'threshold' : {'line' : {'color': "red", 'width' : 4}, 'thickness': 0.90, 'value' : 194}}

    ),
    row = 5, col = 5
)


fig.add_trace(
    go.Indicator(
        mode = 'number',
        value = schools_w_five_or_more,
        title = {"text" : " <br><span style = 'font-size: 0.8em; color:#5DADE2'>Schools with 5 or more cases</span>"}),
    row = 1, col = 6)


colors = ['#5DADE2',] * len(df_municiaplity_now)
colors[0] = 'crimson'

fig.add_trace(
    go.Bar(y = df_municiaplity_now["total_confirmed_cases"], x = df_municiaplity_now["municipality"],
           marker_color= colors,
           text = df_municiaplity_now['total_confirmed_cases'],
          textposition = 'outside'),
    row = 4, col = 1
)

colors_two = ['#5DADE2',] * len(df_weekly)
colors_two[-1] = 'crimson'
df_weekly.rename(columns= {"index" : "Start of Week", "new_total_school_related_cases" : "Weekly Average COVID-19 Cases"}, inplace = True)
fig.add_trace(
            go.Bar(y = df_weekly["Weekly Average COVID-19 Cases"], x = df_weekly["Start of Week"],
                  marker_color = colors_two,
                  text = df_weekly["Weekly Average COVID-19 Cases"],
                  textposition = 'outside'),
    row = 2, col = 4
)


fig.update_layout(
    template = "plotly_dark",
    title_font_color = '#CD6155',
    showlegend = False,
    yaxis_title = "CASES",
    font = dict(
            family = "Arial",
            size = 16),
    margin = dict( pad = 2)

)

fig.update_xaxes(
    tickangle = -30,
    tickfont = dict(size = 14)
)
fig.update_yaxes(
    showgrid = True, gridcolor = "lightgrey")

fig['layout']['yaxis1'].update(automargin = True)
fig['layout']['yaxis2'].update(showgrid=False, showticklabels = False)
fig['layout']['yaxis3'].update(showgrid=False, showticklabels = False)
fig['layout']['xaxis1'].update(title = "Cumulative COVID-19 Cases in Ontario Schools", title_font_color = "#CD6155",
                               showgrid = False, automargin = True, tickangle = 0)
fig['layout']['xaxis3'].update(title = "Current Active COVID-19 Cases in ONT Municipalities", title_font_color = "#CD6155")
#fig['layout']['yaxis2'].update(showgrid=False, showticklabels = False)
fig['layout']['xaxis2'].update(title = "Weekly Average COVID-19 Cases in ONT Schools", title_font_color = "#CD6155", tickangle = 0)
#fig['layout']['yaxis3'].update(showgrid=False, showticklabels = False)


app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(style = {'textAlign': 'Center'}, children = [
    html.H1(children = "ONTARIO COVID-19 CASES in SCHOOLS"),
    html.H2(children = f"Updated: {max(df_sum.reported_date).date()}"),

    dcc.Graph(
        style = {'height':"100vh"},
        figure = fig,
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
