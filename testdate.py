import pandas as pd
import streamlit as st

# Sample DataFrame with "fecha" column in dd-mm-yyyy format
data = {
    "fecha": ["01-06-2023", "15-06-2023", "10-07-2023", "25-07-2023"],
    "value": [10, 15, 20, 25]
}
df = pd.DataFrame(data)

# Step 1: Convert "fecha" column to datetime format
df['fecha'] = pd.to_datetime(df['fecha'], format='%d-%m-%Y')

# Step 2: Create "month_select" column with the desired format
df['month_select'] = df['fecha'].dt.strftime('%B-%Y')

# Streamlit app
st.title("Data Selection by Month")

# Create a selectbox widget with unique "month_select" values
selected_month = st.selectbox("Select Month", sorted(df['month_select'].unique()))

# Step 3: Filter and aggregate data for the selected month
filtered_data = df[df['month_select'] == selected_month]
agg_data = filtered_data.groupby('month_select')['value'].agg(['sum', 'mean', 'count']).reset_index()

# Display the selected data
st.write("Selected Data:")
st.write(filtered_data)

# Display aggregated data
st.write(f"Aggregate Data for {selected_month}:")
st.write("Total Value:", agg_data['sum'].iloc[0])
st.write("Mean Value:", agg_data['mean'].iloc[0])
st.write("Count of Instances:", agg_data['count'].iloc[0])
