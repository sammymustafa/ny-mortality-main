import pandas as pd
import altair as alt
import streamlit as st

### Data Loading and Preprocessing ###

def load_data():
    df = pd.read_csv("Vital_Statistics_Deaths_by_Age-Group__Sex__Race_Ethnicity__and_Selected_Cause_of_Death__Beginning_2003_20240214.csv")
    df.columns = df.columns.str.replace(' ', '-')
    df['Age-Group'] = df['Age-Group'].replace('45300', '1-9')
    df['Age-Group'] = df['Age-Group'].replace('45584', '10-19')
    df = df[df["Selected-Cause-of-Death"] != "Total"]
    df["Sex"] = df["Sex"].replace({"F": "Female", "M": "Male"})
    return df

df = load_data()
df.rename(columns={"Race-or-Ethnicity": "Race"}, inplace=True)
df.rename(columns={"Selected-Cause-of-Death": "Cause"}, inplace=True)

### Streamlit UI Components ###

st.title("NY Mortality Data Dashboard")

# Year Selector
years = df["Year"].unique()
year = st.slider("Select Year", min_value=min(years), max_value=max(years), value=2012)

# Gender Selector
gender_options = ["All"] + list(df["Sex"].unique())
gender = st.radio("Select Gender", options=gender_options)
gender_title = "Both Genders" if gender == "All" else gender + "s"

# Cause of Death Selector
cause_options = df["Cause"].unique()
selected_cause = st.selectbox("Select Cause of Death", options=cause_options)

### Data Filtering ###
if gender == "All":
    filtered_df = df[(df["Year"] == year) & (df["Cause"] == selected_cause)]
else:
    filtered_df = df[(df["Year"] == year) & (df["Sex"] == gender) & (df["Cause"] == selected_cause)]

### Visualizations ###

# Bar Chart: Deaths by Race/Ethnicity
bar_chart_data = filtered_df.groupby("Race")["Deaths"].sum().reset_index()
bar_chart_data = bar_chart_data.sort_values('Deaths', ascending=False)
race_order = ['White Non Hispanic', 'Black Non Hispanic', 'Hispanic', 'Other Non Hispanic', 'Not Stated']
bar_chart = alt.Chart(bar_chart_data).mark_bar().encode(
    x=alt.X('Race:N', title='Race/Ethnicity', sort=race_order),
    y=alt.Y("Deaths:Q", title="Number of Deaths")
).properties(
    title=f"Deaths by Race/Ethnicity in {year} for {gender_title} due to {selected_cause}"
)

st.altair_chart(bar_chart, use_container_width=True)

# Heatmap: Mortality Rates by Age Group and Race/Ethnicity
total_deaths = filtered_df['Deaths'].sum()
heatmap_data = filtered_df.groupby(["Age-Group", "Race"])["Deaths"].sum().reset_index()
heatmap_data['Proportion'] = heatmap_data['Deaths'] / total_deaths
age_group_order = ['<1', '1-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
heatmap = alt.Chart(heatmap_data).mark_rect().encode(
    x=alt.X('Age-Group:N', title='Age Group', sort=age_group_order),
    y=alt.Y("Race:N", title="Race/Ethnicity", sort=race_order),
    color=alt.Color('Proportion:Q', scale=alt.Scale(scheme="redyellowgreen"), title="Proportion of Total Deaths"),
    tooltip=["Age-Group", "Race", "Deaths", "Proportion"]
).properties(
    title=f"Mortality Rates by Age Group and Race/Ethnicity in {year} for {gender_title} due to {selected_cause}"
)

st.altair_chart(heatmap, use_container_width=True)

### Pie Chart: Cause of Death Proportion ###
if st.checkbox("Show Cause of Death Proportions"):
    # Calculate the total number of deaths for the year
    total_deaths_for_year = df[df["Year"] == year]['Deaths'].sum()

    # Get the cause of death proportions
    pie_chart_data = df[df["Year"] == year].groupby("Cause")["Deaths"].sum().reset_index()

    # Calculate the percentage of total deaths for each cause
    pie_chart_data['Percentage'] = (pie_chart_data['Deaths'] / total_deaths_for_year) * 100
    
    # Create the pie chart
    pie_chart = alt.Chart(pie_chart_data).mark_arc().encode(
        theta=alt.Theta(field="Deaths", type="quantitative"),
        color=alt.Color(field="Cause", type="nominal"),
        tooltip=[
            alt.Tooltip('Cause:N'),
            alt.Tooltip('Deaths:Q'),
            alt.Tooltip('Percentage:Q', title='Percentage', format='.1f')
        ]
    ).properties(
        title=f"Cause of Death Proportions in {year}"
    )

    st.altair_chart(pie_chart, use_container_width=True)


### Line Chart: Cause of Death Proportion ###
# Create a selection brush for the x-axis to enable range selection
brush = alt.selection(type='interval', encodings=['x'])

# Create a color condition that highlights the selected disease and dims others
highlight = alt.condition(brush, alt.Color('Cancer:N', legend=None), alt.value('lightgray'))

# Create the base line chart
base = alt.Chart(df).mark_line().encode(
    x=alt.X('Year:O', title='Year'),
    y=alt.Y('Deaths:Q', title='Death Count'),
    color='Cancer:N',
    opacity=alt.condition(brush, alt.value(0.7), alt.value(0.1))
).properties(
    width=600,
    height=300
).add_selection(
    brush
)

# Add a rule to highlight the selected disease line
selected_disease_rule = base.transform_filter(
    alt.datum.Cancer == cancer  # Use the selected cancer type from the dropdown
).mark_line().encode(
    size=alt.value(3)
)

# Combine the base chart with the highlighted rule
line_chart = base + selected_disease_rule

st.altair_chart(line_chart, use_container_width=True)