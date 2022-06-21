import pandas as pd  # pip install pandas openpyxl
import plotly.express as px
from requests import options  # pip install plotly-express
import streamlit as st  # pip install streamlit
import os
import plotly.graph_objects as go
from statsmodels.stats import proportion
from datetime import datetime
import streamlit.components.v1 as components
import numpy as np
import scipy.stats as sta

#from bertopic import BERTopic


#pipreqs "C:\Users\dusti\OneDrive\Maastricht\Master\MasterArbeit\coding stuff\Github"
#path = os.path.dirname(__file__)
my_file = '15.06NRautoreduced to 100.xlsx'
st.set_page_config(page_title="Topic Modelling German Banking", page_icon=":bar_chart:", layout="wide")
@st.cache
def get_data():
    dfunfiltered = pd.read_excel(io="15.06NRautoreduced to 100.xlsx",engine="openpyxl",sheet_name="evaluations")
    dfunfiltered["year"] = dfunfiltered["date"].dt.year
    
    dfunfiltered = dfunfiltered[dfunfiltered["year"]>=2014]
    df = dfunfiltered[dfunfiltered["customer dimension"]!="not classified"]
    

    return df,dfunfiltered
df,dfunfiltered = get_data()

# ---- MAINPAGE ----
st.title(":bar_chart: Customer Evaluations")
st.markdown("##")

st.sidebar.header(":triangular_ruler: Filters")

banktype = st.sidebar.multiselect(
    "Select the banktype:",
    options=df["banktype"].unique(),
    default=df["banktype"].unique()
)
start_time,end_time = st.sidebar.select_slider(
     "Correpsonding Timespans",
     #value=(datetime(2022, 6,15),datetime(2014, 1,1)),
     #format="MM/YY")
     options=sorted(dfunfiltered["year"].unique()),
     value=(2022,2014))

st.sidebar.subheader("About")
st.sidebar.info("The corresponding code can be found on [Github](https://github.com/dustin963/Masterthesis)")

#df_selection = df.query("banktype==@banktype & date>=@start_time & date<=@end_time")
#dfunfiltered = dfunfiltered.query("banktype==@banktype & date>=@start_time & date<=@end_time")
df_selection = df.query("banktype==@banktype & year>=@start_time & year<=@end_time")
dfunfiltered = dfunfiltered.query("banktype==@banktype & year>=@start_time & year<=@end_time")

st.header(":mag: Descriptives")
# TOP KPI's
total_classified_reviews = int(df_selection["company"].count())
total_reviews = int(dfunfiltered["company"].count())
average_rating = round(dfunfiltered["rating"].mean(), 1)
star_rating = ":star:" * int(round(average_rating, 0))
amount_banks = round(dfunfiltered["company"].nunique(), 2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Classified Reviews/Total Reviews:")
    class_success = str(total_classified_reviews)+"/"+str(total_reviews)
    st.subheader(class_success)
    

with middle_column:
    st.subheader("Average Rating:")
    st.subheader(f"{average_rating} {star_rating}")
with right_column:
    st.subheader("Observed Banks:")
    st.subheader(f"{amount_banks}")
#st.markdown("""---""")
st.markdown("##")



rating_by_banktypee = (
    dfunfiltered.groupby(by=["banktype"]).mean()[["rating"]].sort_values(by="rating")
)
fig_rating_by_type = px.bar(
    rating_by_banktypee,
    x=rating_by_banktypee.index,
    y="rating",
    orientation="v",
    title="<b>Rating by banktypee</b>",
    color_discrete_sequence=["#0083B8"] * len(rating_by_banktypee),
    template="plotly_white",)

fig_rating_by_type.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

banktypes = df_selection["banktype"].unique()
dimensions = df_selection["customer dimension"].unique()

proportions = []
error = []
customerdimension = []
banktypel = []
means = []
counts = []
error_mean = []

for banktype in banktypes:
    for dimension in dimensions:
        mean = df_selection[(df["banktype"]==banktype)& (df["customer dimension"]==dimension)]["rating"].mean()
        my,mx =sta.norm.interval(alpha=0.95,loc=np.mean(df_selection[(df["banktype"]==banktype)& (df["customer dimension"]==dimension)]["rating"]))
        count = df_selection[(df["banktype"]==banktype)& (df["customer dimension"]==dimension)]["rating"].count()
        y,x =proportion.proportion_confint(count=df_selection[(df["banktype"]==banktype)& (df["customer dimension"]==dimension)]["body"].count(),    # Number of "successes"
                   nobs=df_selection[(df["banktype"]==banktype)]["body"].count(),    # Number of trials
                   alpha=(1 - 0.95))
        e = (x+y)/2-y
        p = (x+y)/2
        em = (mx+my)/2-my
        mm = (mx+my)/2
        proportions.append(p)
        error.append(e)
        customerdimension.append(dimension)
        banktypel.append(banktype)
        means.append(mean)
        error_mean.append(em)
        counts.append(count)
        


proportions_bydimension = pd.DataFrame({"dimension":customerdimension,'banktype': banktypel, 'proportion': proportions, 'error proportions': error,"mean" :means,"count":counts,"error mean":error_mean})


proportions_chart = px.scatter(proportions_bydimension, x="dimension", y="proportion", color="banktype",
                 error_y="error proportions")
proportions_chart.update_layout(height=800,
    plot_bgcolor="rgba(0,0,0,0)",

    xaxis=(dict(showgrid=False))
)


gr_dimensiondf =df_selection.groupby(["customer dimension"],as_index=False).count()[["customer dimension","company"]]
total_reviews = gr_dimensiondf["company"].sum()
gr_dimensiondf['perc'] = gr_dimensiondf['company'].apply(lambda x: x*100/total_reviews.sum())
gr_dimensiondf = gr_dimensiondf.sort_values(by=["perc"],ascending=False)

dimensions_chart= px.bar(gr_dimensiondf,x="customer dimension",y="perc")
dimensions_chart.update_layout(title='Customer Reviews by Percentage',
           xaxis_title='Customer Dimension', yaxis_title='Percentage of Reviews',title_x=0.5)


proportions_chart_rating = px.bar(proportions_bydimension, x="dimension", y="mean", color="banktype",barmode="group"
                 )


yearly_dimensiondf = pd.DataFrame(columns=["customer dimension","company","year","perc"])

for year in df_selection["year"].unique():

    gryr_dimensiondf = df_selection[df_selection["year"]==year]
    gryr_dimensiondf =gryr_dimensiondf.groupby(["customer dimension"],as_index=False).count()[["customer dimension","company"]]
    gryr_dimensiondf["year"] = year
    total_reviews = gryr_dimensiondf["company"].sum()
    gryr_dimensiondf['perc'] = gryr_dimensiondf['company'].apply(lambda x: x*100/total_reviews.sum())
    yearly_dimensiondf = yearly_dimensiondf.append(gryr_dimensiondf,ignore_index=True)

df_selection["yearspan"] = np.where((df_selection["year"]>=2014) &(df_selection["year"]<=2016), "2014-2016"
,np.where((df_selection["year"]>=2017) &(df_selection["year"]<=2019), "2017-2019",
np.where((df_selection["year"]>=2020) &(df_selection["year"]<=2022), "2020-2022","")))


yearly_dimensiondf = pd.DataFrame(columns=["customer dimension","company","yearspan","perc"])

for yearspan in df_selection["yearspan"].unique():

    gryr_dimensiondf = df_selection[df_selection["yearspan"]==yearspan]
    gryr_dimensiondf =gryr_dimensiondf.groupby(["customer dimension"],as_index=False).count()[["customer dimension","company"]]
    gryr_dimensiondf["yearspan"] = yearspan
    total_reviews = gryr_dimensiondf["company"].sum()
    gryr_dimensiondf['perc'] = gryr_dimensiondf['company'].apply(lambda x: x*100/total_reviews.sum())
    yearly_dimensiondf = yearly_dimensiondf.append(gryr_dimensiondf,ignore_index=True)


yearly_dimensions_chart = px.bar(yearly_dimensiondf.sort_values("yearspan"),x="customer dimension",y="perc",color="yearspan",barmode="group")
summarytable = dfunfiltered[["rating","company"]].groupby(["company"]).describe()["rating"][["mean","count","std"]].round(2)


left2_column, right2_column = st.columns(2)
with left_column:
    st.subheader("Ratings")
    st.plotly_chart(fig_rating_by_type)
with right_column:
    st.subheader("Summary:")
    st.dataframe(summarytable)

st.subheader(":arrow_upper_right: New Rating across the year")
yearly_review_amounts = (dfunfiltered.groupby(["year"],as_index=False).count().round(2)[["banktype","year"]])
yearly_amount_chart= px.bar(yearly_review_amounts,x="year",y="banktype")
yearly_amount_chart.update_layout(title='Amount of new Reviews per Year',
           xaxis_title='Time', yaxis_title='Amount of new Reviews',title_x=0.5)


st.plotly_chart(yearly_amount_chart,use_container_width=True)

length_rating = go.Figure()
length_rating.add_trace(go.Box(x=dfunfiltered["rating"],
    y=dfunfiltered["length of review"],
    name="Onl",
    boxpoints="suspectedoutliers", # no data points
    marker_color='rgb(9,56,125)',
    line_color='rgb(9,56,125)'
))
length_rating.update_layout(title_text="length of reviews by rating",title_x=0.5,xaxis_title='Rating', yaxis_title='length of review',)

st.subheader(":love_letter: Length of customer reviews by rating")
st.plotly_chart(length_rating)


st.markdown("""---""")

st.header(":grey_question: Reported Customer Dimensions")


st.subheader("Proportions for customer dimensions")

st.plotly_chart(dimensions_chart,height=800,use_container_width=True)

st.subheader("Proportions for customer dimensions by banktype including 95"+"%"+" confidence intervals")

st.plotly_chart(proportions_chart,height=800,use_container_width=True)

st.subheader("Rating per customer dimension across banktype")

st.plotly_chart(proportions_chart_rating,height=800,use_container_width=True)

st.subheader("Rating per customer dimension across banktype")

st.plotly_chart(yearly_dimensions_chart,height=800,use_container_width=True)

st.markdown("""---""")


st.header(":page_facing_up: Dataframe")


st.dataframe(df_selection[["company","date","headline","originalbody","rating","customer dimension"]])

HtmlFile = open("text.html", 'r', encoding='utf-8')
source_code = HtmlFile.read() 



HtmlFile = open("visualizedtopics.html", 'r', encoding='utf-8')
visualizedtopics_code = HtmlFile.read() 


st.markdown("""---""")

st.header(":microscope: Topic Modelling Charts")
st.subheader("Topics Clustering")
st.info("The following graphs are not influenced by the filter settings")
components.html(visualizedtopics_code,scrolling=False,height=700)
st.subheader("Topics and Word Representations")
components.html(source_code, width=10000, height=1000,scrolling=True)




hide_st_style = """
            <style>
            
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

