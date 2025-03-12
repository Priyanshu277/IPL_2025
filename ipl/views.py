import os
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64 as b64
from django.shortcuts import render
from django.conf import settings

def create_plot_safely(plot_function):
    """Helper function to safely create plots"""
    plt.switch_backend('Agg')
    try:
        return plot_function()
    finally:
        plt.close('all')

team_map ={"Mumbai Indians":"Mumbai Indians",
          "Chennai Super Kings":"Chennai Super Kings",
          "Kolkata Knight Riders":"Kolkata Knight Riders",
          "Royal Challengers Bangalore":"Royal Challengers Bangalore",
          "Royal Challengers Bengaluru":"Royal Challengers Bangalore",
          "Rajasthan Royals":"Rajasthan Royals",
          "Kings XI Punjab":"Kings XI Punjab",
          "Punjab Kings":"Kings XI Punjab",
          "Sunrisers Hyderabad":"Sunrisers Hyderabad",
          "Deccan Chargers":"Sunrisers Hyderabad",
          "Delhi Capitals":"Delhi Capitals",
          "Delhi Daredevils":"Delhi Capitals",
          "Gujarat Titans":"Gujarat Titans",
          "Gujarat Lions":"Gujarat Titans",
          "Lucknow Super Giants":"Lucknow Super Giants",
          "Pune Warriors":"Pune Warriors",
          "Rising Pune Supergiant":"Pune Warriors",
          "Rising Pune Supergiants":"Pune Warriors",
          "Kochi Tuskers Kerala":"Kochi Tuskers Kerala"}

def preprocess_datamatch():
    data_path_match = os.path.join(settings.BASE_DIR, "ipl/data/matches.csv")
    df_match = pd.read_csv(data_path_match)
    df_match.loc[(df_match['city'].isna()) & (df_match['venue'] == 'Sharjah Cricket Stadium'), 'city'] = 'Sharjah'
    df_match.loc[(df_match['city'].isna()) & (df_match['venue'] == 'Dubai International Cricket Stadium'), 'city'] = 'Dubai'
    df_match.replace({'season': {"2020/21": "2020", "2009/10": "2010", "2007/08": "2008"}}, inplace=True)

    df_match['team1']= df_match['team1'].map(team_map)
    df_match['team2']= df_match['team2'].map(team_map)
    df_match['winner']= df_match['winner'].map(team_map)
    df_match['toss_winner']= df_match['toss_winner'].map(team_map)

    return df_match

def preprocess_datadel():
    data_path_del = os.path.join(settings.BASE_DIR, "ipl/data/deliveries.csv")
    
    df_del = pd.read_csv(data_path_del)

    df_del['batting_team']= df_del['batting_team'].map(team_map)
    df_del['bowling_team']= df_del['bowling_team'].map(team_map)

    return df_del

df_match = preprocess_datamatch()
df_del = preprocess_datadel()

def match_stats(request):
    def generate_plots():
        plots = {}
        # Generate only the charts needed for match statistics
        season_counts = df_match['season'].value_counts().sort_index()

        # Ploting the trend as a line chart
        plt.figure(figsize=(10, 6))  
        plt.plot(season_counts.index, season_counts.values, marker='o', linestyle='-', color='blue')

        # Adding titles and labels
        plt.title('Trend of Total Matches Over Seasons', fontsize=16)
        plt.xlabel('Season', fontsize=12)
        plt.ylabel('Number of Matches', fontsize=12)

        # Annotating each data point with the value
        for i, value in enumerate(season_counts.values):
            plt.text(season_counts.index[i], value, str(value), fontsize=10, ha='center', va='bottom')
        plt.xticks(rotation=45)  
        plt.grid(True)           
        
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        plots['plot1_base64'] = b64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close()

        # Distribution of Match Results
        result_distribution = df_match['result'].value_counts()

        # Creating the bar plot
        plt.figure(figsize=(10, 6))
        sns.barplot(x=result_distribution.index, y=result_distribution.values, palette='viridis')

        # Adding titles and labels
        plt.title('Distribution of Match Results', fontsize=16)
        plt.xlabel('Result', fontsize=12)
        plt.ylabel('Number of Matches', fontsize=12)

        # Showing the values on top of the bars
        for index, value in enumerate(result_distribution):
            plt.text(index, value, f'{value}', ha='center', va='bottom')
        plt.xticks(rotation=45)  
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        plots['plot5_base64'] = b64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close()

        
        # Removing rows where the winner is missing
        df_clean = df_match.dropna(subset=['winner'])

        # Grouping by toss decision and counting how often each decision leads to a win
        wins_by_decision = df_clean.groupby('toss_decision').size().reset_index(name='wins')

        # Calculating the percentage of matches won by teams batting first vs. fielding first
        total_matches = df_clean.shape[0]
        wins_by_decision['percentage'] = (wins_by_decision['wins'] / total_matches) * 100

        # Plotting the results
        plt.figure(figsize=(8, 5))
        sns.barplot(data=wins_by_decision, x='toss_decision', y='percentage', palette='Set2')

        # Adding titles and labels
        plt.title('Percentage of Matches Won by Toss Decision', fontsize=16)
        plt.xlabel('Toss Decision (Bat First vs Field First)', fontsize=14)
        plt.ylabel('Percentage of Wins (%)', fontsize=14)

        # Adding values on top of the bars
        for index, row in wins_by_decision.iterrows():
            plt.text(index, row['percentage'] + 1, f'{row["percentage"]:.1f}%', 
                    ha='center', fontsize=12)

        plt.ylim(0, 100)
        plt.grid(axis='y', linestyle='--', alpha=0.7) 
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        plots['plot9_base64'] = b64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close()

        # Filtering matches where super_over is 'Y'
        super_over_matches = df_match[df_match['super_over'] == 'Y']

        # Group by season and counting the number of super overs
        super_over_by_season = super_over_matches.groupby('season').size().reset_index(name='super_over_count')

        plt.figure(figsize=(10, 6))
        plt.plot(super_over_by_season['season'], super_over_by_season['super_over_count'], marker='o', color='b')
        plt.title('Number of Super Overs Over Time')
        plt.xlabel('Season')
        plt.ylabel('Number of Super Overs')
        plt.xticks(rotation=45)
        plt.grid(True)

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        plots['plot10_base64'] = b64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close()

        # Combine umpire1 and umpire2 counts by adding the series
        umpire_counts = df_match['umpire1'].value_counts().add(df_match['umpire2'].value_counts(), fill_value=0)

        # Sorting by the total count in descending order
        umpire_counts = umpire_counts.sort_values(ascending=False)

        # Top 10 umpires
        top_umpires = umpire_counts.head(10)

        # Plotting the results
        plt.figure(figsize=(10, 6))
        sns.barplot(x=top_umpires.index, y=top_umpires.values, palette='viridis')

        # Adding titles and labels
        plt.title('Top 10 Umpires by Match Counts', fontsize=16)
        plt.xlabel('Umpires', fontsize=14)
        plt.ylabel('Number of Matches', fontsize=14)
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

        # Adding values on top of the bars
        for index, value in enumerate(top_umpires.values):
            plt.text(index, value + 1, int(value), ha='center', fontsize=12)

        plt.grid(axis='y', linestyle='--', alpha=0.7) 
        plt.tight_layout()  

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        plots['plot11_base64'] = b64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close()


        return plots

    context = create_plot_safely(generate_plots)
    return render(request, "match_stats.html", context)

def venue_stats(request):
    def generate_plots():
        plots = {}
        # Replace NaN values in 'city' column with 'Unknown' and count the occurrences
        city_counts = df_match['city'].replace(np.NaN, 'Unknown').value_counts()

        # Creating a bar plot
        plt.figure(figsize=(12, 6))  # Set the figure size
        sns.barplot(x=city_counts.index, y=city_counts.values, palette='viridis')

        # Add titles and labels
        plt.title('Number of Matches Hosted by Each City', fontsize=16)
        plt.xlabel('City', fontsize=12)
        plt.ylabel('Number of Matches', fontsize=12)
        plt.xticks(rotation=90)
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        plots['plot2_base64'] = b64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close()

        return plots

    context = create_plot_safely(generate_plots)
    return render(request, "venue_stats.html", context)

def performance_stats(request):
    def generate_plots():
        plots = {}
        # Calculating the mean of 'target_runs'
        mean_target_runs = df_match['target_runs'].mean()

        # Creating histogram plot to show the distribution 
        plt.figure(figsize=(10, 6))  # Set the figure size
        sns.histplot(df_match['target_runs'].dropna(), bins=30, kde=True, color='blue') 

        # Adding a vertical line for the mean
        plt.axvline(mean_target_runs, color='red', linestyle='--', label=f'Mean: {mean_target_runs:.2f}')

        # Adding titles and labels
        plt.title('Distribution of Target Runs', fontsize=16)
        plt.xlabel('Target Runs', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.legend()
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        plots['plot3_base64'] = b64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close()

        # distribution of results won by runs
        runs_margin = df_match[df_match['result'] == 'runs']['result_margin']

        # Ploting the distribution of result margins using histogram 
        plt.figure(figsize=(10, 6))
        sns.histplot(runs_margin, bins=20, kde=True, color='skyblue')

        # Adding titles and labels
        plt.title('Distribution of Result Margin in Matches Won by Runs', fontsize=16)
        plt.xlabel('Result Margin (Runs)', fontsize=14)
        plt.ylabel('Frequency', fontsize=14)
        plt.grid()

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        plots['plot6_base64'] = b64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close()

        # distribution of results won by wickets
        wickets_margin = df_match[df_match['result'] == 'wickets']['result_margin']

        # Plot the distribution of result margins using histogram
        plt.figure(figsize=(10, 6))
        sns.histplot(wickets_margin, bins=20, kde=True, color='lightcoral')

        # Adding titles and labels
        plt.title('Distribution of Result Margin in Matches Won by Wickets', fontsize=16)
        plt.xlabel('Result Margin (Wickets)', fontsize=14)
        plt.ylabel('Frequency', fontsize=14)
        plt.grid()

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        plots['plot7_base64'] = b64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close()

        # average result margin across seasons for both runs and wickets
        result_margins = df_match[(df_match['result'] == 'runs') | (df_match['result'] == 'wickets')]

        # Creating a pivot table for average result margins by season and result type
        avg_result = pd.pivot_table(
            data=result_margins, 
            index='season', 
            columns='result', 
            values='result_margin', 
            aggfunc='mean'
        )

        # Resetting the index for plotting
        avg_result.reset_index(inplace=True)

        # Plotting the average result margins
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=avg_result, x='season', y='runs', marker='o', label='Average Margin (Runs)', color='blue')
        sns.lineplot(data=avg_result, x='season', y='wickets', marker='o', label='Average Margin (Wickets)', color='orange')

        # Adding titles and labels
        plt.title('Average Result Margin by Season (Runs vs Wickets)', fontsize=16)
        plt.xlabel('Season', fontsize=14)
        plt.ylabel('Average Result Margin', fontsize=14)
        plt.legend(title='Result Type')

        # Showing the values on markers
        for index, row in avg_result.iterrows():
            plt.annotate(f'{row["runs"]:.1f}', 
                        (row['season'], row['runs']), 
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center', fontsize=10, color='blue')
            
            plt.annotate(f'{row["wickets"]:.1f}', 
                        (row['season'], row['wickets']), 
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center', fontsize=10, color='orange')

        plt.grid()
        plt.xticks(rotation=45)  
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        plots['plot8_base64'] = b64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close()


        # avg target run by season 
        avg_run_byseason = pd.pivot_table(data=df_match, index='season', values='target_runs', aggfunc='mean')
        avg_run_byseason.reset_index(inplace=True)

        # Creating line plot
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=avg_run_byseason, x='season', y='target_runs', marker='o', color='blue')

        # Adding titles and labels
        plt.title('Trend of Average Target Runs by Season', fontsize=16)
        plt.xlabel('Season', fontsize=12)
        plt.ylabel('Average Target Runs', fontsize=12)
        plt.xticks(rotation=45) 
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        plots['plot4_base64'] = b64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close()

        

        return plots



    context = create_plot_safely(generate_plots)
    return render(request, "performance_stats.html", context)



def dashboard(request):
    
    # Generate only the charts needed for match statistics
    season_counts = df_match['season'].value_counts().sort_index()

    # Ploting the trend as a line chart
    plt.figure(figsize=(10, 6))  
    plt.plot(season_counts.index, season_counts.values, marker='o', linestyle='-', color='blue')

    # Adding titles and labels
    plt.title('Trend of Total Matches Over Seasons', fontsize=16)
    plt.xlabel('Season', fontsize=12)
    plt.ylabel('Number of Matches', fontsize=12)

    # Annotating each data point with the value
    for i, value in enumerate(season_counts.values):
        plt.text(season_counts.index[i], value, str(value), fontsize=10, ha='center', va='bottom')
    plt.xticks(rotation=45)  
    plt.grid(True)           
    
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    plot1_base64 = b64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    plt.close()

    # Replace NaN values in 'city' column with 'Unknown' and count the occurrences
    city_counts = df_match['city'].replace(np.NaN, 'Unknown').value_counts()

    # Creating a bar plot
    plt.figure(figsize=(12, 6))  # Set the figure size
    sns.barplot(x=city_counts.index, y=city_counts.values, palette='viridis')

    # Add titles and labels
    plt.title('Number of Matches Hosted by Each City', fontsize=16)
    plt.xlabel('City', fontsize=12)
    plt.ylabel('Number of Matches', fontsize=12)
    plt.xticks(rotation=90)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    plot2_base64 = b64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    plt.close()


    # Calculating the mean of 'target_runs'
    mean_target_runs = df_match['target_runs'].mean()

    # Creating histogram plot to show the distribution 
    plt.figure(figsize=(10, 6))  # Set the figure size
    sns.histplot(df_match['target_runs'].dropna(), bins=30, kde=True, color='blue') 

    # Adding a vertical line for the mean
    plt.axvline(mean_target_runs, color='red', linestyle='--', label=f'Mean: {mean_target_runs:.2f}')

    # Adding titles and labels
    plt.title('Distribution of Target Runs', fontsize=16)
    plt.xlabel('Target Runs', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.legend()
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    plot3_base64 = b64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    plt.close()

    
    # Distribution of Match Results
    result_distribution = df_match['result'].value_counts()

    # Creating the bar plot
    plt.figure(figsize=(10, 6))
    sns.barplot(x=result_distribution.index, y=result_distribution.values, palette='viridis')

    # Adding titles and labels
    plt.title('Distribution of Match Results', fontsize=16)
    plt.xlabel('Result', fontsize=12)
    plt.ylabel('Number of Matches', fontsize=12)

    # Showing the values on top of the bars
    for index, value in enumerate(result_distribution):
        plt.text(index, value, f'{value}', ha='center', va='bottom')
    plt.xticks(rotation=45)  
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    plot5_base64 = b64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    plt.close()

    

   

    
    

    


    context = {
        "plot_base64": plot1_base64,
        "plot2_base64": plot2_base64,
        "plot3_base64": plot3_base64,
        "plot5_base64": plot5_base64,
    }

    return render(request, "dashboard.html", context)



    