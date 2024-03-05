import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Hypothetical data for the dashboard
df = pd.read_csv("Vital_Statistics_Deaths_by_Age-Group__Sex__Race_Ethnicity__and_Selected_Cause_of_Death__Beginning_2003_20240214.csv")

# Group data by Year and Cause of Death for line chart
line_chart_data = df.groupby(['Year', 'Cause of Death'])['Deaths'].sum().unstack()

# Group data by Cause of Death for pie chart
pie_chart_data = df[df['Year'] == 2010]['Deaths'].groupby(df['Cause of Death']).sum()

# Group data by County for bar chart
bar_chart_data = df[df['Year'] == 2010]['Deaths'].groupby(df['County']).sum()

# Create line chart
plt.figure(figsize=(10, 6))
sns.lineplot(data=line_chart_data)
plt.title('Trend of Deaths by Cause Over Years')
plt.ylabel('Number of Deaths')
plt.xlabel('Year')
plt.legend(title='Cause of Death')
plt.grid(True)
plt.tight_layout()  # Adjust layout to fit the figure nicely
plt.savefig('line_chart.png')  # Save the figure as a .png file
plt.show()

# Create pie chart
plt.figure(figsize=(8, 8))
pie_chart_data.plot(kind='pie', autopct='%1.1f%%')
plt.title('Cause of Death Distribution for 2010')
plt.ylabel('')  # Hide the y-axis label
plt.tight_layout()  # Adjust layout to fit the figure nicely
plt.savefig('pie_chart.png')  # Save the figure as a .png file
plt.show()

# Create bar chart
plt.figure(figsize=(10, 6))
sns.barplot(x=bar_chart_data.index, y=bar_chart_data.values)
plt.title('Total Number of Deaths by County for 2010')
plt.ylabel('Number of Deaths')
plt.xlabel('County')
plt.xticks(rotation=45)
plt.tight_layout()  # Adjust layout to fit the figure nicely
plt.savefig('bar_chart.png')  # Save the figure as a .png file
plt.show()
