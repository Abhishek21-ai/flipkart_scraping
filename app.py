from flask import Flask, render_template, request
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
import json



app = Flask(__name__)



@app.route('/', methods=['GET'])
def Home():
    return render_template('index.html')


@app.route("/search", methods=['POST'])
def search():
    try:
        if request.method == 'POST':
            keyword = request.form['search']
            pages = int(request.form['pages'])
            num_page =pages
            keyword = keyword.replace(' ', '+')
            title = []
            rating = []
            price = []
            insight = []
            images = []
            prod_url = []
            base_url = 'https://www.flipkart.com'
            prec_cnt = 0
            pric_cnt = 0
            for i in range(num_page):

                url = 'https://www.flipkart.com/search?q=' + keyword + '&page=' + str(i)

                doc = urllib.request.urlopen(url).read()
                soup = BeautifulSoup(doc, 'html.parser')
                dummy_title = soup.find_all('div', {'class': '_4rR01T'})
                dummy_rating = soup.find_all('div', {'class': '_3LWZlK'})
                dummy_price = soup.find_all('div', {'class': '_30jeq3 _1_WHN1'})
                dummy_insight = soup.find_all('ul', {'class': '_1xgFaf'})
                dummy_images = soup.find_all('img', {'class': '_396cs4 _3exPp9'})
                dummy_prod = soup.find_all('a', {'class': '_1fQZEK'})

                if len(dummy_title) == 0:
                    dummy_title = soup.find_all('a', {'class': 'IRpwTa'})
                    dummy_rating = soup.find_all('div', {'class': '_3LWZlK'})  # _2UzuFa
                    dummy_price = soup.find_all('div', {'class': '_30jeq3'})
                    dummy_insight = soup.find_all('div', {'class': '_2WkVRV'})
                    dummy_images = soup.find_all('img', {'class': '_2r_T1I'})
                    dummy_prod = soup.find_all('a', {'class': '_2UzuFa'})

                    if len(dummy_title) == 0:
                        dummy_title = soup.find_all('a', {'class': 's1Q9rs'})
                        dummy_rating = soup.find_all('div', {'class': '_3LWZlK'})
                        dummy_price = soup.find_all('div', {'class': '_30jeq3'})
                        dummy_insight = soup.find_all('div', {'class': '_3Djpdu'})
                        dummy_images = soup.find_all('img', {'class': '_396cs4 _3exPp9'})
                        dummy_prod = soup.find_all('a', {'class': '_2rpwqI'})

            

                for j in dummy_title:
                    x=j.text
                    j=x.replace(' ','')
                    title.append(j)

                for j in dummy_rating:
                    if prec_cnt < len(title):
                        rating.append(j.text)
                        prec_cnt = prec_cnt + 1
                    else:
                        break

                if len(title) != len(rating):
                    ref = len(title) - len(rating)
                    for x in range(ref):
                        rating.append('Not Available')
                for j in dummy_price:
                    if pric_cnt < len(title):
                        str_cvt = j.text
                        str_cvt = str_cvt.split('₹')[1]
                        str_cvt = int(str_cvt.replace(',', ''))
                        price.append(str_cvt)
                        pric_cnt = pric_cnt + 1
                    else:
                        break

                for j in dummy_insight:
                    insight.append(j.text)

                if len(title) != len(insight):

                    ref = len(title) - len(insight)
                    for x in range(ref):
                        insight.append('Not Available')

                for j in dummy_images:
                    images.append(j['src'])

                for j in dummy_prod:
                    prod_url.append(base_url + j['href'])

            
                my_dict = {'Product_Name': title, 'Price': price, 'Rating': rating, 'details': insight, 'image_url': images,'product_url': prod_url}

                df = pd.DataFrame(my_dict)
                df.to_json('static/product.json')
                
        return render_template('allprod.html',
                            tables=[df.to_html(classes='data',columns=['Product_Name','Price','Rating','details'])],  # pass the df as html
       
                            )
    except:
        return render_template('404.html')    


@app.route("/display")
def display():
    df= pd.read_json('static/product.json')
    return render_template('base.html', data=df['Product_Name'])


@app.route("/create",methods=['POST'])
def create():
    if request.method == 'POST':
        
        real_prod = request.form['real_prod']
        df=pd.read_json('static/product.json')
        url=df[df['Product_Name']==real_prod]['product_url'].values
        url=url[0]

    

        doc = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(doc, 'html.parser')

        dummy_review = soup.find_all('div', {'class': '_6K-7Co'})
        dummy_que = soup.find_all('div', {'class': '_1xR0kG _3cziW5 _1HEV8P'})  
        dummy_ans=soup.find_all('div',{'class': '_2yeNfb'})   
        
        # child_que=dummy_que.findChildren("span",recursive=False)

        if len(dummy_que) == 0:
            dummy_review = soup.find_all('div', {'class': 't-ZTKy'})
            dummy_que = soup.find_all('div', {'class': '_1xR0kG _3cziW5 _1HEV8P'})
            dummy_ans=soup.find_all('div',{'class': '_2yeNfb'})
            if len(dummy_que) == 0:
                dummy_review = soup.find_all('div', {'class': 't-ZTKy'})
                dummy_que = soup.find_all('div', {'class': '_1xR0kG _3cziW5'})
                dummy_ans=soup.find_all('div',{'class': '_2yeNfb'})
            
            

        
        review=[j.text.replace("READ","").replace("MORE","") for j in dummy_review]
       
        que=[]
        ans=[]
        for i in range(len(dummy_que)):
            que.append(dummy_que[i].text)
            ans.append(dummy_ans[i].text)
 
      
        rev_dict={'review':review,'que':que,'ans':ans}
    

       
        return render_template('review.html',data=rev_dict)
    
if __name__ == "__main__":
    app.run(debug=True)