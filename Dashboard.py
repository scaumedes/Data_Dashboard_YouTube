#importing libraries
import pandas as pd 
import numpy as np 
import streamlit as st
from datetime import datetime

#functions for red/green delta styling in dataframe
def style_negative(v, props=''):
    try: 
        return props if v < 0 else None
    except:
        pass
    
def style_positive(v, props=''):
    try: 
        return props if v > 0 else None
    except:
        pass    

st.set_page_config(layout="wide")

#loading data
@st.cache_data
def load_data():
    #skipping the first row
    df_agg = pd.read_csv('Aggregated_Metrics_By_Video.csv').iloc[1:,:]
    df_agg.columns = ['Video','Video title','Video publish time','Comments added','Shares','Dislikes','Likes',
                      'Subscribers lost','Subscribers gained','RPM(USD)','CPM(USD)','Average % viewed','Average view duration',
                      'Views','Watch time (hours)','Subscribers','Your estimated revenue (USD)','Impressions','Impressions ctr(%)']
    df_agg['Video publish time'] = pd.to_datetime(df_agg['Video publish time'])
    df_agg['Average view duration'] = df_agg['Average view duration'].apply(lambda x: datetime.strptime(x,'%H:%M:%S'))
    df_agg['Avg watch length (sec)'] = df_agg['Average view duration'].apply(lambda x: x.second + x.minute*60 + x.hour*3600)
    df_agg['Engagement ratio'] =  (df_agg['Comments added'] + df_agg['Shares'] +df_agg['Dislikes'] + df_agg['Likes']) /df_agg.Views
    df_agg['Views / sub gained'] = df_agg['Views'] / df_agg['Subscribers gained']
    df_agg.sort_values('Video publish time', ascending = False, inplace = True)    
    df_agg_sub = pd.read_csv('Aggregated_Metrics_By_Country_And_Subscriber_Status.csv')
    df_comments = pd.read_csv('Aggregated_Metrics_By_Video.csv')
    df_time = pd.read_csv('Video_Performance_Over_Time.csv')
    df_time['Date'] = pd.to_datetime(df_time['Date'])
    return df_agg, df_agg_sub, df_comments, df_time 

df_agg, df_agg_sub, df_comments, df_time = load_data()

#calculating median for the columns for the videos not older then a year
df_agg_diff = df_agg.copy()
metric_date_12mo = df_agg_diff['Video publish time'].max() - pd.DateOffset(months =12)
median_agg = df_agg_diff[df_agg_diff['Video publish time'] >= metric_date_12mo].median()

#calculating differences from the median for values for numeric columns
numeric_cols = np.array((df_agg_diff.dtypes == 'float64') | (df_agg_diff.dtypes == 'int64'))
df_agg_diff.iloc[:,numeric_cols] = (df_agg_diff.iloc[:,numeric_cols] - median_agg).div(median_agg)

#building dashboard
st.title('Dashboard')
st.write("Data analysis of Ken Jee's chaneel")
    
df_agg_metrics = df_agg[['Video publish time','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed',
                             'Avg watch length (sec)', 'Engagement ratio','Views / sub gained']]
metric_date_6mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months =6)
metric_date_12mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months =12)
metric_medians6mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_6mo].median()
metric_medians12mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_12mo].median()
    
col1, col2, col3, col4, col5 = st.columns(5)
columns = [col1, col2, col3, col4, col5]
    
count = 0
for i in metric_medians6mo.index:
    with columns[count]:
        delta = (metric_medians6mo[i] - metric_medians12mo[i])/metric_medians12mo[i]
        st.metric(label= i, value = round(metric_medians6mo[i],2), delta = "{:.2%}".format(delta))
        count += 1
        if count >= 5:
            count = 0

#building dataframe
#get date information / trim to relevant data 
df_agg_diff['Publish_date'] = df_agg_diff['Video publish time'].apply(lambda x: x.date())
df_agg_diff_final = df_agg_diff.loc[:,['Video title','Publish_date','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed', 'Avg watch length (sec)', 'Engagement ratio','Views / sub gained']]
    
df_agg_numeric_lst = df_agg_diff_final.median().index.tolist()
df_to_pct = {}
for i in df_agg_numeric_lst:
    df_to_pct[i] = '{:.1%}'.format
    
st.dataframe(df_agg_diff_final.style.hide().applymap(style_negative, props='color:red;').applymap(style_positive, props='color:green;').format(df_to_pct))