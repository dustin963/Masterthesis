import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
#import os
import plotly.graph_objects as go
from statsmodels.stats import proportion
from datetime import datetime
#from bertopic import BERTopic


#pipreqs "C:\Users\dusti\OneDrive\Maastricht\Master\MasterArbeit\coding stuff\Github"
#path = os.path.dirname(__file__)
my_file = 'Model_09_06_2022_size20_nrtopicsauto_reducedto60.xlsx'
st.set_page_config(page_title="Topic Modelling German Banking", page_icon=":bar_chart:", layout="wide")
@st.cache
def get_data():
    df = pd.read_excel(my_file, sheet_name="evaluations",usecols="B:D,F,G,H,L:M")
    df = df[df["Customer Dimension"]!="Nicht klassifiziert"]
    return df
df = get_data()

# ---- MAINPAGE ----
st.title(":bar_chart: Customer Evaluations")
st.markdown("##")

#st.sidebar.header("Please Filter Here:")
st.header(":triangular_ruler: Filters")
banktyp = st.multiselect(
    "Select the Banktype:",
    options=df["Banktyp"].unique(),
    default=df["Banktyp"].unique()
)
start_time,end_time = st.slider(
     "Correpsonding Timespans",
     value=(datetime(2022, 6,15),datetime(2015, 1,1)),
     format="MM/YY")
st.text(start_time)
st.text(end_time)
st.markdown("##")
st.markdown("""---""")

df_selection = df.query("Banktyp==@banktyp & date>=@start_time & date<=@end_time")
st.header(":mag: Descriptives")
# TOP KPI's
total_reviews = int(df_selection["company"].count())
average_rating = round(df_selection["rating"].mean(), 1)
star_rating = ":star:" * int(round(average_rating, 0))
amount_banks = round(df_selection["company"].nunique(), 2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Reviews:")
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


rating_by_banktype = (
    df_selection.groupby(by=["Banktyp"]).mean()[["rating"]].sort_values(by="rating")
)
fig_rating_by_type = px.bar(
    rating_by_banktype,
    x=rating_by_banktype.index,
    y="rating",
    orientation="v",
    title="<b>Rating by Banktype</b>",
    color_discrete_sequence=["#0083B8"] * len(rating_by_banktype),
    template="plotly_white",)

fig_rating_by_type.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)
banktyps = df_selection["Banktyp"].unique()
dimensions = df_selection["Customer Dimension"].unique()

proportions = []
error = []
customerdimension = []
banktypl = []

for banktyp in banktyps:
    for dimension in dimensions:
        y,x =proportion.proportion_confint(count=df_selection[(df_selection["Banktyp"]==banktyp)& (df_selection["Customer Dimension"]==dimension)]["company"].count(),    # Number of "successes"
                   nobs=df_selection[(df_selection["Banktyp"]==banktyp)]["company"].count(),    # Number of trials
                   alpha=(1 - 0.95))
        e = (x+y)/2-y
        p = (x+y)/2
        proportions.append(p)
        error.append(e)
        customerdimension.append(dimension)
        banktypl.append(banktyp)
        


proportions_bydimension = pd.DataFrame({"dimension":customerdimension,'banktyp': banktypl, 'proportion': proportions, 'error': error })
proportions_chart = px.scatter(proportions_bydimension, x="dimension", y="proportion", color="banktyp",
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








hide_st_style = """
            <style>
            
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)