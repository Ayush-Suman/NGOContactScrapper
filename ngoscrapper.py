import requests
from bs4 import BeautifulSoup
from pyexcel_xls import save_data
from collections import OrderedDict

excel = "ngodata.xls"

data = OrderedDict()
listdata = [["Name", "State", "Link"]]

states = [
    'delhi',
    'bihar'
]

for state in states:
    i = 1
    while True:
        url = "https://ngosindia.org/{}/?lcp_page0={}".format(state, i)
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.text, "html.parser")
            ul = soup.find('ul', class_ = 'lcp_catlist')
            lis = ul.find_all('li')
            if len(lis) == 0 or i==2:
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
