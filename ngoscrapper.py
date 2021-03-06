import requests
from bs4 import BeautifulSoup
from pyexcel_xls import save_data
from collections import OrderedDict

states = [u'andaman-nicobar', u'andhra-pradesh', u'arunachal-pradesh', u'assam', u'bihar', u'chandigarh', u'chhattisgarh', u'dadra-nagar-haveli', u'daman-and-diu', u'delhi', u'goa', u'gujarat', u'haryana', u'himachal-pradesh', u'jammu-and-kashmir', u'jharkhand', u'karnataka', u'kerala', u'ladakh', u'lakshadweep', u'madhya-pradesh', u'maharashtra', u'mumbai', u'manipur', u'meghalaya', u'mizoram', u'nagaland', u'orissa', u'pondicherry', u'punjab', u'rajasthan', u'sikkim', u'tamil-nadu', u'telangana', u'tripura', u'uttarakhand', u'uttar-pradesh', u'west-bengal']

#url = 'https://ngosindia.com/contact-us/'
#page = requests.get(url)
#soup = BeautifulSoup(page.text, "html.parser")
#div = soup.find_all('div', 'ngo-blockcontent')
#print(str(div).replace(',', '\n\n'))
#div = div[8].find('div')
#ul = div.find('ul')
#lis = ul.find_all('li')
#for li in lis:
#    strong = li.find('strong')
#    a = strong.find('a', href=True)
#    states.append(a['href'].split('/')[3])
#print(states)

excel = "ngodata.xls"

data = OrderedDict()
listdata = [["Name", "State", "Link"]]



for state in states:
    i = 1
    while True:
        url = "https://ngosindia.org/{}/?lcp_page0={}".format(state, i)
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.text, "html.parser")
            ul = soup.find('ul', class_ = 'lcp_catlist')
            lis = ul.find_all('li')
            if len(lis) == 0:
                raise Exception
            for li in lis:
                a = li.find('a', href = True)
                print(a.text +" "+a['href']+"\n")
                listdata.append([a.text, state, a['href']])
            
            i+=1
            print(i)
        except Exception as e:
            print("No more page left")
            break 
    # print(page)
    data.update({"Sheet1": listdata})
    save_data(excel, data)
print("Data Saved")

listdata.remove(["Name", "State", "Link"])
excel = "ngocontactdata.xls"
contactlistdata = [["Name", "State", "Link", "Email", "Mobile"]]

for singledata in listdata:
    url = singledata[2]
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    div = soup.find_all('div', class_ = 'npos-postcontent')
    #print("Div: "+str(div[1]))
    p = div[1].find('p')
    texts = str(p).split('<br/>')
    #print(texts)
    email = ''
    mobile = ''
    for text in texts:
        text = text.replace('\n', '')
        print("Text: "+text)
        if text.startswith('Email'):
            email = text.split(':')[1]
            print("Email: "+email.strip())
        elif text.startswith('Mobile'):
            mobile = text.split(':')[1]
    contactlistdata.append([singledata[0], singledata[1], singledata[2], email.strip(), mobile.strip()])
    data.update({"Sheet1": contactlistdata})
    save_data(excel, data)
print("Contacts Saved")


import asyncio
import aiohttp


links = []
excel = "ngodata.xls"


async def getcontacts(name, state, url, session:aiohttp.ClientSession, **kwargs)->dict:
    print("Requesting for "+url)
    try:
        resp = await session.request('GET', url=url, **kwargs)
        text = await resp.text()
        #print(text)
        soup = BeautifulSoup(text, "html.parser")
        div = soup.find_all('div', class_ = 'npos-postcontent')
        print("Div: "+str(div))
        p = div[1].find('p')
        texts = str(p).split('<br/>')
        #print(texts)
        email = ''
        mobile = ''
        for text in texts:
            text = text.replace('\n', '')
            print("Text: "+text)
            if text.startswith('Email'):
                email = text.split(':')[1]
                print("Email: "+email.strip())
            elif text.startswith('Mobile'):
                mobile = text.split(':')[1]
    except:
        email = ''
        mobile = ''
    finally:
        dic = {"Name": name, "State":state, "Link":url, "Email": email, "Mob": mobile}
        return dic

async def getallcontacts(**kwargs):
    async with aiohttp.ClientSession() as session:
        tasks = []
        datasheet:list = data["Sheet1"]
        datasheet.remove(["Name", "State", "Link"])
        for c in datasheet:
            tasks.append(getcontacts(session=session, name=c[0], state=c[1], url=c[2], **kwargs))
        #print(tasks)
        htmls = await asyncio.gather(*tasks)
        print("Gathering Done")
        #print(htmls)
        return htmls

loop = asyncio.get_event_loop()
try:
    final_data = loop.run_until_complete(getallcontacts())
finally:
    loop.close()

final_list = ["Name", "State", "Link", "Email", "Mobile"]

for singledata in final_data:
    final_list.append([singledata['Name'],singledata['State'],singledata['Link'],singledata['Email'],singledata['Mob']])

excel = "ngocontactdata.xls"
data.update({"Sheet1": final_list})
save_data(excel, data)

