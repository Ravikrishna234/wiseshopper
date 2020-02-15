from flask import Flask,request,jsonify,render_template, redirect, url_for, session
import requests
from bs4 import BeautifulSoup as bs
import asyncore
from urllib.request import urlopen as ulib
import pymongo
from random import random
from operator import itemgetter
import re,time,pprint
global lst
lst=[]
app= Flask(__name__)
app.secret_key ='search'
@app.route("/",methods= ['POST','GET'])

def index():
    if request.method == "POST":
        session['searchString']= request.form['content']
        session['searchString1'] = session.get('searchString').replace(" ", "")
        # session['searchString2'] = request.form['content1']
        # print(session.get('searchString2'))

        print((session.get('searchString')))
        return redirect(url_for('flipkart'))
    else:
        return render_template('index.html')
@app.route('/flipkart',methods= ['POST','GET'])
def flipkart():
    try:
        if request.method == "POST":
            session['searchString2'] = request.form['content1']
            session['radio']= request.form.get("gender")
            print(session.get('radio'))
            print(session.get('searchString2'))
        flipkart_url = "https://www.flipkart.com/search?q=" + session.get('searchString')
        print(flipkart_url)
        flipkartPage = requests.get(flipkart_url)
        # print(flipkartPage.text)
        flipkart_html = bs(flipkartPage.text, "html.parser")  # parsing the webpage as HTML
        bigboxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"})  # seacrhing for appropriate tag to redirect to the product link
        # filtered = flipkart_html.find_all('div', class_="bhgxx2 col-12-12")
        # print(filtered)
        # print(bigboxes)
        del bigboxes[0:3]  # the first 3 members of the list do not contain relevant information, hence deleting them.
        box = bigboxes[0]  # taking the first iteration (for demo)
        productname=flipkart_html.findAll('a', class_="_2cLu-l")
        productprice=flipkart_html.findAll('div',class_="_1vC4OE")
        # productdict=
        print(len(productname))
        productlist={}



        lst=[]
        if len(productname) > 0:
            for i in range(len(productname)):

                price = re.sub(r'[^\w]', ' ', productprice[i].text).replace(" ","")
                # price = int(price)
                print(price)
                #
                productlist = {"Product Name":productname[i].get('title'),"ProductPrice":int(price)}

                lst.append(productlist)
            # sorted(user,key=itemgetter('age'))

        else:
            productname = flipkart_html.findAll('div', class_="_3wU53n")
            productprice = flipkart_html.findAll('div', class_="_1vC4OE")
            for i in range(len(productname)):
                price = re.sub(r'[^\w]', ' ', productprice[i].text).replace(" ", "")

                productlist = {"Product Name":productname[i].text,"ProductPrice":int(price)}

                lst.append(productlist)
        # lst= sorted(lst, key=itemgetter('ProductPrice'))
        productLink = "https://www.flipkart.com" + box.div.div.div.a['href']  # extracting the actual product link
        prodRes = requests.get(productLink)  # getting the product page from server
        prod_html = bs(prodRes.text, "html.parser")  # parsing the product page as HTML
        commentboxes = prod_html.find_all('div', {'class': "_3nrCtb"})  # finding the HTML section containing the customer comments

        # table = db[searchString]  # creating a collection with the same name as search string. Tables and Collections are analogous.

        reviews = []  # initializing an empty list for reviews
        #  iterating over the comment section to get the details of customer and their comments
        for commentbox in commentboxes:
            try:
                name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text

            except:
                name = 'No Name'

            try:
                rating = commentbox.div.div.div.div.text

            except:
                rating = 'No Rating'

            try:
                commentHead = commentbox.div.div.div.p.text
            except:
                commentHead = 'No Comment Heading'
            try:
                comtag = commentbox.div.div.find_all('div', {'class': ''})
                custComment = comtag[0].div.text
            except:
                custComment = 'No Customer Comment'
            # fw.write(searchString+","+name.replace(",", ":")+","+rating + "," + commentHead.replace(",", ":") + "," + custComment.replace(",", ":") + "\n")
            mydict = {"Product": box.div.div.div.a.text, "Name": name, "Rating": rating, "CommentHead": commentHead,
                      "Comment": custComment}  # saving that detail to a dictionary
            # x = table.insert_one(mydict)  # insertig the dictionary containing the rview comments to the collection
            reviews.append(mydict)  # appending the comments to the review list
            
            if str(session.get('radio')) == "ascending":
                lst = sorted(lst, key=itemgetter('ProductPrice'))
            elif str(session.get('radio')) == "descending":
                sorted(lst, key=itemgetter('ProductPrice'), reverse=True)
            else:
                return render_template('flipkart.html', lst=lst)
        return render_template('flipkart.html', lst=lst)  # showing the review to the user
    except:
        return 'something is wrong'
        # return render_template('results.html')
@app.route('/ebay')
def ebay():
    try:
        url_seperator="&_sacat=0&_pgn=1"
        ebayurl="https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw="+ session.get('searchString')
        # time.sleep(random() * 5 * 60)
        print(ebayurl)
        lpt = []
        count= 0
        productlist1 = {}
        ebayurlPage = requests.get(ebayurl)
        # print(ebayurlPage.text)
        ebayurlPage_html = bs(ebayurlPage.text, "html.parser")  # parsing the webpage as HTML
        for post in ebayurlPage_html.findAll("li",class_="s-item"):
            # link=post.findAll("h3",class_="s-item__title s-item__title--has-tags")
            productname=post.findAll("h3",class_="s-item__title s-item__title--has-tags")
            productprice=post.findAll("span",class_= "s-item__price")
            # print(productprice)
            if productname and productprice:
                productlist1 = {"Product Name": productname[0].text, "Product Price": productprice[0].text}
                lpt.append(productlist1)
                print(productprice[0].text)
                # count=count+1
        #
        # for i in range(count):
        #
        #
        # if not productlist1:
        #     return "Item Not Found in Ebay try some other website"
        return render_template('ebay.html', lpt=lpt)
    except:
        return "Item Not Found in Ebay try some other website"
@app.route("/Snapdeal")
def Snapdeal():
    try:
        url_seperator="&sort=rlvncy"
        snapdealurl="https://www.snapdeal.com/search?keyword="+ session.get('searchString1')+url_seperator
        print(snapdealurl)
        lrt = []
        count= 0
        productlist2 = {}
        snapdealurlPage = requests.get(snapdealurl)
        # print(snapdealurlPage.text)
        snapdealurl_html = bs(snapdealurlPage.text, "html.parser")  # parsing the webpage as HTML
        productname = snapdealurl_html.findAll("div",class_= "product-desc-rating")
            # link=post.findAll("h3",class_="s-item__title s-item__title--has-tags")
            # productname=post.p.text
        productprice=snapdealurl_html.findAll("span",class_="lfloat product-price")
        for i in range(len(productname)):
            print(productprice[i].text)
            productlist2 = {"Product Name": productname[i].p.text, "Product Price": productprice[i].text}
            lrt.append(productlist2)
        # print(lst)

        return render_template('Snapdeal.html', lrt=lrt)
    except:
        return "Item Not Found in Ebay try some other website"
@app.route("/Amazon")
def Amazon():
    try:
        url_seperator="&sort=rlvncy"
        amazonurl="https://www.amazon.in/s?k="+ session.get('searchString')
        print(amazonurl)
        let = []
        count= 0
        productlist2 = {}
        amazonPage = requests.get(amazonurl)
        # print(tatacliqPage.text)
        amazon_html = bs(amazonPage.text, "html.parser")  # parsing the webpage as HTML
        productname = amazon_html.findAll("span",class_= "a-text-normal")
        productprice =amazon_html.findAll("span", class_="a-offscreen")
        # link=post.findAll("h3",class_="s-item__title s-item__title--has-tags")
        # productname=productname.a.get('title')
        # print(productname.findAll(class_="a-link-normal"))
        for i in range(len(productname)):
            print(productprice[i].text)
        for i in range(len(productname)):
            # print(productprice[i].text)
            productlist2 = {"Product Name": productname[i].text, "Product Price": productprice[i].text}
            let.append(productlist2)
        return render_template('amazon.html', let=let)
    except:
        return "Item Not Found in Ebay try some other website"
if __name__ == "__main__":
    app.run(port=8000, debug=True)  # running the app on the local machine on port 8000
