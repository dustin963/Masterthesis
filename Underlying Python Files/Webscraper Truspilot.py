import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from random import randint
from time import sleep





# The number of available pages and the Bankname have to be set by the user
pagenumber = 531
bankname = "ING"

for i in range(290,pagenumber+1):
    sleep(randint(1,2))
    print("this is the current number of iterations:" + str(i))
    url = "https://de.trustpilot.com/review/ing.de?page="+ str(i)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    #y = soup.findAll("a", class_=("link_internal__7XN06", "button_button__T34Lr", "button_medium__a_AHE", "button_primary__VTK8w", "link_button___108l, pagination-link_item__mkuN3"))
    #x = soup.find(["main", "div","section","div","nav"], {"class":["layout_content__o0ojo", "styles_mainContent__nFxAv","styles_reviewsContainer__3_GQw","styles_pagination__6VmQv","link_internal__7XN06 link_disabled__mIxH1 button_button__T34Lr button_medium__a_AHE button_primary__VTK8w link_button___108l pagination-link_current___vBZ_ pagination-link_item__mkuN3"]})
    #y = x.find("a",class_="link_internal__7XN06 link_disabled__mIxH1 button_button__T34Lr button_medium__a_AHE button_primary__VTK8w link_button___108l pagination-link_current___vBZ_ pagination-link_item__mkuN3")

    data = json.loads(soup.find('script', type='application/ld+json').text)
    json_string=json.dumps(data)
    #print(json_string)
    with open('json_data.json', 'w') as outfile:
        outfile.write(json_string)

    reviews = data["@graph"]
    companynames = []
    dates = []
    headlines = []
    reviewBodies = []
    reviewRating = []
    
    for review in data["@graph"]:
        if review["@type"]=="Review":
            companynames.append(bankname)
            dates.append(review["datePublished"])
            headlines.append(review["headline"])
            reviewBodies.append(review["reviewBody"])
            reviewRating.append(review["reviewRating"]["ratingValue"])
    
    
    if i == 1 or i==290:
        TrustPilot = pd.DataFrame({"company":companynames,'date': dates, 'headline': headlines, 'body': reviewBodies, 'rating': reviewRating})
        print(TrustPilot)
        TrustPilot.to_csv("MorerecentData/TruspilotCustomerReviews"+ bankname+".csv",index=False,encoding="utf-8-sig",header=True)
    elif i != 1:
        TrustPilot = pd.DataFrame({"company":companynames,'date': dates, 'headline': headlines, 'body': reviewBodies, 'rating': reviewRating})
        print(TrustPilot)
        TrustPilot.to_csv("MorerecentData/TruspilotCustomerReviews"+bankname+".csv",index=False,encoding="utf-8-sig",mode="a",header=False)

    TrustPilotdftest = pd.DataFrame({"company":companynames,'date': dates, 'headline': headlines, 'body': reviewBodies, 'rating': reviewRating})
    


    #df = pd.DataFrame({"Text":results})
    #df.to_csv("headlines.csv",index=False,encoding="utf-8")
