import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
#import os
import plotly.graph_objects as go
from statsmodels.stats import proportion
from datetime import datetime
import streamlit.components.v1 as components
#from bertopic import BERTopic


#pipreqs "C:\Users\dusti\OneDrive\Maastricht\Master\MasterArbeit\coding stuff\Github"
#path = os.path.dirname(__file__)
my_file = '15.06NRautoreduced to 100.xlsx'
st.set_page_config(page_title="Topic Modelling German Banking", page_icon=":bar_chart:", layout="wide")
@st.cache
def get_data():
    df = pd.read_excel(io="15.06NRautoreduced to 100.xlsx",engine="openpyxl",sheet_name="evaluations")
    df = df[df["customer dimension"]!="not classified"]
    return df
df = get_data()

# ---- MAINPAGE ----
st.title(":bar_chart: Customer Evaluations")
st.markdown("##")

#st.sidebar.header("Please Filter Here:")
st.header(":triangular_ruler: Filters")
banktype = st.multiselect(
    "Select the banktype:",
    options=df["banktype"].unique(),
    default=df["banktype"].unique()
)
start_time,end_time = st.slider(
     "Correpsonding Timespans",
     value=(datetime(2022, 6,15),datetime(2015, 1,1)),
     format="MM/YY")
st.text(start_time)
st.text(end_time)
st.markdown("##")
st.markdown("""---""")

df_selection = df.query("banktype==@banktype & date>=@start_time & date<=@end_time")
st.header(":mag: Descriptives")
# TOP KPI's
total_reviews = int(df_selection["company"].count())
average_rating = round(df_selection["rating"].mean(), 1)
star_rating = ":star:" * int(round(average_rating, 0))
amount_banks = round(df_selection["company"].nunique(), 2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Classified Reviews:")
    st.subheader(f"{total_reviews:,}")
with middle_column:
    st.subheader("Average Rating:")
    st.subheader(f"{average_rating} {star_rating}")
with right_column:
    st.subheader("Observed Banks:")
    st.subheader(f"{amount_banks}")
#st.markdown("""---""")
st.markdown("##")
st.markdown("""---""")


rating_by_banktypee = (
    df_selection.groupby(by=["banktype"]).mean()[["rating"]].sort_values(by="rating")
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

for banktype in banktypes:
    for dimension in dimensions:
        y,x =proportion.proportion_confint(count=df_selection[(df_selection["banktype"]==banktype)& (df_selection["customer dimension"]==dimension)]["company"].count(),    # Number of "successes"
                   nobs=df_selection[(df_selection["banktype"]==banktype)]["company"].count(),    # Number of trials
                   alpha=(1 - 0.95))
        e = (x+y)/2-y
        p = (x+y)/2
        proportions.append(p)
        error.append(e)
        customerdimension.append(dimension)
        banktypel.append(banktype)
        


proportions_bydimension = pd.DataFrame({"dimension":customerdimension,'banktype': banktypel, 'proportion': proportions, 'error': error })
proportions_chart = px.scatter(proportions_bydimension, x="dimension", y="proportion", color="banktype",
                 error_y="error")
proportions_chart.update_layout(height=800,
    plot_bgcolor="rgba(0,0,0,0)",

    xaxis=(dict(showgrid=False))
)






summarytable = df_selection[["rating","company"]].groupby(["company"]).describe()["rating"][["mean","count","std"]]
st.text("")

left2_column, right2_column = st.columns(2)
with left_column:
    st.subheader("Ratings")
    st.plotly_chart(fig_rating_by_type)
with right_column:
    st.subheader("Summary:")
    st.dataframe(summarytable)

#topic_model = BERTopic.load(path+"/my_model")
#barcharttopicmodel = topic_model.visualize_barchart(n_words=10,top_n_topics=60)




st.plotly_chart(proportions_chart,height=800,use_container_width=True)
#st.plotly_chart(barcharttopicmodel)








st.dataframe(df_selection)

HtmlFile = open("/text.html", 'r', encoding='utf-8')
source_code = HtmlFile.read() 

components.html(source_code, width=10000, height=1000,scrolling=True)

HtmlFile = open("/visualizedtopics.html", 'r', encoding='utf-8')
visualizedtopics_code = HtmlFile.read() 


components.html(visualizedtopics_code, width=1000, height=1000,scrolling=False)



hide_st_style = """
            <style>
            
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

