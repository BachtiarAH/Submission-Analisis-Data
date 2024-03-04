import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

all_data = pd.read_csv("main_data.csv")

with st.sidebar:
    st.header("Filter")
    # Convert 'datetime' column to datetime format
    all_data['datetime'] = pd.to_datetime(all_data['datetime'])

    # Extract minimum and maximum dates from the dataset
    min_date = all_data['datetime'].min().date()
    max_date = all_data['datetime'].max().date()
    selected_date_range = st.date_input("Select Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date))

    
st.header("Dashboard Air Quality")


clean_combined_df = all_data[(all_data['datetime'] >= pd.to_datetime(selected_date_range[0])) & (all_data['datetime'] <= pd.to_datetime(selected_date_range[1]))]

st.subheader(f"Analysis of PM2.5 Levels from {selected_date_range[0]} to {selected_date_range[1]} at Multiple Stations")

with st.container():
    average_pm25_each_station = clean_combined_df.groupby('station')['PM2.5'].mean()
    max_pm25_station = average_pm25_each_station.idxmax()
    min_pm25_station = average_pm25_each_station.idxmin()
    
    plt.figure(figsize=(18, 8))
    bars = plt.bar(x=average_pm25_each_station.keys(), height=average_pm25_each_station.values)
    
    for bar in bars:
        if bar.get_height() == average_pm25_each_station[max_pm25_station]:
            bar.set_color('red')  # Color max PM2.5 station bar red
        elif bar.get_height() == average_pm25_each_station[min_pm25_station]:
            bar.set_color('green')  # Color min PM2.5 station bar green
    
    plt.xlabel('Stations')
    plt.ylabel('PM2.5')
    plt.title('Average PM2.5 Level per Station from 2013 to 2017')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Filter out None values
    average_pm25_each_station = {station: pm25 for station, pm25 in average_pm25_each_station.items() if pm25 is not None}

    # Divide the screen into six columns
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # List of all columns
    columns = [col1, col2, col3, col4, col5, col6]

    # Get the station with the smallest and largest PM2.5 values
    min_station = min(average_pm25_each_station, key=average_pm25_each_station.get)
    max_station = max(average_pm25_each_station, key=average_pm25_each_station.get)

    # Iterate over the keys and values of average_pm25_each_station
    for i, (station, pm25) in enumerate(average_pm25_each_station.items()):
    # Format PM2.5 value with two digits after the decimal point
        pm25_formatted = "{:.2f}".format(pm25)
        
        # Write station name and PM2.5 value in respective column
        with columns[i % len(columns)]:
            if station == min_station:
                st.metric(label=f"{station} (Δ)", value=pm25_formatted, delta="▼ min", delta_color="normal")
            elif station == max_station:
                st.metric(label=f"{station} (Δ)", value=pm25_formatted, delta="▲ max", delta_color="inverse")
            else:
                st.metric(label=station, value=pm25_formatted)
    
    
    # Display the chart
    st.pyplot(plt)
    
    
st.subheader("Corelation between PM10 and CO")
with st.container():
    mean_PM10_monthly = clean_combined_df.groupby(['year', 'month'])['PM10'].mean()
    mean_CO_monthly = clean_combined_df.groupby(['year', 'month'])['CO'].mean()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="Average PM10", value="{:.2f}".format(mean_PM10_monthly.mean()))
    
    with col2:
        st.metric(label="Average CO", value="{:.2f}".format(mean_CO_monthly.mean()))

    with st.container():
        plt.figure(figsize=(12, 8))
        sns.regplot(x=mean_PM10_monthly.values, y=mean_CO_monthly.values)
        plt.xlabel("PM10 levels")
        plt.ylabel("CO levels")
        st.pyplot(plt)


    
    
st.subheader("Comparison of SO2 Levels Between Summer and Winter Months")
with st.container():
    mean_SO2 = clean_combined_df.groupby(['year', 'month'])['SO2'].mean()
    mean_SO2_dict = mean_SO2.to_dict()  
    winter_month = [1,2,11,12]
    summer_month = [6,7,8,9]

    summer_SO2 = {}
    winter_SO2 = {}

    for key, value in mean_SO2_dict.items():
        if key[1] in summer_month:
            summer_SO2[key] = value
        elif key[1] in winter_month:
            winter_SO2[key] = value
    
    # Convert the keys to datetime objects
    summer_dates = [datetime.datetime(year, month, 1) for year, month in summer_SO2.keys()]
    winter_dates = [datetime.datetime(year, month, 1) for year, month in winter_SO2.keys()]

    # Create a new figure
    plt.figure(figsize=(16,8))

    # Plot summer_SO2 and winter_SO2
    plt.bar(summer_dates, list(summer_SO2.values()), label='Summer SO2')
    plt.bar(winter_dates, list(winter_SO2.values()), label='Winter SO2')

    # Add a legend
    plt.legend()
    
    st.pyplot(plt)
    
st.caption("Copyright (c) 2024 Bachtiar Arya Habibie")