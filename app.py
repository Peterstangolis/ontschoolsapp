## Python - Ontario Schools COVID-19 Data set App

# Required Libraries:

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
from datetime import datetime
from datetime import timedelta

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

# Change the name of one catholique elementary school
cass = df_active[df_active.school.str.contains('taire catholique de Casselman')]
cass_index = cass.index
df_active.at[cass_index, 'school'] = 'Catholic Elementary School de Casselman'

cole = df_active[df_active["school"].str.contains('Ãcole Ã©lÃ©mentaire catholique Saint-Isidore')]
cole_index = cole.index
df_active.at[cole_index, 'school'] = 'Saint-Isidore Catholic Elementary School'



## Filter the Active Cases Data set for the last_reported date
df_active_now = df_active[df_active.reported_date == max(df_active.reported_date)]

#Drop Board Site from active_now:
board_site_index = df_active_now[df_active_now.school.str.contains('Board')].index
if len(board_site_index) > 0:
    df_active_now = df_active_now.drop(board_site_index)


## Group the active_now data set by municipality
df_municipality_now = df_active_now.groupby("municipality")['total_confirmed_cases'].sum().reset_index().sort_values(by=["total_confirmed_cases"], ascending=False).head(30)


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

# Schools with 2 or more cases
df_schools_total_active_now = df_active_now.groupby(["municipality","school"])['total_confirmed_cases'].sum().reset_index().sort_values(by = "total_confirmed_cases", ascending = False)
schools_w_two_or_more = df_schools_total_active_now[df_schools_total_active_now.total_confirmed_cases >= 2].school.count()


#### CREATE THE DASHBOARD ####
#annotations = []

fig = make_subplots(
        rows = 5, cols = 6, row_heights = [0.2, 0.2, 0.2, 0.2, 0.2],
        #vertical_spacing=0.03,
        specs = [
                    [ {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type" : "indicator"}, {"type" : "indicator"}, {"type" : "indicator"} ],
                    [ {"type" : "scatter", "rowspan": 2, "colspan" : 2}, None, {"type" : "bar", "rowspan" : 2, "colspan" : 2}, None, {"type" : "table", "rowspan" : 2, "colspan":2}, None],
                    [  None, None, None, None, None, None],
                    [{"type" : "bar", "rowspan": 2, "colspan" : 4}, None, None, None, None, None],
                    [  None, None, None, None, {"type": "indicator", "rowspan" : 1, "colspan" : 2}, None],
                ],
     subplot_titles = ("","","","","","","Cumulative COVID-19 Cases in Ontario Schools","Weekly Average COVID-19 Cases in Ontario Schools",
                       "Top Schools with Active COVID-19 Cases", f"Ontario Municipalities with Active COVID-19 Case Numbers On:{max(df_sum.reported_date).date()}", ""),
)

last_reported_date = max(df_sum.reported_date)
first_reported_date = min(df_sum.reported_date).date()

fig.add_trace(
       go.Scatter(
        x = df_sum['reported_date'],
        y = df_sum['cumulative_school_related_cases'],
        mode = 'lines+markers',
        marker = dict(size = 5,
                      line = dict( width = 1.2, color = '#5DADE2'))
       ),
        row = 2, col = 1
     )


#fig.update_layout(
#        title = f"Cumulative COVID-19 Cases in Students, Staff & Total <br> Report Updated: {first_reported_date }",
#)

fig.add_trace(
    go.Indicator(
        value = value_t,
        delta = {'reference': reference_t, 'increasing' : {'color' : '#5DADE2' }, 'decreasing' : {'color' : 'crimson' }},
        mode = "number+delta",
        #number = {"font" : {"size" : 60}},
        title = {"text" : " <br><span style = 'font-size: 0.7em; color:#294C63'>Reported Cases</span>"},
    ),
    row = 1, col = 1
)

fig.add_trace(
    go.Indicator(
        value = value_student,
        delta = {'reference': reference_student, 'increasing' : {'color' : '#5DADE2' }, 'decreasing' : {'color' : 'crimson' }},
        mode = "number+delta",
        #number = {"font" : {"size" : 60}},
        title = {"text" : " <br><span style = 'font-size: 0.7em; color:#294C63'>Student Cases</span>"},
        domain = {'row': 0, 'column': 2}),
     row = 1, col = 2
)

fig.add_trace(
    go.Indicator(
        mode = "number+delta",
        value = value_staff,
        delta = {"reference": reference_staff, 'increasing' : {'color' : '#5DADE2' }, 'decreasing' : {'color' : 'crimson' }},
        #number = {"font" : {"size" : 60}},
        title = {"text" : " <br><span style = 'font-size: 0.7em; color:#294C63'>Staff Cases</span>"},
        domain = {'row': 0, 'column': 1}),
    row = 1, col = 3
)

schools_w_cases = df_sum.current_schools_w_cases[df_sum.reported_date == max(df_sum.reported_date)].values[0]
y_schools_w_cases = df_sum.loc[df_sum.index[-2], 'current_schools_w_cases']

total_schools_ont = max(df_sum.current_total_number_schools)
perc_school_cases = str(round(schools_w_cases / total_schools_ont, 1) * 100)

if perc_school_cases[-1] == '0':
    perc_school_cases = perc_school_cases[0:2]

fig.add_trace(
    go.Indicator(
        mode = 'number+delta',
        value = schools_w_cases,
        delta = {'reference' : y_schools_w_cases, 'increasing' : {'color' : '#5DADE2' }},
        #number = {"font" : {"size" : 70}},
        title = {"text" : f" <br><span style = 'font-size: medium; color:#294C63'>Active Cases <br>{perc_school_cases}% of ONT Schools</span>"}),
    row = 1, col = 4
)


value = df_sum.loc[df_sum.index[-1], 'current_schools_closed']
value_yest = df_sum.loc[df_sum.index[-2], 'current_schools_closed']

fig.add_trace(
    go.Indicator(
        mode = 'number+delta',
        delta = {'reference' : value_yest, 'increasing' : {'color' : '#5DADE2' }},
        value = value,
        #number = {"font" : {"size" : 60}},
        title = {"text" : " <br><span style = 'font-size: 0.7em; color:#294C63'>Schools Closed</span>"},
        ),
    row = 1, col = 5)


days_remain = 194 - df_sum.reported_date.count()
fig.add_trace(
    go.Indicator(
        mode = "gauge+number",
        value = df_sum.reported_date.count(),
        title = {'text': f"<span style='font-size:0.7em; color:#294C63'> Schools Days Completed:<br> {days_remain} To Go </span>"},
        #number = {"font" : {"size" : 60}},
        gauge = {
            'axis' : { 'range' : [0, 195]},
            'bar' : {'color' : '#5DADE2'},
            'threshold' : {'line' : {'color': "crimson", 'width' : 4}, 'thickness': 0.90, 'value' : 194}}

    ),
    row = 5, col = 5
)


fig.add_trace(
    go.Indicator(
        mode = 'number',
        value = schools_w_two_or_more,
        title = {"text" : " <br><span style = 'font-size: 0.7em; color:#294C63'>Schools with at least 2 <br>Active Cases</span>"},
        #number = {"font" : {"size" : 60}}
    ),
    row = 1, col = 6)


colors = ['#5DADE2',] * len(df_municipality_now)
colors[0] = 'crimson'

fig.add_trace(
    go.Bar(y = df_municipality_now["total_confirmed_cases"], x = df_municipality_now["municipality"],
            marker = dict(color = df_municipality_now["total_confirmed_cases"], coloraxis="coloraxis"),
           text = df_municipality_now['total_confirmed_cases'],
           textposition = 'outside'
           ),
    row = 4, col = 1
)

colors_two = ['#5DADE2',] * len(df_weekly)
colors_two[-1] = 'crimson'
df_weekly.rename(columns= {"index" : "Start of Week", "new_total_school_related_cases" : "Weekly Average COVID-19 Cases"}, inplace = True)

fig.add_trace(
            go.Bar(y = df_weekly["Weekly Average COVID-19 Cases"], x = df_weekly["Start of Week"],
                   marker = dict(color = df_municipality_now["total_confirmed_cases"], coloraxis="coloraxis"),
                  text = df_weekly["Weekly Average COVID-19 Cases"],
                  textposition = 'outside'),
    row = 2, col = 3
)




# Top Schools with Active CASES
top_10_schools = df_active_now.groupby('school')['total_confirmed_cases'].sum().reset_index().sort_values(by = "total_confirmed_cases", ascending = False).head(15)
top_10_schools = top_10_schools.rename({"total_confirmed_cases" : "Active Cases", "school": "School"}, axis = 1)
top_10_schools.reset_index(inplace = True)


# colors = ['#5DADE2',] * len(top_10_schools)
# colors[0] = 'crimson'
#
# fig.add_trace(
#             go.Bar(x = top_10_schools["Active Cases"], y = top_10_schools["School"],
#                 orientation='h',
#                 marker_color = colors,
#                 text = top_10_schools["Active Cases"],
#                 textposition = 'outside'
#                   ),
#     row = 2, col = 5
# )
# add Table instead of Bar PLOT
fig.add_trace(
    go.Table(
        columnorder = [1, 2],
        columnwidth = [200, 80],
        header=dict(values=[['<b>SCHOOL</b>'],['<b>CASES</b>']],
                line_color='#F8F9F9',
                fill_color='#5DADE2',
                align=['left','center'],
                font = dict(color='#154360', size = 13),
                height = 25
                ),
        cells=dict(values= [top_10_schools[k].tolist() for k in top_10_schools.columns[1:]], # 2nd column
               line_color='#F8F9F9',
               fill_color=[['#F5F5F5','#A4CDE8']* len(top_10_schools)],
               align=['left', 'center'],
               font = dict(color = '#154360', size = 13),
               height = 25)
    ),
    row=2, col = 5
)


####################################  UPDATE LAYOUT ########################################################

fig.update_layout(
    template = "plotly_white",
    #title = {
    #    'text' : f"ONTARIO COVID-19 CASES in SCHOOLS\n <b>(Updated: {max(df_sum.reported_date).date()} )",
    #    'x' : 0.04,
    #    'y' : 0.97,
    #    'xanchor' : 'left'},
    title_x = 0.05,
    title_font_color = '#3D92A8',
    showlegend = False,
    yaxis_title = "Cumulative Cases",
    font = dict(
            size = 13))
    #margin = dict(pad = 2)\



# fig.update_xaxes(
#     tickangle = -30,
#     tickfont = dict(size = 14)
# )

# fig.update_yaxes(
#     showgrid = True, gridcolor = "lightgrey")

fig['layout']['yaxis1'].update(automargin = True, range = [0, 6700], showgrid = True, gridcolor = 'lightgrey')
fig['layout']['yaxis2'].update(showgrid=True, showticklabels = False, range = [0, 300])
fig['layout']['yaxis3'].update(showgrid=True, showticklabels = False, range = [0, 700])
#fig['layout']['yaxis3'].update(showgrid=False, showticklabels = False)
fig['layout']['xaxis1'].update(tickangle= -30, showgrid = False, automargin = False,
                                tickfont=dict(size = 11))
fig['layout']['xaxis3'].update(tickangle = -45, title = "Top 30 Municipalities",
                                tickfont=dict(size = 11))
#fig['layout']['yaxis2'].update(showgrid=False, showticklabels = False)
fig['layout']['xaxis2'].update(tickangle = -30,
                               title_font_color = "#3D92A8",
                               tickfont=dict(size = 11))
#fig['layout']['xaxis3'].update(showgrid=False, showticklabels = False, range = [0, 80],
#                              title = "Case Number & Associated School", title_font_color = "#3D92A8",
#                              )

# Add annotations to Top 10 BarH


# annotations.append(dict(xref = 'x3', yref = 'y3',
#                     y = top_10_schools.iloc[0, 1], x = 63,
#                     text = top_10_schools.iloc[0, 1],
#                     font = dict(family = 'Verdana ', size = 10),
#                     showarrow = False))
# for i, t in enumerate(top_10_schools["School"]):
#     if i < len(top_10_schools)-1:
#         annotations.append(dict(xref = 'x3', yref='y3',
#                              y = top_10_schools.iloc[i+1, 1], x = 63,
#                              text = top_10_schools.iloc[i+1, 1],
#                              font = dict(family = 'Verdana ', size = 10),
#                              showarrow = False,
#                              align = 'right'
#                              )
#         )


# annotations.append(dict(xref = 'x1', yref = 'y1',
#                   x = max(df_sum.reported_date) + timedelta(days=5)  , y = max(df_sum.cumulative_school_related_cases) - 200,
#                   text = max(df_sum.cumulative_school_related_cases),
#                   showarrow = False,
#                   font = dict(
#                       size = 18,
#                       color = "white"),
#                 bordercolor = 'crimson',
#                 bgcolor = 'crimson'
#                   ))
#
# annotations.append(dict(xref = 'x3', yref = 'y3',
#                      y = max(df_municipality_now.iloc[:,1])-50,
#                      x = "Ajax",
#                      text = F"Currently Active COVID-19 Cases in Ontario Municipalities <br><b> {max(df_sum.reported_date).date()}",
#                      showarrow = False,
#                      font = dict(
#                              size = 16,
#                              color = '#3D92A8'),
#                      ) )
#
# fig.update_layout(annotations = annotations)

fig.update_layout(coloraxis=dict(colorscale="RdBu_r"))
fig.layout.update(showlegend=False)
fig.layout.coloraxis.update(showscale = False)

######************************* PLOT BEGINS: ********************************######

# Boostrap CSS
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                meta_tags = [
                {"name": "viewpoint", "content": "width=device-width, initial-scale=1"}
                ])

app.title = "ONT School COVID-19 Dashboard"
server = app.server

app.layout = html.Div(style = {'backgroundColor':'#711411', 'font-family': 'Verdana', 'margin-bottom' : '20px'}, children = [
    html.H1(children = "COVID-19 CASES in  ONTARIO SCHOOLS",
            style = {
                'textAlign' : 'center',
                'color' : 'lightgrey',
                'padding-top' : '25px',
                'padding-bottom' : '0px',
                'font-size' : '200%',
                'height' : '60px',
                'line-height': 1.2,
                'margin-top' : '30px',
                'font-family':'Monaca',
                'font-weight' : 'bold'
            }),

    #title = {'text': f"<span style='font-size:0.8em; color:#294C63'> Schools Days Completed:<br> {days_remain} To Go </span>"},
    html.H5(children =   f"UPDATED: {max(df_sum.reported_date).date()}",
            style = {
                'textAlign' : 'center',
                'color' : '#5DADE2',
                'color' : 'lightgrey',
                'padding-top' : '0px',
                'font-size' : '25px',
                'font-family':'Monaca',
                'height' : '20px',
                'line-height': 1.1,
                'font-weight' : 'bold',
                #'background-color' : 'lightblue'
                'font-variant-caps': 'small-caps'
            }),

    dcc.Graph(
        style = {'height':"100vh",
                 'margin-bottom' : '20px',
                 'margin-left' : '20px',
                 'margin-right' : '20px',
                 'margin-top' : '20px'},
        config = {'responsive': True},
        figure = fig,
    ),
    # html.P(children = '"Source:" <a ref> "https://data.ontario.ca/dataset/summary-of-cases-in-schools" target="_blank">  Schools COVID-19 Data</a>',
    #                   style = {
    #                       'textAlign' : 'right',
    #                       'color' : 'lightgrey',
    #                       'font' : 'Lucida Handwriting',
    #                       'font-size' : '13',
    #                       'font-style' : 'italic',
    #                       'font-weight' : 'bold',
    #                       'margin-bottom' : '10px',
    #                       'margin-left' : '10x'
    #                   }),

    html.Footer("Created By: Peter Stangolis",
                 style = {
                     'textAlign' : 'left',
                     'color' : 'lightgrey',
                     'font' : 'Lucida Handwriting',
                     'font-size' : '13',
                     'font-style' : 'italic',
                     'font-weight' : 'bold',
                     'margin-bottom' : '10px',
                     'margin-left' : '30px'
                 }),

    html.A("Data Source", href="https://data.ontario.ca/dataset/summary-of-cases-in-schools",
            target="_blank",

            style = {
                'textAlign' : 'left',
                'color' : 'lightgrey',
                'font-stye' : 'italic',
                'margin-left' : '30px'
            }
            ),
], className = 'ten columns offset-by-one'
)

if __name__ == '__main__':
    app.run_server(debug=True)
