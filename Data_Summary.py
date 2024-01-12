import pandas as pd 
from datetime import datetime 
import plotly.express as px
import plotly.graph_objs as go
import plotly.subplots as sp
import warnings
warnings.filterwarnings("ignore")
import streamlit as st 
pd.options.display.float_format = '{:,.2f}'.format


custom_css = """
<style>
body {
    background-color: #043c7c;
    color: white;
}

h1, h2 {
    text-align: center;
    color: #2B3990;
}

h3 {
 
    color: #2B3990;
}

h4 {
    text-align: center;
    color: #2B3990;
}
    

/* Add more custom styles as needed */
</style>
"""
st.set_page_config(layout="wide", page_title="Hello", page_icon="👋")
st.markdown(custom_css, unsafe_allow_html=True)


# def load_data():
#     master_trans = pd.read_csv(r"\\tatooine\alteryx\users\Chi\Alteryx\SAKARALIFE\MasterTrans_py.csv", encoding='latin-1')
#     master_cust = pd.read_csv(r"\\tatooine\alteryx\users\Chi\Alteryx\SAKARALIFE\MasterCust_py.csv", encoding='latin-1')
#     missing_loc = pd.read_csv(r"\\tatooine\alteryx\users\Chi\Alteryx\SAKARALIFE\missing_locations_test.csv", encoding='latin-1')
#     return master_trans, master_cust, missing_loc

# Call the load_data function and assign its values to variables
# master_trans, master_cust, missing_loc = load_data()
st.sidebar.title("File Uploads")
uploaded_trans = st.sidebar.file_uploader(
    "Upload Mastertrans CSV", type=["csv"], key="transactions"
)
uploaded_cust = st.sidebar.file_uploader("Upload Mastercust CSV", type=["csv"], key="customers")

uploaded_loc = st.sidebar.file_uploader(
    "Upload MissingLoc CSV", type=["csv"], key="locations"
)

if uploaded_trans is not None:
    master_trans = pd.read_csv(uploaded_trans, encoding='latin-1')

    if uploaded_cust is not None:
        master_cust = pd.read_csv(uploaded_cust, encoding='latin-1')

        if uploaded_loc is not None:
            missing_loc = pd.read_csv(uploaded_loc)
            master_trans["wrt_dat"] = pd.to_datetime(master_trans["wrt_dat"])
            master_trans = master_trans[master_trans['wrt_dat'] >= '2019-01-01']
            
         # Filter transactions based on date range
            st.sidebar.title("Time Filter")
            start_date = st.sidebar.date_input("Start Date", min(master_trans["wrt_dat"]))
            end_date = st.sidebar.date_input("End Date", max(master_trans["wrt_dat"]))
            master_trans =  master_trans[
                (master_trans["wrt_dat"] >= pd.to_datetime(start_date))
                & (master_trans["wrt_dat"] <= pd.to_datetime(end_date))
            ]

            # Title
            st.markdown("<h1>LS Direct</h1>", unsafe_allow_html=True)
            st.markdown(f"<h2>Data Ingestion: {', '.join(master_trans.db_db.unique())}</h2>", unsafe_allow_html=True)
            image_url = "https://media.licdn.com/dms/image/D4E3DAQHWVajZ1sc61g/image-scale_191_1128/0/1695153109897/ls_direct_marketing_cover?e=2147483647&v=beta&t=0XFHIGXQzXC0yHyak2ornc1V-JLGsHoPY2RSjSps89s"
            
########### Insert tabs #############
            
            st.markdown("""
    <style>
        .stTabs [data-baseweb="tab-list"] {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            width: 300px; 
 
            white-space: pre-wrap;
            background-color: #2B3990;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            font-size: 30px; 
            font-weight: bold; 
            color: #FFFFFF !important; 
        }

        .stTabs [aria-selected="true"] {
            background-color: ;
        }
    </style>
""", unsafe_allow_html=True)

            
            tab1, tab2, tab3 = st.tabs(["Data Overview", "Sales Overview", "Customer Overview"])

            
            with tab1:

                st.image(image_url, use_column_width=True)
                st.markdown(f"<h4>The latest transaction date is: {master_trans['wrt_dat'].max().strftime('%Y-%m-%d')}</h4>", unsafe_allow_html=True)

                def format_number(x):
                    if isinstance(x, (int, float)):
                        return f"{x:,.0f}"
                    return x 

                #### Data for Cards ####

                cal_ticket = master_trans[['db_customerID', 'wrt_dat', "wrt_sale"]]
                ticket_sales = cal_ticket.groupby(['wrt_dat', 'db_customerID'
                                                   ])['wrt_sale'].sum().reset_index()
                ticket_sales = ticket_sales[ticket_sales.wrt_sale != 0]

                # Checking if db_customerIDs in master_trans are also available in master_cust
                master_trans.db_customerID = master_trans.db_customerID.astype(str)
                master_cust.db_customerID = master_cust.db_customerID.astype(str)
                trans_no_cusid = master_trans[~master_trans.db_customerID.
                                              isin(master_cust.db_customerID.to_list())]

                trans_no_cusid['db_customerID'] = trans_no_cusid['db_customerID'].astype(str).str.rstrip('.0')
                trans_no_cusid2 = trans_no_cusid[~trans_no_cusid.db_customerID.
                                              isin(master_cust.db_customerID.to_list())]
                st.session_state.trans_no_cusid = trans_no_cusid
                st.session_state.trans_no_cusid2 = trans_no_cusid2
                data = {
                    'Checking': [
                        'Number of unmatched stores', 'Number of unmatched transactions',
                        'Median Ticket', 'Average Ticket', 'Maximum Ticket'
                    ],
                    'Values': [
                        len(missing_loc),
                        #len(join_loc_miss),
                        len(trans_no_cusid2),
                        round(ticket_sales['wrt_sale'].median(), 3),
                        round(ticket_sales['wrt_sale'].mean(), 3),
                        ticket_sales['wrt_sale'].max()
                    ]
                }

                df = pd.DataFrame(data)
                #df['Values'] = df['Values'].apply(format_number)

                # Missing transactions
                master_trans1 = master_trans.copy()
                master_trans1['wrt_dat'] = pd.to_datetime(master_trans1['wrt_dat'], format="%Y-%m-%d")
                master_trans1['wrt_year'] = master_trans1['wrt_dat'].dt.year
                master_trans1['wrt_month'] = master_trans1['wrt_dat'].dt.month  # Full month name
                master_trans1['day_of_week'] = master_trans1['wrt_dat'].dt.strftime("%A")
                master_trans1['DoW'] = master_trans1['wrt_dat'].dt.weekday


                daily_sale = master_trans1.groupby('wrt_dat').agg({'wrt_sale':'sum'}).reset_index()
                avg_sales_daily = daily_sale['wrt_sale'].mean()


                daily_counts = master_trans1.groupby([master_trans1['wrt_dat'].dt.date, master_trans1['day_of_week']])['wrt_so_no'].count().reset_index()
                daily_counts.columns = ['Date', 'Day_of_Week', 'Transaction_Count']

                # Assuming daily_counts['Date'].max() is a datetime object
                max_date = daily_counts['Date'].max()

                # Subtract one year from the maximum date
                start_date1 = max_date - relativedelta(years=1)
                end_date1 = max_date 
                date_range = pd.date_range(start=start_date1, end=end_date1, freq='D')

                # Find missing dates (dates without transactions)
                missing_dates = date_range[~date_range.isin(daily_counts['Date'])]
                formatted_missing_dates = [date.strftime('%Y-%m-%d') for date in missing_dates]
                missing_dates_df = pd.DataFrame({'Missing Dates': formatted_missing_dates})
                missing_dates_df['Day of Week'] = missing_dates_df['Missing Dates'].apply(lambda x: pd.to_datetime(x).day_name())
                missing_dates_df = missing_dates_df.sort_values(by='Missing Dates', ascending=False)

                #### Cards at beginning ####
                total_unmatched_store = int(df.iloc[0, 1])  
                total_unmatched_trans = int(df.iloc[1, 1])  
                v_status = master_cust[master_cust.CASS_StatusCode == 'V']
                v_status_valid = round(len(v_status) / len(master_cust) * 100, 2)
                missing_dates = int(len(missing_dates_df)) 

                average_ticket = df.iloc[3, 1]
                maximum_ticket = df.iloc[4, 1]

                PLOT_BGCOLOR = "#bee0ec"
                st.markdown(f"""
                <style>
                .stPlotlyChart {{
                    outline: 3px solid {PLOT_BGCOLOR};
                    border-radius: 6px; 
                    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.20), 0 6px 20px 0 rgba(0, 0, 0, 0.30);
                }}
                </style>
                """, unsafe_allow_html=True)


                unmatched_store_fig = go.Figure(go.Indicator(
                    mode="number",
                    title={"text": "<b>Total Unmatched StoreIDs</b>","font": {"color": '#2B3990'}},
                    value=total_unmatched_store,
                    number={
                        "font": {"color": "red" if len(missing_loc) > 0 else "green"}
                    },
                ))
                unmatched_store_fig.update_layout(
                    paper_bgcolor=PLOT_BGCOLOR,
                    #plot_bgcolor="skyblue",
                    margin=dict(pad=0, r=30, t=40, b=40, l=30),
                    width=90, 
                    height=185
                    )


                unmatched_trans_fig = go.Figure(go.Indicator(
                    mode="number",
                    title={"text": "<b>Total Unmatched Transactions</b>","font": {"color": '#2B3990'}},
                    value=total_unmatched_trans,
                    number={
                        "font": {"color": "red" if float(missing_dates) > 0 else "green"}
                    },
                ))

                unmatched_trans_fig.update_layout(
                    paper_bgcolor=PLOT_BGCOLOR,
                    #plot_bgcolor="skyblue",
                    margin=dict(pad=0, r=30, t=40, b=40, l=30),
                    width=90, 
                    height=185
                    )


                status_fig = go.Figure(go.Indicator(
                    mode="number",
                    title={"text": "<b>Valid CASS Addresses</b>", "font": {"color": '#2B3990'}},
                    value=float(v_status_valid),
                    number={
                        "suffix": "%",
                        "font": {"color": "green" if float(v_status_valid) > 85 else "red"}
                    },
                ))
                status_fig.update_layout(
                    paper_bgcolor=PLOT_BGCOLOR,
                    #plot_bgcolor="skyblue",
                    margin=dict(pad=0, r=30, t=40, b=40, l=30),
                    width=90, 
                    height=185
                    )

                missing_date_fig = go.Figure(go.Indicator(
                    mode="number",
                    title={"text": "<b>Total Missing Dates (1 year)</b>","font": {"color": '#2B3990'}},
                    value=missing_dates, 
                    number={
                        "font": {"color": "red" if float(missing_dates) > 0 else "green"}
                    },
                ))
                missing_date_fig.update_layout(
                    paper_bgcolor=PLOT_BGCOLOR,
                    #plot_bgcolor="skyblue",
                    margin=dict(pad=0, r=30, t=40, b=40, l=30),
                    width=90, 
                    height=185
                    )

                # Create containers
                # Streamlit layout for displaying KPI cards side by side

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.plotly_chart(unmatched_store_fig, use_container_width=True, key="container1", **{"style": f"background-color: {PLOT_BGCOLOR}; height: 50px;"})

                with col2:
                    st.plotly_chart(unmatched_trans_fig, use_container_width=True, key="container2", **{"style": f"background-color: {PLOT_BGCOLOR}; height: 50px;"})

                with col3:
                    st.plotly_chart(status_fig, use_container_width=True, key="container3", **{"style": f"background-color: {PLOT_BGCOLOR}; height: 50px;"})

                with col4:
                    st.plotly_chart(missing_date_fig, use_container_width=True, key="container4", **{"style": f"background-color: {PLOT_BGCOLOR}; height: 50px;"})


    ################TABLE 1+2 ###############
                ### Data Overall

                def missing_summary(df):
                    missing_values = df.isnull().sum().apply(lambda x: f'{x:,}')
                    percentages_missing = round(df.isnull().sum() / len(df) * 100, 2)

                    unique_percentages = round(df.nunique() / len(df) * 100, 2)

                    summary = pd.DataFrame({
                        'Missing Values': missing_values,
                        'Percentage of Missing Data': percentages_missing,
                        'Percentage of Unique Data': unique_percentages
                    })

                    def highlight_red_missing(val):
                        color = 'red' if val > 80 else ''
                        return f'color: {color}; text-align: right'

                    def highlight_red_unique(val):
                        color = 'red' if val < 60 else ''
                        return f'color: {color}; text-align: right'

                    styled_summary = summary.style.applymap(
                        highlight_red_missing,
                        subset=['Percentage of Missing Data']
                    ).applymap(
                        highlight_red_unique,
                        subset=['Percentage of Unique Data']
                    ).format({
                        'Percentage of Missing Data': '{:.2f}%',
                        'Percentage of Unique Data': '{:.2f}%'
                    })

                    return styled_summary

                datasets = [master_trans, master_cust]

                col1, col2 = st.columns(2)
                # Create containers with adjusted height and style using st.markdown
                with col1.container():
                    st.markdown(
                        f"""
                        <div style="background-color: #2B3990; padding: 5px;border-radius: 6px;">
                            <h4 style="color: white; font-weight: bold; text-align: center;">Summary for Master Trans Dataset</h4>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    col1.dataframe(missing_summary(master_trans), height=400, width=1500)  # Adjust height and width as needed
                    #st.markdown("<hr style='border: 2px solid #001F3F;'>", unsafe_allow_html=True)

                with col2.container():
                    st.markdown(
                        f"""
                        <div style="background-color: #2B3990; padding: 5px; border-radius: 6px;">
                            <h4 style="color: white; font-weight: bold; text-align: center;">Summary for Master Cust Dataset</h4>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    col2.dataframe(missing_summary(master_cust), height=400, width=1500)                  
                st.markdown("<hr style='border: 2px solid #001F3F;'>", unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1: 
                    if float(missing_dates) > 0:
                        st.markdown(
                            f"<font color='red'> Warning: Number of missing dates: {len(formatted_missing_dates)} from {start_date1} (Minimum wrt_date) to {end_date1} (Maximum wrt_date) </font>",
                            unsafe_allow_html=True
                        )
                        table = go.Figure(data=[go.Table(
                        header=dict(values=['<b>Missing Dates<b>', '<b>Day of Week<b>'], fill=dict(color='#2B3990'), font=dict(color='white', size=14)),
                        cells=dict(values=[missing_dates_df['Missing Dates'], missing_dates_df['Day of Week']], fill=dict(color='white'), font=dict(color='black', size=12))
                    )])

                        table.update_layout(
                            title='<b>Missing Transaction Dates<b>',
                            title_font=dict(size=16, color='#2B3990', family='Arial'),
                            width=1500,
                            height=400,
                            margin=dict(t=50, b=10, l=10, r=10),

                        )

                        table.update_layout(width=1500)  # Adjust the width of the chart
                        st.plotly_chart(table, use_container_width=True)

                    else:
                        st.markdown("<font color='green'>There are no missing dates. No data to show here. </font>",unsafe_allow_html=True)
                
                with col2: 
                    missing_loc['Total_Sales'] = missing_loc['Total_Sales'].apply(format_number)
                    if len(missing_loc) > 0:
                        st.markdown(
                            f"<font color='red'> Warning: The following information pertains to unmatched storeIDs. </font>",
                            unsafe_allow_html=True
                        )
                        table = go.Figure(data=[go.Table(
                        header=dict(values=['<b>Unmatched StoreID<b>', '<b>Unmatched Total Sales<b>'], fill=dict(color='#2B3990'), font=dict(color='white', size=14)),
                        cells=dict(values=[missing_loc['UnmatchedStoreID_fromLoc'], missing_loc['Total_Sales']], fill=dict(color='white'), font=dict(color='black', size=12))
                    )])

                        table.update_layout(
                            title='<b>Unmatched StoreIDs<b>',
                            title_font=dict(size=16, color='#2B3990', family='Arial'),
                            width=1500,
                            height=400,
                            margin=dict(t=50, b=10, l=10, r=10),

                        )

                        table.update_layout(width=1500)  # Adjust the width of the chart
                        st.plotly_chart(table, use_container_width=True)

                    else:
                        st.markdown("<font color='green'>There are no unmatched stores. No data to show here. </font>",unsafe_allow_html=True)
     


            ##############################################################################################################################################################
            with tab2: 
                image_url = "https://media.licdn.com/dms/image/D4E3DAQHWVajZ1sc61g/image-scale_191_1128/0/1695153109897/ls_direct_marketing_cover?e=2147483647&v=beta&t=0XFHIGXQzXC0yHyak2ornc1V-JLGsHoPY2RSjSps89s"
                st.image(image_url, use_column_width=True)

                st.markdown(f"<h3 style='text-align: center;'>📈--Sales Overview--📈</h3>", unsafe_allow_html=True)
    ############ 3 cards #################
                PLOT_BGCOLOR = "#bee0ec"
                st.markdown(f"""
                <style>
                .stPlotlyChart {{
                    outline: 3px solid {PLOT_BGCOLOR};
                    border-radius: 6px; 
                    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.20), 0 6px 20px 0 rgba(0, 0, 0, 0.30);
                }}
                </style>
                """, unsafe_allow_html=True)

                median_sale = round(ticket_sales['wrt_sale'].median(), 3)
                mean_sale = round(ticket_sales['wrt_sale'].mean(), 3)
                max_sale = ticket_sales['wrt_sale'].max()            
                maximum_sale_fig = go.Figure(go.Indicator(
                    mode="number",
                    title={"text": "<b>Maximum Ticket</b>","font": {"color": '#2B3990'}},
                    value=max_sale,
                ))

                maximum_sale_fig.update_layout(
                    paper_bgcolor=PLOT_BGCOLOR,
                    #plot_bgcolor="skyblue",
                    margin=dict(pad=0, r=30, t=40, b=40, l=30),
                    width=120, 
                    height=185,
                    #number_font=dict(color='grey')
                    )


                mean_sale_fig = go.Figure(go.Indicator(
                    mode="number",
                    title={"text": "<b>Average Ticket</b>","font": {"color": '#2B3990'}},
                    value=mean_sale,
                ))

                mean_sale_fig.update_layout(
                    paper_bgcolor=PLOT_BGCOLOR,
                    #plot_bgcolor="skyblue",
                    margin=dict(pad=0, r=30, t=40, b=40, l=30),
                    width=120, 
                    height=185,
                   # number_font=dict(color='grey')
                    )


                median_sale_fig = go.Figure(go.Indicator(
                    mode="number",
                    title={"text": "<b>Median Ticket</b>", "font": {"color": '#2B3990'}},
                    value=float(median_sale),

                ))
                median_sale_fig.update_layout(
                    paper_bgcolor=PLOT_BGCOLOR,
                    #plot_bgcolor="skyblue",
                    margin=dict(pad=0, r=30, t=40, b=40, l=30),
                    width=120, 
                    height=185, 
                   # number_font=dict(color='grey')
                    )


                col1, col2, col3 = st.columns(3)

                with col1:
                    st.plotly_chart( maximum_sale_fig, use_container_width=True, key="container1", **{"style": f"background-color: {PLOT_BGCOLOR}; height: 50px;"})

                with col2:
                    st.plotly_chart(mean_sale_fig, use_container_width=True, key="container2", **{"style": f"background-color: {PLOT_BGCOLOR}; height: 50px;"})

                with col3:
                    st.plotly_chart(median_sale_fig, use_container_width=True, key="container3", **{"style": f"background-color: {PLOT_BGCOLOR}; height: 50px;"})

        ###################### Daily avg ticket chart ############3
                ticket_sales_test = ticket_sales.groupby(['wrt_dat','db_customerID'])['wrt_sale'].sum().reset_index()
                #ticket_sales_test =  ticket_sales_test[ticket_sales_test['wrt_dat'] >= '2021-01-01']
                test_sales_month = ticket_sales_test.groupby(['wrt_dat'])['wrt_sale'].mean().reset_index()


                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=test_sales_month['wrt_dat'],
                    y=test_sales_month['wrt_sale'],
                    fill='tozeroy',  # Fill area below the line
                    mode='lines+markers',
                    line=dict(color= '#2B3990'),
                    name='Sales'
                ))

                fig.update_layout(
                    xaxis_title='<b>Date</b>',
                    yaxis_title='<b>Avg Ticket</b>',
                    title='<b>Daily Avg Ticket</b>',
                    template='plotly_dark',
                    title_font=dict(color='#2B3990', size = 14),
                    width=1500,
                   # height=450,
                    xaxis=dict(range=[test_sales_month['wrt_dat'].min(), test_sales_month['wrt_dat'].max()])
                )

                fig.update_layout(width=1500)  # Adjust the width of the chart
                st.plotly_chart(fig, use_container_width=True)

    ########## Daily Sales #################### 
                daily_sale = master_trans1.groupby('wrt_dat').agg({'wrt_sale':'sum'}).reset_index()
                avg_sales_daily = daily_sale['wrt_sale'].mean()

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=daily_sale['wrt_dat'],
                    y=daily_sale['wrt_sale'],
                    fill='tozeroy',
                    mode='lines+markers',
                    line=dict(color='#043c7c'),
                    name='Sales'
                ))

                fig.add_hline(y=avg_sales_daily, line_dash='dash', line_color='white', name='Average')

                fig.add_annotation(
                    x=daily_sale['wrt_dat'].max(),
                    y=avg_sales_daily,
                    text=f'Avg: {avg_sales_daily:,.2f}',
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor='white',
                    font=dict(size=12, color='white'),
                    align='center'
                )

                fig.update_layout(
                    xaxis_title='<b>Date</b>',
                    yaxis_title='<b>Sales</b>',
                    title='<b>Daily Sales</b>',
                    title_font=dict(color='#2B3990', size = 14),
                    template='plotly_dark',
                    width=1500,
                    height=450,
                    xaxis=dict(range=[daily_sale['wrt_dat'].min(), daily_sale['wrt_dat'].max()])
                )

                st.plotly_chart(fig, use_container_width=True)

    #######################Monthly SAles + Avg Ticket#################################
                col1, col2 = st.columns(2)

                # Column 1: Monthly Avg Ticket
                with col1:
                    ticket_sales['wrt_dat'] = pd.to_datetime(ticket_sales['wrt_dat'], format="%Y-%m-%d")
                    ticket_sales['wrt_year'] = ticket_sales['wrt_dat'].dt.year
                    ticket_sales['wrt_month'] = ticket_sales['wrt_dat'].dt.month 

                    ticket_sales_month = ticket_sales.groupby(['wrt_year','wrt_month','db_customerID'])['wrt_sale'].sum().reset_index()
                    ticket_sales_month = ticket_sales_month.groupby(['wrt_year','wrt_month'])['wrt_sale'].mean().reset_index()

                    fig = px.line(ticket_sales_month,
                                  x='wrt_month',
                                  y='wrt_sale',
                                  color='wrt_year',
                                  title='<b> Monthly Average Ticket<b>',
                                  labels={
                                      'wrt_month': 'Month',
                                      'wrt_sale': 'Average Ticket',
                                      'wrt_year': 'Year'
                                  },
                                  template='plotly_dark',
                                )
                    line_colors = [
                         'grey', '#27AAE1', '#2B3990', '#000BE5','Violet','lightpink', 'yellow', 'mediumblue' 
                    ]
                    for idx, year in enumerate(fig.data):
                        fig.data[idx].line.color = line_colors[idx % len(line_colors)]

                    fig.update_traces(
                        mode='lines+markers',
                        marker=dict(size=7),
                    )

                    fig.update_layout(
                        width=1500, 
                        title_font=dict(color='#2B3990', size = 14),
                        #height=450,  
                    )
                    fig.update_xaxes(title_text='<b>Month<b>')
                    fig.update_yaxes(title_text='<b>Average Ticket<b>', rangemode="tozero")
                    fig.update_layout(width=1500)  # Adjust the width of the chart
                    st.plotly_chart(fig, use_container_width=True)



    ################# Column 2: Sales over Years###############
                with col2:
                    master_trans_dup_remove = master_trans1.copy()
                    sales_year = master_trans_dup_remove.groupby('wrt_year').agg({'wrt_sale':'sum'}).reset_index()
                    #sales_year = sales_year[sales_year.wrt_year >= 2017]
                    median_value = sales_year['wrt_sale'].median()

                    fig1 = go.Figure()

                    # Add the sales data
                    fig1.add_trace(go.Scatter(
                        x=sales_year['wrt_year'],
                        y=sales_year['wrt_sale'],
                        fill='tozeroy',
                        mode='lines+markers',
                        marker=dict(symbol='circle', size=8, color='#043c7c', line=dict(width=2, color='white')),
                        line=dict(color='#043c7c'),
                        name='Sales'
                    ))

                    # Add the white median line
                    fig1.add_shape(
                        type='line',
                        x0=sales_year['wrt_year'].min(),
                        x1=sales_year['wrt_year'].max(),
                        y0=median_value,
                        y1=median_value,
                        line=dict(color='red', width=2, dash='dash'),
                        name='Median'
                    )

                    fig1.add_annotation(
                        x=sales_year['wrt_year'].min(),
                        y=median_value,
                        text=f'Median: {median_value:,.2f}', 
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor='red',
                        bgcolor='red',
                        font=dict(size=12, color='white'),
                        align='center'
                    )

                    fig1.update_layout(
                        xaxis_title='<b>Year</b>',
                        yaxis_title='<b>Sales</b>',
                        title='<b>Sales over Years</b>',
                        title_font=dict(color='#2B3990', size = 14),
                        template='plotly_dark',
                    )

                    fig1.update_layout(xaxis={'dtick': 1})
                    fig1.update_layout(width=1500)  # Adjust the width of the chart
                    st.plotly_chart(fig1, use_container_width=True)


                col1, col2 = st.columns(2)

    ################# Column 1: Weekday Sales#############
                with col1: 
                    st.session_state.master_trans_dup_remove = master_trans_dup_remove
                    sale_month = master_trans_dup_remove.groupby(['wrt_year', 'wrt_month']).agg({'wrt_sale':'sum'}).reset_index()
                    #sale_month = sale_month[sale_month.wrt_year >= 2017]
                    min_value3 = sale_month['wrt_sale'].min()
                    min_index3 = sale_month['wrt_sale'].idxmin()
                    max_value3 = sale_month['wrt_sale'].max()
                    max_index3 = sale_month['wrt_sale'].idxmax()
                    line_colors = [
                         'grey', '#27AAE1', '#2B3990', '#000BE5','Violet','lightpink', 'yellow', 'mediumblue' 
                    ]

                    fig2 = px.line(
                        sale_month,
                        x='wrt_month',
                        y='wrt_sale',
                        color='wrt_year',
                        title='<b>Comparison of Sales by Month and Year<b>',
                        labels={
                            'wrt_month': 'Month',
                            'wrt_sale': 'sales',
                            'wrt_year': 'Year'
                        },
                        template='plotly_dark',

                    )

                    # Annotate the minimum + maximum point
                    fig2.add_annotation(x=sale_month.loc[min_index3, 'wrt_month'],
                                       y=min_value3,
                                       text=f'Min: {min_value3:,.2f}',
                                       showarrow=True,
                                       arrowhead=1,
                                       arrowcolor='red',
                                       font=dict(color='white', size=12),
                                       bgcolor='red',
                                       opacity=0.7,
                                       xshift=10,
                                       yshift=10)

                    # Annotate the max point
                    fig2.add_annotation(x=sale_month.loc[max_index3, 'wrt_month'],
                                       y=max_value3,
                                       text=f'Max: {max_value3:,.2f}',
                                       showarrow=True,
                                       arrowhead=1,
                                       arrowcolor='red',
                                       font=dict(color='white', size=12),
                                       bgcolor='red',
                                       opacity=0.7,
                                       xshift=10,
                                       yshift=10)

                    for idx, year in enumerate(fig2.data):
                        fig2.data[idx].line.color = line_colors[idx % len(line_colors)]

                    fig2.update_traces(
                        mode='lines+markers',
                        marker=dict(size=7),
                    )

                    fig2.update_layout(
                        width=1000,  
                        height=450,  
                        yaxis=dict(range=[0, max(sale_month['wrt_sale'])]),
                        title_font=dict(color='#2B3990', size = 14),

                    )

                    fig2.update_xaxes(title_text='<b>Month<b>')
                    fig2.update_yaxes(title_text='<b>Sales<b>')

                    fig2.update_layout(width=1500)  # Adjust the width of the chart
                    st.plotly_chart(fig2, use_container_width=True)

    ############# Column 2: Monthly Sales#############
                with col2:
                    dow_sale = master_trans_dup_remove.groupby(['wrt_year', 'DoW','day_of_week']).agg({
                        'wrt_sale':
                        'sum'
                    }).reset_index()
                    #dow_sale= dow_sale[dow_sale.wrt_year >= 2017]

                    min_value2 = dow_sale['wrt_sale'].min()
                    min_index2 = dow_sale['wrt_sale'].idxmin()
                    max_value2 = dow_sale['wrt_sale'].max()
                    max_index2 = dow_sale['wrt_sale'].idxmax()

                    line_colors = [
                    'grey', '#27AAE1', '#2B3990', '#000BE5', 'Violet', 'lightpink', 'yellow', 'mediumblue'
                    ]

                    fig3 = px.line(
                    dow_sale,
                    x='DoW',
                    y='wrt_sale',
                    color='wrt_year',
                    title='<b>Comparison of Sales by Day of the Week and Year<b>',
                    labels={
                        'DoW': 'Day',
                        'wrt_sale': 'Sales',
                        'wrt_year': 'Year'
                    },
                    template='plotly_dark',
                    color_discrete_sequence=line_colors  # Set line colors
                    )

                    # Customize x-axis tick labels to display day names
                    fig3.update_xaxes(
                    title_text='<b>Day of Week<b>',
                    tickvals=list(range(7)),  # Tick values from 0 to 6
                    ticktext=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],  # Day names
                    )

                    fig3.add_annotation(x=dow_sale.loc[min_index2, 'DoW'],
                                   y=min_value2,
                                   text=f'Min: {min_value2:,.2f}',
                                   showarrow=True,
                                   arrowhead=1,
                                   arrowcolor='red',
                                   font=dict(color='white', size=12),
                                   bgcolor='red',
                                   opacity=0.7,
                                   xshift=10,
                                   yshift=10)

                    # Annotate the minimum point
                    fig3.add_annotation(x=dow_sale.loc[max_index2, 'DoW'],
                                   y=max_value2,
                                   text=f'Max: {max_value2:,.2f}',
                                   showarrow=True,
                                   arrowhead=1,
                                   arrowcolor='red',
                                   font=dict(color='white', size=12),
                                   bgcolor='red',
                                   opacity=0.7,
                                   xshift=10,
                                   yshift=10)

                    fig3.update_traces(
                    mode='lines+markers',
                    marker=dict(size=8),
                    )

                    fig3.update_layout(
                    width=1000,
                    height=450,
                    yaxis=dict(range=[0, max(dow_sale['wrt_sale'])]), 
                    title_font=dict(color='#2B3990', size = 14),

                    )

                    fig3.update_yaxes(title_text='<b>Sales<b>')

                    fig3.update_layout(width=1500)  # Adjust the width of the chart
                    st.plotly_chart(fig3, use_container_width=True)

                ############## 
                if len(trans_no_cusid) == 0:
                    st.markdown("<font color='green'> All customerID in Master_trans table match Master_cust.customerID. No data to show here. </font>",unsafe_allow_html=True)
                else:
                    col1, col2 = st.columns(2)
                    with col1:     
                        explain_message1 = f"<font color='red'> There are {format_number(len(trans_no_cusid2))} mismatched transactions w/ {format_number(trans_no_cusid2.db_customerID.nunique())} mismatched unique CustomerID vs. Master_cust.customerID.</font><br>"
                        st.markdown(explain_message1, unsafe_allow_html=True)

                        # Displaying the table
                        mismatched_cusID = trans_no_cusid2[['db_db','db_storeID', 'db_customerID', 'wrt_dat','wrt_so_no','wrt_sale']]\
                            .sort_values(by='wrt_dat', ascending=False)\
                            .drop_duplicates(subset=['db_db', 'db_storeID', 'db_customerID', 'wrt_dat', 'wrt_so_no'])

                        table_fig = go.Figure(data=[go.Table(
                            header=dict(values=["<b>" + col + "</b>" for col in mismatched_cusID.columns], fill=dict(color='#2B3990'), font=dict(color='white', size=14)),
                            cells=dict(values=mismatched_cusID.head(100).transpose().values.tolist(), fill=dict(color='white'), font=dict(color='black', size=12))
                        )])

                        table_fig.update_layout(
                            title='<b>Data Glimpse of 100 Transactions with Unmatched db_customerIDs in Master_Cus<b>',
                            title_font=dict(color='#2B3990', size = 14),
                            width=1500,
                            #height=450,
                            margin=dict(t=50, b=10, l=10, r=10),
                            template="plotly_dark"
                        )

                        st.plotly_chart(table_fig, use_container_width=True)


                    with col2: 
                        explain_message2 = f"<font color='red'> Here is the glimspe of the sales analysis of those unmatched db_customerIDs</font><br>"
                        st.markdown(explain_message2, unsafe_allow_html=True)

                        trans_no_cusid1 = trans_no_cusid.copy()
                        trans_no_cusid1['wrt_dat'] = pd.to_datetime(trans_no_cusid1 ['wrt_dat'], format="%Y-%m-%d")
                        trans_no_cusid1['wrt_year'] = trans_no_cusid1 ['wrt_dat'].dt.year
                        trans_no_cusid1['wrt_month'] = trans_no_cusid1 ['wrt_dat'].dt.month  

                        no_result = trans_no_cusid1.groupby(['wrt_year']).agg({'wrt_sale':'sum'}).rename(columns={'wrt_sale':'unmatched_yearly_sale'}).reset_index()
                        res = master_trans1.groupby(['wrt_year']).agg({'wrt_sale':'sum'}).rename(columns={'wrt_sale':'yearly_sale'}).reset_index()
                        merge_no = no_result.merge(res, on = 'wrt_year', how = 'left')
                        merge_no['yearly_pct_unmatched_sale'] = merge_no['unmatched_yearly_sale']/merge_no['yearly_sale']*100
                        no_res2 = trans_no_cusid1.groupby(['wrt_year','wrt_month']).agg({'wrt_sale':'sum'}).rename(columns={'wrt_sale':'unmatched_monthly_sale'}).reset_index()

                        res2 = master_trans1.groupby(['wrt_year','wrt_month']).agg({'wrt_sale':'sum'}).rename(columns={'wrt_sale':'monthly_sale'}).reset_index()
                        merge_no2 = no_res2.merge(res2, on = ['wrt_year','wrt_month'], how = 'left')
                        merge_no2['monthly_pct_unmatched_sale'] = merge_no2['unmatched_monthly_sale']/merge_no2['monthly_sale']*100
                        merge_no3 = merge_no2.merge(merge_no, on = 'wrt_year', how = 'left')
                        # merge_no2 = merge_no2.rename(columns= {'wrt_sale_x':'total_sales', 'wrt_sale_y':'unmatched_sales'})
                        merge_no3['pct_unmatched_monthly_to_yearly_sale'] = merge_no3['unmatched_monthly_sale']/merge_no3['yearly_sale']*100
                        merge_no4 = merge_no3[['wrt_year','wrt_month','monthly_pct_unmatched_sale','yearly_pct_unmatched_sale', 'pct_unmatched_monthly_to_yearly_sale']]
                        merge_no4 = merge_no4.rename(columns={
                            'wrt_year': 'Year',
                            'wrt_month': 'Month',
                            'monthly_pct_unmatched_sale': 'Monthly % Unmatched Sale',
                            'yearly_pct_unmatched_sale': 'Yearly % Unmatched Sale',
                            'pct_unmatched_monthly_to_yearly_sale': 'Monthly-to-Yearly % Unmatched Sale'
                        })
                        def format_percentage(value):
                            return f"{value:.2f}%"
                        
                        def get_cell_color(value):
                            if value > 5:
                                return "#EFB5B9"
                            else:
                                return "white"
                        
                        # Apply formatting and coloring to the DataFrame
                        formatted_values = merge_no4[['Monthly % Unmatched Sale', 'Yearly % Unmatched Sale', 'Monthly-to-Yearly % Unmatched Sale']].applymap(format_percentage)
                        cell_colors = merge_no4[['Monthly % Unmatched Sale', 'Yearly % Unmatched Sale', 'Monthly-to-Yearly % Unmatched Sale']].applymap(get_cell_color)
                        

                        fig2 = go.Figure(
                            data=[
                                go.Table(
                                    header=dict(
                                        values=["<b>" + col + "</b>" for col in merge_no4.columns],
                                        fill_color='#2B3990',
                                        font=dict(color="white"),
                                        align="center",
                                        height=40,
                                        line_color='#2B3990'
                                    ),
                                    cells=dict(
                                            values=[
                                                merge_no4['Year'],
                                                merge_no4['Month'],
                                                formatted_values['Monthly % Unmatched Sale'].values,
                                                formatted_values['Yearly % Unmatched Sale'].values,
                                                formatted_values['Monthly-to-Yearly % Unmatched Sale'].values
                                            ], 
                                        line_color='#2B3990',
                                   
                                        fill=dict(
                                    color=[
                                        cell_colors['Monthly % Unmatched Sale'].values,
                                        cell_colors['Yearly % Unmatched Sale'].values,
                                        cell_colors['Monthly-to-Yearly % Unmatched Sale'].values
                                    ]
                                ),

                                        font=dict(color="black"),
                                        align="center",
                                        height=30,
                                    ),
                                )
                            ]
                        )
                        fig2.update_layout(
                            title='<b>Sales Analysis of Unmatched Transactions</b>',
                            title_font=dict(color='#2B3990'),
                            #title_font=dict(size=18, color='#043c7c', family='Arial'),
                            width=1500,
                            #height=300,
                            margin=dict(t=50, b=10, l=10, r=10),
                            template="plotly_dark"
                        )

                        st.plotly_chart(fig2, use_container_width=True)
                st.markdown("<hr style='border: 2px solid #001F3F;'>", unsafe_allow_html=True)
    ##############################################################################################################################################################
            with tab3: 
                image_url = "https://media.licdn.com/dms/image/D4E3DAQHWVajZ1sc61g/image-scale_191_1128/0/1695153109897/ls_direct_marketing_cover?e=2147483647&v=beta&t=0XFHIGXQzXC0yHyak2ornc1V-JLGsHoPY2RSjSps89s"
                st.image(image_url, use_column_width=True)

                st.markdown(f"<h3 style='text-align: center;'>🌍--Customer Overview--🌍</h3>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)

                # Column 1: Yearly Cust
                with col1:
                    count_unique_cust = master_trans1.groupby('wrt_year').agg(
                        Total_Count=('db_customerID', 'count'),
                        Unique_Count=('db_customerID', 'nunique')
                    ).reset_index() 

                    count_unique_cust = count_unique_cust[count_unique_cust.wrt_year >= 2017]
                    fig = go.Figure()

                    # Add the area plot for 'total_count'
                    fig.add_trace(
                        go.Scatter(x=count_unique_cust['wrt_year'],
                                   y=count_unique_cust['Total_Count'],
                                   fill='tozeroy',
                                   mode='lines+markers',
                                   marker=dict(symbol='circle',
                                               size=8,
                                               color='#2B3990',
                                               line=dict(width=2, color='white')),
                                   line=dict(color='#2B3990'),
                                   name='Total Count'))

                    # Add the area plot for 'unique_count'
                    fig.add_trace(
                        go.Scatter(x=count_unique_cust['wrt_year'],
                                   y=count_unique_cust['Unique_Count'],
                                   fill='tozeroy',
                                   mode='lines+markers',
                                   marker=dict(symbol='circle',
                                               size=8,
                                               color='#27AAE1',
                                               line=dict(width=2, color='white')),
                                   line=dict(color='#27AAE1'),
                                   name='Unique Count'))

                    # Customize the layout
                    fig.update_layout(xaxis_title='<b>Year</b>',
                                      yaxis_title='<b>Count</b>',
                                      title='<b>Total Count vs. Unique Count Over the Years</b>',
                                      title_font=dict(color='#2B3990', size = 14),
                                      template='plotly_dark',
                                      width=1000,
                                      height=450)
                    fig.update_layout(xaxis={'dtick': 1})
                    fig.update_layout(width=1500)  
                    st.plotly_chart(fig, use_container_width=True)

                # Column 2: Daily cust
                with col2:
                    count_unique_cust_daily = master_trans1.groupby('wrt_dat').agg(
                        Total_Count=('db_customerID', 'count'),
                        Unique_Count=('db_customerID', 'nunique')
                    ).reset_index() 

                    fig1 = go.Figure()

                    # Add the area plot for 'unique_count'
                    fig1.add_trace(
                        go.Scatter(x=count_unique_cust_daily['wrt_dat'],
                                   y=count_unique_cust_daily['Unique_Count'],
                                   fill='tozeroy',
                                   mode='lines+markers',
                                   marker=dict(symbol='circle',
                                               size=8,
                                               color='#27AAE1',
                                               line=dict(width=2, color='lightblue')),
                                   line=dict(color='#27AAE1'),
                                   name='Unique Count'))

                    # Customize the layout
                    fig1.update_layout(xaxis_title='<b>Date</b>',
                                       yaxis_title='<b>Count</b>',
                                       title='<b>Daily Unique Customers</b>',
                                       title_font=dict(color='#2B3990', size = 14),
                                       template='plotly_dark'
                                       # width=1000,
                                       # height=450
                                    )
                    # Show the chart
                    fig1.update_layout(width=1500)  
                    st.plotly_chart(fig1, use_container_width=True)

                ##################################################################
                line_colors = [
                    'grey', '#27AAE1', '#2B3990', '#000BE5', 'Violet', 'lightpink', 'yellow', 'mediumblue'
                    ]

                dow_cus_month = master_trans1.groupby(['wrt_year', 'wrt_month']).agg({
                    'db_customerID':
                    'count'
                }).reset_index()

                dow_cus_month = dow_cus_month[dow_cus_month.wrt_year >= 2017]


                dow_cus_unique_month = master_trans1.groupby(['wrt_year', 'wrt_month']).agg({
                    'db_customerID':
                    'nunique'
                }).reset_index()

                dow_cus_unique_month = dow_cus_unique_month[dow_cus_unique_month.wrt_year > 2019]

                # Find min,max values
                min_value = dow_cus_month['db_customerID'].min()
                min_index = dow_cus_month['db_customerID'].idxmin()
                max_value = dow_cus_month['db_customerID'].max()
                max_index = dow_cus_month['db_customerID'].idxmax()


                with col1:
                    fig3 = px.line(dow_cus_month,
                              x='wrt_month',
                              y='db_customerID',
                              color='wrt_year',
                              title='<b>Comparison of Total Customers by Month and Year<b>',
                              labels={
                                  'wrt_month': 'Month',
                                  'db_customerID': 'Total Customers',
                                  'wrt_year': 'Year'
                              },
                              template='plotly_dark',
                            )

                    # Annotate the minimum + maximum point
                    fig3.add_annotation(x=dow_cus_month.loc[min_index, 'wrt_month'],
                                       y=min_value,
                                       text=f'Min: {min_value:,.2f}',
                                       showarrow=True,
                                       arrowhead=1,
                                       arrowcolor='red',
                                       font=dict(color='white', size=12),
                                       bgcolor='red',
                                       opacity=0.7,
                                       xshift=10,
                                       yshift=10)

                    # Annotate the minimum point
                    fig3.add_annotation(x=dow_cus_month.loc[max_index, 'wrt_month'],
                                       y=max_value,
                                       text=f'Max: {max_value:,.2f}',
                                       showarrow=True,
                                       arrowhead=1,
                                       arrowcolor='red',
                                       font=dict(color='white', size=12),
                                       bgcolor='red',
                                       opacity=0.7,
                                       xshift=10,
                                       yshift=10)

                    for idx, year in enumerate(fig3.data):
                        fig3.data[idx].line.color = line_colors[idx % len(line_colors)]

                    fig3.update_traces(
                        mode='lines+markers',
                        marker=dict(size=7),
                    )

                    fig3.update_layout(
                        width=1000,  
                        height=450,  
                        title_font=dict(color='#2B3990', size = 14),
                        yaxis=dict(range=[0, max(dow_cus_month['db_customerID'])])
                    )
                    fig3.update_xaxes(title_text='<b>Month<b>')
                    fig3.update_yaxes(title_text='<b>Total Customers<b>')
                    fig3.update_layout(width=1500)  
                    st.plotly_chart(fig3, use_container_width=True)

                # Column 2: Daily cust
                with col2:
                    fig4 = px.line(dow_cus_unique_month,
                              x='wrt_month',
                              y='db_customerID',
                              color='wrt_year',
                              title='<b>Comparison of Total Unique Customers by Month and Year<b>',
                              labels={
                                  'wrt_month': 'Month',
                                  'db_customerID': 'Total Unique Customers',
                                  'wrt_year': 'Year'
                              },
                              template='plotly_dark',
                            )
                    fig4.update_traces(
                        mode='lines+markers',
                        marker=dict(size=7),
                    )
                    for idx, year in enumerate(fig4.data):
                        fig4.data[idx].line.color = line_colors[idx % len(line_colors)]

                    fig4.update_layout(
                        width=1000,  
                        height=450,  
                        title_font=dict(color='#2B3990', size = 14),
                        yaxis=dict(range=[0, max(dow_cus_unique_month['db_customerID'])])
                    )
                    fig4.update_xaxes(title_text='<b>Month<b>')
                    fig4.update_yaxes(title_text='<b>Total Unique Customers<b>')
                    fig4.update_layout(width=1500)  
                    st.plotly_chart(fig4, use_container_width=True)

                ###########################################################################
                life_time_purchase = master_trans1.groupby('db_customerID').agg({'wrt_so_no':'nunique'}).\
                rename(columns = {'wrt_so_no':'Number of Purchases'}).reset_index()

                purchase_frequency = life_time_purchase['Number of Purchases'].value_counts().reset_index()
                purchase_frequency.columns = ['Number of Purchases', 'Customer Count']

                total_customers = purchase_frequency['Customer Count'].sum()
                def cat(number_of_purchases):
                    if number_of_purchases == 1:
                        return "1 Purchase"
                    elif number_of_purchases == 2:
                        return "2 Purchases"
                    elif number_of_purchases == 3:
                        return "3 Purchases"
                    elif number_of_purchases == 4:
                        return "4 Purchases"
                    elif number_of_purchases == 5:
                        return "5 Purchases"
                    elif number_of_purchases == 10:
                        return "10 Purchases"
                    else:
                        return "> 10 Purchases"

                # Specify the desired order of categories
                desired_order = ['1 Purchase', '2 Purchases', '3 Purchases', '4 Purchases', '5 Purchases', '10 Purchases', '> 10 Purchases']

                # Apply the custom function to create a new 'category' column
                purchase_frequency['Category'] = purchase_frequency['Number of Purchases'].apply(cat)

                # Print the updated DataFrame
                purchase_frequency.head(100)


                cat_count = purchase_frequency.groupby('Category')['Customer Count'].sum().reset_index()

                cat_count['Percentage'] = round((cat_count['Customer Count'] / total_customers) * 100,4)
                cat_count['Percentage'] = cat_count['Percentage'].astype(str) + '%'
                cat_count['Category'] = pd.Categorical(cat_count['Category'], categories=desired_order, ordered=True)
                cat_count = cat_count.sort_values('Category')

                fig5 = px.bar(
                    cat_count,
                    x='Category',
                    y='Customer Count',
                    text='Percentage',  
                    title='<b>Customer Count and Percentage by Number of Purchases<b>',
                    labels={'Number of Purchases': 'Number of Purchases', 'Customer Count': 'Customer Count'},
                    template='plotly_dark',
                    color_discrete_sequence=['#2B3990']
                )

                # Customize the layout
                fig5.update_layout(
                    xaxis_title='<b>Number of Purchases<b>',
                    yaxis_title='<b>Customer Count<b>',
                    title_font=dict(color='#2B3990', size = 14),
                    showlegend=False,
                    width=1500,
                    #height=450,
                )

                st.plotly_chart(fig5, use_container_width=True)




