import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import plotly.io as pio
import dash
from dash import dcc
from dash import html
from dash_bootstrap_components import themes
from dash.dependencies import Input, Output
external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootswatch@5.3.3/dist/slate/bootstrap.min.css']
pio.templates.default = 'plotly_dark'

# dowload and clean data
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')


"""
The gss_clean dataframe now contains the following features:

id - a numeric unique ID for each person who responded to the survey
weight - survey sample weights
sex - male or female
education - years of formal education
region - region of the country where the respondent lives
age - age
income - the respondent's personal annual income
job_prestige - the respondent's occupational prestige score, as measured by the GSS using the methodology described above
mother_job_prestige - the respondent's mother's occupational prestige score, as measured by the GSS using the methodology described above
father_job_prestige -the respondent's father's occupational prestige score, as measured by the GSS using the methodology described above
socioeconomic_index - an index measuring the respondent's socioeconomic status
satjob - responses to "On the whole, how satisfied are you with the work you do?"
relationship - agree or disagree with: "A working mother can establish just as warm and secure a relationship with her children as a mother who does not work."
male_breadwinner - agree or disagree with: "It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family."
men_bettersuited - agree or disagree with: "Most men are better suited emotionally for politics than are most women."
child_suffer - agree or disagree with: "A preschool child is likely to suffer if his or her mother works."
men_overwork - agree or disagree with: "Family life often suffers because men concentrate too much on their work."
"""

# introduction to data and dashboard
intro = """
In [their 2022 work on the topic](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9842568/), Rotman and Mandel explain that the gender wage gap can be broken into two components: the explained and the unexplained. The explained component has to do with the fact that women, especially in the past but even now, tend to have less education and full-time working experience. Women's education was not as well-supported historically, and even now women are more likely to sacrifice in their career aspirations for family, including raising children. However, there is still an unexplained component of the gap that has to do with the bias in the system. The authors argue that this unexplained portion results in lower returns for women on their years of education and job experience. 

The General Social Survey (GSS) is a wealth of information about political attitudes, moral values, financial priorities and many other topics collected from Americans every other year, along with the demographics of the respondants. Its purpose is to inform research and policy, and is freely accessible [here](https://gss.norc.org/Get-The-Data). This dashboard displays data from the 2019 study. We will use this data to explore the gender wage gap ourselves.
"""

# table
incomes = gss_clean[['income',
                     'job_prestige',
                     'socioeconomic_index',
                     'education',
                     'sex']].groupby(
    'sex').agg('mean').reset_index()
incomes.columns = ['Sex',
                   'Mean Income',
                   'Occupational Prestige',
                   'Socioeconomic Status',
                   'Years of Education']
incomes = round(incomes, 2)
table = ff.create_table(incomes,
                       colorscale = [[0, '#ab63fa'],
                                     [.5, '#f2e5ff'],
                                     [1, '#ffffff']]
                       )

# scatterplot
scatter = px.scatter(gss_clean, x = 'job_prestige', y = 'income', color = 'sex',
       color_discrete_map = {'male':'#636efa', 'female':'#ef553b'},
                     height = 400, width = 630,
                     labels = {'job_prestige' : 'Occupational Prestige',
                               'income' : 'Income'},
                     hover_data = ['sex',
                                   'income',
                                   'job_prestige',
                                   'education',
                                   'socioeconomic_index'],
                     trendline = 'ols'
                    )
scatter.update_layout(legend = {'yanchor' : 'top',
                                'y' : 0.99,
                                'xanchor' : 'left',
                                'x' : 0.01
                               }
                     )

# side-by-side boxplots
box1 = px.box(gss_clean, x = 'income', y = 'sex', color = 'sex',
              height = 200, width = 315,
              labels = {'income' : 'Income', 'sex' : ''},
       color_discrete_map = {'male':'#636efa', 'female':'#ef553b'}

      )
box1.update_layout(showlegend = False)

box2 = px.box(gss_clean, x = 'job_prestige', y = 'sex', color = 'sex',
              height = 200, width = 315,
              labels = {'job_prestige' : 'Occupational Prestige',
                        'sex' : ''},
       color_discrete_map = {'male':'#636efa', 'female':'#ef553b'}
      )
box2.update_layout(showlegend = False)

# facet boxplots
boxes = gss_clean[['income', 'sex', 'job_prestige']]
boxes['prestige_bin'] = pd.cut(boxes.job_prestige,
                                bins = 6)
boxes = boxes.dropna()

facet_boxes = px.box(boxes, x = 'income', y = 'sex', color = 'sex',
       height = 500, width = 630,
       color_discrete_map = {'male':'#636efa', 'female':'#ef553b'},
       facet_col = 'prestige_bin', facet_col_wrap = 2,
       labels = {'income' : 'Income', 'sex' : ''},
      )
facet_boxes.for_each_annotation(
    lambda a: a.update(
        text = a.text.replace("prestige_bin=", "")
    )
)
facet_boxes.update_layout(showlegend = False)

# app
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

app.layout = html.Div(
    html.Div(
    [
        html.Br(),
        html.Br(),
        html.H1('Gender Pay Gap: A Glimpse from the 2019 GSS'),
        dcc.Markdown(children = intro),
        
        html.H3('Overview of Gender Pay Gap in Numbers'),
        dcc.Graph(figure = table),
        
        html.Br(),
        html.Br(),
        html.Hr(),
        
        # Interactive barplot
        html.Div([
            html.H3('Response to the question:'),
            html.H3(id = 'title')
        ], style = {'width' : '20%', 'float' : 'left'}
        ),

        html.Div([
            html.Div([
                html.Label('Category:'),
                dcc.Dropdown(id = 'category',
                             options = [{'label' : 'Sex', 'value' : 'sex'},
                                        {'label' : 'Years of education', 'value' : 'education'},
                                        {'label' : 'Region', 'value' : 'region'}
                                       ],
                             value = 'sex')
            ], style = {'width' : '20%', 'float' : 'left'}),
            
            html.Div([
                html.Label('Question:'),
                dcc.Dropdown(id = 'question',
                             options = [{'label' : "On the whole, how satisfied are you with the work you do?",
                                         'value' : 'satjob'},
                                        {'label' : "It is much better for everyone involved if the man...",
                                         'value' : 'male_breadwinner'},
                                        {'label' : "A working mother can establish just as warm and secure...",
                                         'value' : 'relationship'},
                                        {'label' : "Most men are better suited emotionally for politics...",
                                         'value' : 'men_bettersuited'},
                                        {'label' : "A preschool child is likely to suffer if his or her mother works.",
                                         'value' : 'child_suffer'},
                                        {'label' : "Family life often suffers because men concentrate too much...",
                                         'value' : 'men_overwork'}
                                       ],
                             value = 'satjob')
            ], style = {'width' : '75%', 'float' : 'right'}
            ),
            
            html.Br(),
            html.Br(),
            html.Br(),
            dcc.Graph(id = 'user_bar'),
        ], style = {'width' : '70%', 'float' : 'right'}
        ),
        

        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Hr(),


        html.Div(html.H3('Income and Occupational Prestige by Sex'),
                 style = {'width' : '25%', 'float' : 'left'}),
        html.Div(dcc.Graph(figure = scatter),
                 style = {'width' : '70%', 'float' : 'right'}),
        
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Hr(),
        
        
        html.Div(html.H3('Distribution of Income and Occupational Prestige by Sex'),
                 style = {'width' : '25%', 'float' : 'left'}),
        html.Div(
            [
                html.Div(dcc.Graph(figure = box1),
                        style = {'width' : '50%', 'float' : 'left'}),
                html.Div(dcc.Graph(figure = box2),
                        style = {'width' : '50%', 'float' : 'right'})
            ], style = {'width' : '70%', 'float' : 'right'}
        ),

        
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(),
        html.Hr(),
        
        
        html.Div(html.H3('Distribution of Income by Sex and Occupational Prestige (Bins)'),
                 style = {'width' : '25%', 'float' : 'left'}),
        html.Div(dcc.Graph(figure = facet_boxes),
                 style = {'width' : '70%', 'float' : 'right'}),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br(),
        html.Br(), html.Br(), html.Br()
    ], style = {'width' : '90%', 'float' : 'right'}
    ), style = {'width' : '80%', 'float' : 'left'},
    

)





"""
 "On the whole, how satisfied are you with the work you do?"
"A working mother can establish just as warm and secure a relationship with her children as a mother who does not work."
"It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family."
"Most men are better suited emotionally for politics than are most women."
"A preschool child is likely to suffer if his or her mother works."
"Family life often suffers because men concentrate too much on their work."
"""


@app.callback(Output(component_id = 'title', component_property = 'children'),
              [Input(component_id = 'category', component_property = 'value'),
              Input(component_id = 'question', component_property = 'value')])



def title(category, question):
        q = {'satjob' : "On the whole, how satisfied are you with the work you do?",
         'relationship' : "A working mother can establish just as warm and secure a relationship with her children as a mother who does not work.",
         'male_breadwinner' : "It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family.",
         'men_bettersuited' : "Most men are better suited emotionally for politics than are most women.",
         'child_suffer' : "A preschool child is likely to suffer if his or her mother works.",
         'men_overwork' : "Family life often suffers because men concentrate too much on their work"
        }
        
        c = {'sex' : 'sex',
             'education' : 'years of education',
             'region' : 'region'}
        
        return f'"{q[question]}" by {c[category]}'

@app.callback(Output(component_id = 'user_bar', component_property = 'figure'),
             [Input(component_id = 'category', component_property = 'value'),
              Input(component_id = 'question', component_property = 'value')])
    
def user_bar(category, question):
    bars = gss_clean[[category, question]].value_counts().reset_index()
    barplot = px.bar(bars, x = category, y = 'count', color = question,
                     height = 400, width = 630,
                     labels = {'male_breadwinner' : 'Response',
                                'satjob' : 'Response',
                                'relationship' : 'Response',
                                'men_bettersuited' : 'Response',
                                'child_suffer' : 'Response',
                                'men_overwork' : 'Response',
                                'count' : 'Frequency'
                           },
                     barmode = 'group'
                 )
    return barplot.update_layout(legend = {'yanchor' : 'top',
                                'y' : 0.95,
                                'xanchor' : 'right',
                                'x' : 0.95
                                           },
                                 xaxis = {'title' : ''},
                                 
                     )

if __name__ == '__main__':
    app.run(debug = True, jupyter_mode = 'external')
