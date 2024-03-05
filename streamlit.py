import pandas as pd
import altair as alt
import streamlit as st

### Data Loading and Preprocessing ###

def load_data():
    df = pd.read_csv("Vital_Statistics_Deaths_by_Age-Group__Sex__Race_Ethnicity__and_Selected_Cause_of_Death__Beginning_2003_20240214.csv")
    df['Age-Group'] = df['Age-Group'].replace('45300', '1-9')
    df['Age-Group'] = df['Age-Group'].replace('45584', '10-19')
    df.columns = df.columns.str.replace(' ', '-')
    df = df[df["Cause"] != "Total"]
    df["Sex"] = df["Sex"].replace({"F": "Female", "M": "Male"})
    return df

df = load_data()
df.rename(columns={"Race": "Race"}, inplace=True)
df.rename(columns={"Cause": "Cause"}, inplace=True)

### Streamlit UI Components ###

st.title("NY Mortality Data Dashboard")

# Year Selector
years = df["Year"].unique()
year = st.slider("Select Year", min_value=min(years), max_value=max(years), value=2012)

# Gender Selector
gender_options = ["All"] + list(df["Sex"].unique())
gender = st.radio("Select Gender", options=gender_options)

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
bar_chart = alt.Chart(bar_chart_data).mark_bar().encode(
    x=alt.X("Race:N", title="Race/Ethnicity"),
    y=alt.Y("Deaths:Q", title="Number of Deaths"),
    color="Race:N"
).properties(
    title=f"Deaths by Race/Ethnicity in {year} for {gender} due to {selected_cause}"
)

st.altair_chart(bar_chart, use_container_width=True)

# Heatmap: Mortality Rates by Age Group and Race/Ethnicity
heatmap_data = filtered_df.groupby(["Age-Group", "Race"])["Deaths"].sum().reset_index()
heatmap = alt.Chart(heatmap_data).mark_rect().encode(
    x=alt.X("Age-Group:N", title="Age Group"),
    y=alt.Y("Race:N", title="Race/Ethnicity"),
    color=alt.Color("Deaths:Q", title="Number of Deaths", scale=alt.Scale(scheme="redyellowgreen")),
    tooltip=["Age-Group", "Race", "Deaths"]
).properties(
    title=f"Mortality Rates by Age Group and Race/Ethnicity in {year} for {gender} due to {selected_cause}"
)

st.altair_chart(heatmap, use_container_width=True)

### Pie Chart: Cause of Death Proportion ###

if st.checkbox("Show Cause of Death Proportions"):
    pie_chart_data = df[df["Year"] == year].groupby("Cause")["Deaths"].sum().reset_index()
    pie_chart = alt.Chart(pie_chart_data).mark_arc().encode(
        theta=alt.Theta(field="Deaths", type="quantitative"),
        color=alt.Color(field="Cause", type="nominal"),
        tooltip=["Cause", "Deaths"]
    ).properties(
        title=f"Cause of Death Proportions in {year}"
    )

    st.altair_chart(pie_chart, use_container_width=True)