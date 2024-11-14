import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# 1.1 Load the data
codebook_csv_path = 'data/codebook.csv'
recommended_citation_csv_path = 'data/recommended_citation.csv'
undp_composite_indices_csv_path = 'data/undp_composite_indices.csv'

# Load the data into dataframes for exploration
codebook_df = pd.read_csv(codebook_csv_path)
recommended_citation_df = pd.read_csv(recommended_citation_csv_path)
undp_composite_indices_df = pd.read_csv(undp_composite_indices_csv_path)

# 1.2 Select the HDI data of the countries regardless of gender
df_tidy = undp_composite_indices_df.query('gender == "Total"').drop('gender',axis=1)

# 1.3 Remove the NA
# Drop rows where crucial columns have missing values 
df_tidy_drop = df_tidy.dropna(subset=['human_development_index'])

# Change the value of region
df_cleaned = df_tidy_drop.copy() # To avoid SettingWithCopyWarning
df_cleaned.loc[df_cleaned['country'] == 'World', 'region'] = 'World'
replace_dict = {'SA': 'South Asia',
                'SSA': 'Sub-Saharan Africa',
                'ECA': 'Europe and Central Asia',
                'AS': 'Arab States',
                'LAC': 'Latin America and the Caribbean',
                'EAP': 'East Asia and the Pacific'
}
df_cleaned['region'] = df_cleaned['region'].replace(replace_dict)
df_cleaned['region'] = df_cleaned['region'].fillna('Developed Region')

# 1.4 Deal with the duplicates
# Check the duplicates

# 1.5 Create new variable and change the value for region
df_cleaned = df_cleaned.sort_values(['country', 'year'])
df_cleaned['hdi_change'] = df_cleaned.groupby('country')['human_development_index'].pct_change()

# Fill change percent of the first year of each country with 0
df_cleaned['hdi_change'] = df_cleaned['hdi_change'].fillna(0)

# All regions
sample_data = df_cleaned.copy()

# Calculate the average HDI value for each country and sort by HDI
avg_hdi_per_country = sample_data.groupby('country')['human_development_index'].mean().sort_values()

# Create a color gradient (from purple to red)
norm = plt.Normalize(vmin=avg_hdi_per_country.min(), vmax=avg_hdi_per_country.max())
colorscale = px.colors.sequential.Turbo[::-1]  

# Assign colors to these countries
country_color_map = {country: px.colors.sample_colorscale(colorscale, norm(hdi))[0]
                     for country, hdi in avg_hdi_per_country.items()}

# Add assigned colors to a dataset
sample_data['color'] = sample_data['country'].map(country_color_map)

# Create a Hover Map Message
sample_data['custom_data'] = sample_data.apply(
    lambda row: [row['country'], row['year'], row['human_development_index'], row['hdi_change'],
                 row['life_expectancy_at_birth'], row['expected_years_of_schooling'],
                 row['mean_years_of_schooling'], row['gross_national_income_per_capita']],
    axis=1
)

def update_line_chart(selected_regions, hoverData):
    df = sample_data[sample_data['region'].isin(selected_regions)] 
    fig = px.line(df, x='year', y='human_development_index', color='country',
                  line_group='country',
                  labels={
                      'year': 'Year',
                      'human_development_index': 'Human Development Index (HDI)'
                  },
                  custom_data=['custom_data'])

    for country in avg_hdi_per_country.index:
        if country == 'World':
            fig.update_traces(selector=dict(name=country),
                              line=dict(dash='solid', width=2, color='black'))
        else:
            fig.update_traces(selector=dict(name=country),
                              line=dict(dash='solid', width=1, color=country_color_map[country]))

    # When checking hovering, highlight the line
    if hoverData:
        hovered_country = hoverData['points'][0]['customdata'][0][0]   
        fig.update_traces(selector=dict(name=hovered_country),
                          line=dict(width=4))

    fig.update_traces(
        hovertemplate="<b>%{customdata[0][0]}</b><br>"
                      "%{customdata[0][1]} HDI value: %{customdata[0][2]:.3f}<br>"
                      "HDI change from previous year: %{customdata[0][3]:+.2%}<br>"
                      "Life expectancy at birth: %{customdata[0][4]:.1f} years<br>"
                      "Expected years of schooling: %{customdata[0][5]:.1f} years<br>"
                      "Mean years of schooling: %{customdata[0][6]:.1f} years<br>"
                      "Gross National Income per capita: %{customdata[0][7]:,.0f} (constant 2017 PPP$)"
    )

    fig.update_layout(width=1300, 
                      height=700, 
                      xaxis=dict(tickmode='linear', dtick=2),
                      yaxis=dict(
                          tickvals=[0.200, 0.280, 0.360, 0.440, 0.520, 0.600, 0.680, 0.760, 0.840, 0.920, 1.000],
                          ticktext=['0.200', '0.280', '0.360', '0.440', '0.520', '0.600', '0.680', '0.760', '0.840', '0.920', '1.000']
                      ),
                      annotations=[
                          dict(
                              x=1.0, 
                              y=1.05, 
                              xref="paper",
                              yref="paper",
                              text="<b>Low (< 0.550)</b> | <b>Medium (0.550-0.699)</b> | <b>High (0.700-0.799)</b> | <b>Very high (≥ 0.800)</b>",
                              showarrow=False,
                              align="center",
                              bgcolor="rgba(255,255,255,0.8)",
                              bordercolor="black",
                              borderwidth=1,
                              font=dict(size=10)
                          )
                      ])

    return fig

def create_app():
    # Plot the graph
    app = Dash(__name__)

    app.layout = html.Div([
        html.H4('HDI Over Time for All Countries'),
        dcc.Graph(id="graph"),
        # Create a selector of the regions
        dcc.Checklist(
            id="checklist",
            options=[
                {'label': 'Arab States', 'value': 'Arab States'},
                {'label': 'East Asia and the Pacific', 'value': 'East Asia and the Pacific'},
                {'label': 'Europe and Central Asia', 'value': 'Europe and Central Asia'},
                {'label': 'Latin America and the Caribbean', 'value': 'Latin America and the Caribbean'},
                {'label': 'South Asia', 'value': 'South Asia'},
                {'label': 'Sub-Saharan Africa', 'value': 'Sub-Saharan Africa'},
                {'label': 'Developed Region', 'value': 'Developed Region'},
                {'label': 'World', 'value': 'World'}
            ],
            value=['World', 'East Asia and the Pacific'],  
            inline=True
        ),
    ])

    app.callback(
        Output("graph", "figure"), 
        Input("checklist", "value"),
        Input("graph", "hoverData")
    )(update_line_chart)

    server = app.server
    return app


