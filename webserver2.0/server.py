#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "zc2425"
DB_PASSWORD = "TXePyLYulh"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")




@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def main():
  return render_template("main.html")

@app.route('/login2')
def login2():
  return render_template("loginpage.html")

#user log in: check whehter correct password
@app.route('/user_login', methods=['POST'])
def user_login():

  username_input = request.form['username']
  email_input = request.form['email']

  cml_email = "SELECT email FROM Customer WHERE username = '" + username_input + "'"
  true_email = g.conn.execute(text(cml_email))

  result_email = []
  for line in true_email:
  	result_email.append(line['email'])
  true_email.close()

  # user not exist
  if result_email == []:
    return render_template("user_not_exist.html")


  un = [username_input]
  if result_email != []:
  	if (email_input == result_email[0]) :
  		context = dict(data = result_email, un = un)
  		return render_template("mainwithlogin.html", **context)
  		#return render_template("main.html", **context)
      #return render_template("index.html", **context)
  	elif email_input != result_email[0]:
  		return render_template("wrong_password.html")


#return to main page with login
@app.route('/backtomain', methods=['POST', 'GET'])
def mainwithlogin():
  un = request.args.get('un')
  un = [un]
  context = dict(un = un)
  return render_template("mainwithlogin.html", **context)
 


#seller log in: check whehter correct password
@app.route('/seller_login', methods=['POST'])
def seller_login():
  username_input = request.form['username']
  email_input = request.form['email']

  cml_email = "SELECT email FROM Seller WHERE username = '" + username_input + "'"
  true_email = g.conn.execute(text(cml_email))

  result_email = []
  for line in true_email:
  	result_email.append(line['email'])
  true_email.close()

  # seller not exist
  if result_email == []:
	return render_template("seller_not_exist.html")
  if result_email != []:
  	if email_input == result_email[0]:
  		context = dict(data = result_email, username_input=username_input)
  		return render_template("seller_mainpage.html", **context)
  	elif email_input != result_email[0]:
  		return render_template("wrong_password.html")

#create page: seller account information, from seller_mainpage.html, to seller_account.html
@app.route('/seller_account')
def seller_account():
  seller_name = request.args.get('su')
  cmd = "SELECT * FROM Seller WHERE username = '" + seller_name + "'"
  result = g.conn.execute(text(cmd))

  username = []
  email = []
  date = []
  for line in result:
    username.append(line['username'])
    email.append(line['email'])
    date.append(line['create_date'])
  result.close()

  all_seller = []
  for i in range(0,len(username)):
    one_seller_row = []
    one_seller_row.append(username[i])
    one_seller_row.append(email[i])
    one_seller_row.append(date[i])
    all_seller.append(one_seller_row)
    one_seller_row = []

  print username
  print email
  print date
  print all_seller 

  context = dict(seller_name=seller_name, all_seller=all_seller)
  return render_template("seller_account.html", **context)

#create seller product page, from seller_prod.html, from seller_prod.html
@app.route('/seller_prod')
def seller_prod():
  seller_name = request.args.get('su')

  #get seller_id by seller name
  cml = "SELECT * FROM Seller WHERE username = '" + seller_name + "'"
  result = g.conn.execute(text(cml))
  sellerid = []
  for line in result:
    sellerid.append(line['user_id']) 
  result.close()

  #get seller's all products
  cml2 = "SELECT * FROM Product WHERE seller_id = " + str(sellerid[0]) + ""
  result2 = g.conn.execute(text(cml2))
  prod_id = []
  prod_name = []
  cat = []
  brand = []
  price = []
  for line2 in result2:
    prod_id.append(line2['product_id'])
    prod_name.append(line2['product_name']) 
    cat.append(line2['category_name'])
    brand.append(line2['brand'])
    price.append(line2['price'])
  result2.close()

  all_seller_prod = []
  for i in range(0,len(prod_id)):
    one_seller_prod = []
    one_seller_prod.append(prod_id[i])
    one_seller_prod.append(prod_name[i])
    one_seller_prod.append(cat[i])
    one_seller_prod.append(brand[i])
    one_seller_prod.append(price[i])
    all_seller_prod.append(one_seller_prod)
    one_seller_prod = []
  
  context = dict(prod_id = prod_id, all_seller_prod=all_seller_prod, seller_name=seller_name,sellerid=sellerid[0])
  return render_template("seller_prod.html", **context)

#remove seller product, from seller_prod.html
@app.route('/seller_remove_prod', methods=['POST','GET'])
def seller_remove_prod():
  seller_name = request.args.get('sn')
  #seller_id =request.args.get('seller_id')
  prod_id =request.args.get('prod_id')
  
  #get seller id by seller name
  cml = "SELECT * FROM Seller WHERE username = '" + seller_name + "'"
  result = g.conn.execute(text(cml))
  sellerid = []
  for line in result:
    sellerid.append(line['user_id']) 
  result.close()

  #seller remove a product
  cml2 = "DELETE FROM Product WHERE seller_id = " + str(sellerid[0]) + "and product_id = " + str(prod_id) + ""
  result2 = g.conn.execute(text(cml2))

   #find this seller's current product list
  cml3 = "SELECT * FROM Product WHERE seller_id = " + str(sellerid[0]) + ""
  result3 = g.conn.execute(text(cml3))
  prod_id_lst = []
  prod_name = []
  cat_lst = []
  brand = []
  price = []
  for line3 in result3:
    prod_id_lst.append(line3['product_id'])
    prod_name.append(line3['product_name'])
    cat_lst.append(line3['category_name'])
    brand.append(line3['brand'])
    price.append(line3['price'])
  result3.close()

  all_prod = []
  for i in range(0,len(prod_id_lst)):
    one_prod_row = []
    one_prod_row.append(prod_id_lst[i])
    one_prod_row.append(prod_name[i])
    one_prod_row.append(cat_lst[i])
    one_prod_row.append(brand[i])
    one_prod_row.append(price[i])
    all_prod.append(one_prod_row)
    one_prod_row = []

  print all_prod

  context = dict(seller_name=seller_name, all_seller_prod=all_prod,sellerid=sellerid[0])
  return render_template("seller_prod.html", **context)


#seller add product, from seller_prod.html
@app.route('/addproduct', methods=['POST','GET'])
def addproduct():
  seller_id = request.args.get('seller_id')
  seller_name = request.args.get('sn')
  product_name = request.form['product_name']
  category_name = request.form['category_name']
  brand = request.form['brand']
  price = request.form['price']

  #print seller_id
  #print category_name

  #select last line's product id
  cml = "SELECT * FROM Product ORDER BY product_id DESC LIMIT 1"
  result = g.conn.execute(text(cml))
  id_lst = []
  for line in result:
    id_lst.append(line['product_id'])
  result.close()

  #get all brand list
  cml11 = "SELECT * FROM brand"
  all_brand_lst = []
  result11 = g.conn.execute(text(cml11))
  for line11 in result11:
    all_brand_lst.append(line11['brand'])
  result11.close()

  #get all category list
  cml12 = "SELECT * FROM Category"
  all_cat_lst = []
  result12 = g.conn.execute(text(cml12))
  for line12 in result12:
    all_cat_lst.append(line12['category_name'])
  result12.close()

  #print category_name in all_cat_lst and brand in all_brand_lst
  #if newly added product in category and brand
  if category_name in all_cat_lst and brand in all_brand_lst:
    #insert value
    new_prod_id = int(id_lst[0])+1
    cmd2 = 'INSERT INTO Product VALUES (:product_id, :product_name, :category_name, :seller_id, :brand, :price)'
    result2 = g.conn.execute(text(cmd2), product_id = new_prod_id, product_name=product_name,
      category_name=category_name, seller_id = seller_id, brand=brand, price=price)
    
    #get seller's all products
    cml2 = "SELECT * FROM Product WHERE seller_id = " + str(seller_id) + ""
    result2 = g.conn.execute(text(cml2))
    prod_id = []
    prod_name = []
    cat = []
    brand = []
    price = []
    for line2 in result2:
      prod_id.append(line2['product_id'])
      prod_name.append(line2['product_name']) 
      cat.append(line2['category_name'])
      brand.append(line2['brand'])
      price.append(line2['price'])
    result2.close()

    all_seller_prod = []
    for i in range(0,len(prod_id)):
      one_seller_prod = []
      one_seller_prod.append(prod_id[i])
      one_seller_prod.append(prod_name[i])
      one_seller_prod.append(cat[i])
      one_seller_prod.append(brand[i])
      one_seller_prod.append(price[i])
      all_seller_prod.append(one_seller_prod)
      one_seller_prod = []
    
    context = dict(all_seller_prod=all_seller_prod, sellerid=seller_id)
    return render_template("seller_prod.html", **context)
  
  else:
    context = dict(sellerid=seller_id,seller_name=seller_name)
    return render_template("nonexist_cat_brand.html", **context)


#after failing to add product, back to seller main page; from nonexist_cat_brand.html
@app.route('/backsellermain', methods=['POST','GET'])
def backsellermain():
    seller_id = request.args.get('seller_id')
    seller_name = request.args.get('seller_name')
    context = dict(username_input=seller_name)
    return render_template("seller_mainpage.html", **context)

#visitor log in: just direct to main page
@app.route('/visitor_login',methods=['POST'])
def visitor_login():
	#return render_template("main.html")
  return render_template("main.html")



# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print name
  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
  g.conn.execute(text(cmd), name1 = name, name2 = name);
  return redirect('/')

# 0.5.  by productrt
@app.route('/searchProduct', methods=['POST'])
def searchProduct():
  un = request.args.get('username')
  product_input = request.form['product'].lower() # case insensitive
  store_product_input = [] # store this input for later use
  store_product_input.append(product_input)
  
  cml = "SELECT * FROM Product WHERE lower(product_name) LIKE '%" + product_input + "%'"
  result = g.conn.execute(text(cml))
  
  product = []
  price = []
  brand = []
  category = []
  seller = []
  pid = []
 
  for line in result:
    product.append(line['product_name']) 
    price.append(line['price'])
    brand.append(line['brand'])
    category.append(line['category_name'])
    seller.append(line['seller_id'])
    pid.append(line['product_id'])
  result.close()

  #find seller name  by seller_id 
  seller_name_list = []
  for item2 in seller:
    item2 = str(item2)
    cml2 = "SELECT * FROM Seller WHERE user_id = " + item2 + ""
    result2 = g.conn.execute(text(cml2))
    for line2 in result2:
      seller_name_list.append(line2['username'])
    result2.close()

  all_product = []
  for i in range(0,len(product)):
    one_product_row = []
    one_product_row.append(product[i])
    one_product_row.append(seller_name_list[i])
    one_product_row.append(category[i])
    one_product_row.append(brand[i])
    one_product_row.append(seller[i])
    one_product_row.append(price[i])
    one_product_row.append(pid[i])
    all_product.append(one_product_row)
    one_product_row = []

  # if do not login, change the username to 8888
  if un == None:
    un = 8888

  un = [un]
  context = dict(data = product, price = price, brand = brand, all_product=all_product, pid=pid, input = store_product_input, result_username = un)
  return render_template("search_product_login.html", **context)
  #if username != None: # have login
  #  un = [username]
  #  # stored data: product, price, brand, pid and all_product 
  # context = dict(data = product, price = price, brand = brand, all_product=all_product, pid=pid, input = store_product_input, result_username = un)
  #  return render_template("search_product_login.html", **context)
  #else: # just guest
  #  context = dict(data = product, price = price, brand = brand, all_product=all_product, pid=pid, input = store_product_input)
  #  return render_template("search_product.html", **context)

# 1. search country
@app.route('/searchCountry', methods=['POST'])
def searchCountry():
  country_input = request.form['country']
  cml = "SELECT * FROM brand WHERE country = '" + country_input + "'"
  result = g.conn.execute(text(cml))

  brand = []
  brand.append(country_input + ' : ')
  for line in result:
    brand.append(line['brand']) 
  result.close()

  context = dict(data = brand)
  return render_template("search_result.html", **context)

# 2. search a particular seller
@app.route('/searchSeller', methods=['POST'])
def searchSeller():
  seller_input = request.form['seller']
  cml = "SELECT * FROM Seller WHERE username = '" + seller_input + "'"
  result = g.conn.execute(text(cml))

  info = []
  info.append('Seller')
  #for line in result:
  #  brand.append(line['brand']) 
  #result.close()
  for line in result:
    info.append(line['username'])
    info.append(line['email'])
    info.append(line['create_date'])
  result.close()
  
  context = dict(data = info)
  return render_template("search_result.html", **context)

# 3. filters: brand country, band name, price range
@app.route('/filter', methods=['POST'])
def searchCountryBrand():
  searchedProductName = request.args.get('var')
  store_product_input = [searchedProductName]

  un = request.args.get('username')
  

  country_input = request.form['country'].lower()
  brand_input = request.form['brand'].lower()
  lowerprice_input = request.form['lowerprice']
  upperprice_input = request.form['upperprice']


  #x = (len(lowerprice_input) > 0) & (isinstance(lowerprice_input, basestring) == True)
  #y = (len(upperprice_input) > 0) & (isinstance(upperprice_input, basestring) == True) 
  #print x
  #print y
  #print 
  #if (x == True) | (y == True):
  #  if un == None:
  #    un = 8888
  #  un = [un]
  #  context = dict(result_username = un)
  #  return render_template("invalid_input.html", **context)

  #else:

  if (country_input != "") & (brand_input != "") & (lowerprice_input != "") & (upperprice_input != ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(B.country) = '" + country_input + "'" +  "AND lower(B.brand) = '" + brand_input + "'"  + " AND lower(P.product_name) LIKE '%" + searchedProductName + "%'" + "AND P.price >= " + lowerprice_input + "" + "AND P.price <= " + upperprice_input + ""
  elif (country_input != "") & (brand_input != "") & (lowerprice_input != "") & (upperprice_input == ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(B.country) = '" + country_input + "'" +  "AND lower(B.brand) = '" + brand_input + "'"  + " AND lower(P.product_name) LIKE '%" + searchedProductName + "%'" + "AND P.price >= " + lowerprice_input + ""    
  elif (country_input != "") & (brand_input != "") & (lowerprice_input == "") & (upperprice_input != ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(B.country) = '" + country_input + "'" +  "AND lower(B.brand) = '" + brand_input + "'"  + " AND lower(P.product_name) LIKE '%" + searchedProductName + "%'" + "AND P.price <= " + upperprice_input + ""
  elif (country_input != "") & (brand_input != "") & (lowerprice_input == "") & (upperprice_input == ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(B.country) = '" + country_input + "'" +  "AND lower(B.brand) = '" + brand_input + "'"  + " AND lower(P.product_name) LIKE '%" + searchedProductName + "%'" 
  elif (country_input != "") & (brand_input == "") & (lowerprice_input != "") & (upperprice_input != ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(B.country) = '" + country_input + "'" + " AND lower(P.product_name) LIKE '%" + searchedProductName + "%'" + "AND P.price >= " + lowerprice_input + "" + "AND P.price <= " + upperprice_input + ""
  elif (country_input != "") & (brand_input == "") & (lowerprice_input != "") & (upperprice_input == ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(B.country) = '" + country_input + "'" + " AND lower(P.product_name) LIKE '%" + searchedProductName + "%'" + "AND P.price >= " + lowerprice_input + "" 
  elif (country_input != "") & (brand_input == "") & (lowerprice_input == "") & (upperprice_input != ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(B.country) = '" + country_input + "'" + " AND lower(P.product_name) LIKE '%" + searchedProductName + "%'" + "AND P.price <= " + upperprice_input + ""
  elif (country_input != "") & (brand_input == "") & (lowerprice_input == "") & (upperprice_input == ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(B.country) = '" + country_input + "'" + " AND lower(P.product_name) LIKE '%" + searchedProductName + "%'" 
    ###
  elif (country_input == "") & (brand_input != "") & (lowerprice_input != "") & (upperprice_input != ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(B.brand) = '" + brand_input + "'"  + " AND lower(P.product_name) LIKE '%" + searchedProductName + "%'" + "AND P.price >= " + lowerprice_input + "" + "AND P.price <= " + upperprice_input + ""
  elif (country_input == "") & (brand_input != "") & (lowerprice_input != "") & (upperprice_input == ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(B.brand) = '" + brand_input + "'"  + " AND lower(P.product_name) LIKE '%" + searchedProductName + "%'" + "AND P.price >= " + lowerprice_input + ""    
  elif (country_input == "") & (brand_input != "") & (lowerprice_input == "") & (upperprice_input != ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(B.brand) = '" + brand_input + "'"  + " AND lower(P.product_name) LIKE '%" + searchedProductName + "%'" + "AND P.price <= " + upperprice_input + ""
  elif (country_input == "") & (brand_input != "") & (lowerprice_input == "") & (upperprice_input == ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(B.brand) = '" + brand_input + "'"  + " AND lower(P.product_name) LIKE '%" + searchedProductName + "%'" 
  elif (country_input == "") & (brand_input == "") & (lowerprice_input != "") & (upperprice_input != ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(P.product_name) LIKE '%" + searchedProductName + "%'" + "AND P.price >= " + lowerprice_input + "" + "AND P.price <= " + upperprice_input + ""
  elif (country_input == "") & (brand_input == "") & (lowerprice_input != "") & (upperprice_input == ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(P.product_name) LIKE '%" + searchedProductName + "%'" + "AND P.price >= " + lowerprice_input + "" 
  elif (country_input == "") & (brand_input == "") & (lowerprice_input == "") & (upperprice_input != ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(P.product_name) LIKE '%" + searchedProductName + "%'" + "AND P.price <= " + upperprice_input + ""
  else: #(country_input == "") & (brand_input == "") & (lowerprice_input == "") & (upperprice_input == ""):
    cml = "SELECT * FROM brand B, Product P WHERE B.brand = P.brand AND lower(P.product_name) LIKE '%" + searchedProductName + "%'"
    

  result = g.conn.execute(text(cml))
  
  product = []
  price = []
  brand = []
  category = []
  seller = []
  pid = []
 
  for line in result:
    product.append(line['product_name']) 
    price.append(line['price'])
    brand.append(line['brand'])
    category.append(line['category_name'])
    seller.append(line['seller_id'])
    pid.append(line['product_id'])
  result.close()
  
  

  #find seller name  by seller_id 
  seller_name_list = []
  for item2 in seller:
    item2 = str(item2)
    cml2 = "SELECT * FROM Seller WHERE user_id = " + item2 + ""
    result2 = g.conn.execute(text(cml2))
    for line2 in result2:
      seller_name_list.append(line2['username'])
    result2.close()

  all_product = []
  for i in range(0,len(product)):
    one_product_row = []
    one_product_row.append(product[i])
    one_product_row.append(seller_name_list[i])
    one_product_row.append(category[i])
    one_product_row.append(brand[i])
    one_product_row.append(seller[i])
    one_product_row.append(price[i])
    one_product_row.append(pid[i])
    all_product.append(one_product_row)
    one_product_row = []
  
  # if do not login, change the username to 8888
  if un == None:
    un = 8888

  un = [un]
  context = dict(data = product, price = price, brand = brand, all_product=all_product, pid=pid, input = store_product_input, result_username = un)
  
  return render_template("search_product_login.html", **context)

#4. create product pages
@app.route('/product')
def product_1000():
  var = request.args.get('pid')

  cml10 = "SELECT * FROM Product WHERE product_id = '" + var + "'"
  result = g.conn.execute(text(cml10))

  product = []
  price = []
  brand = []
  category = []
  seller = []
  pid = []
  #product.append(product + ' : ')
  for line in result:
    product.append(line['product_name']) 
    price.append(line['price'])
    brand.append(line['brand'])
    category.append(line['category_name'])
    seller.append(line['seller_id'])
    pid.append(line['product_id'])
  result.close()

  #find seller name  by seller_id 
  for item in seller:
    item = str(item)
    cml2 = "SELECT * FROM Seller WHERE user_id = " + item + ""
    result2 = g.conn.execute(text(cml2))
    seller_name = []
    for line2 in result2:
      seller_name.append(line2['username'])
    result2.close()

  #count number of orders
  for item3 in pid:
    item3 = str(item3)
    #cml3 = "SELECT COUNT(product_id) as count FROM Buy WHERE product_id = 1001 GROUP BY product_id" 
    cml3 = "SELECT SUM(quantity) AS quant FROM Buy WHERE product_id = '" + var + "'"
    result3 = g.conn.execute(text(cml3))
    order_num = []
    for line3 in result3:
      order_num.append(line3['quant'])
    result3.close()

  #count rating of a product
  for item4 in pid:
    item4 = str(item4)
    cml4 = "SELECT AVG(review_rating) AS rating FROM Review WHERE product_id = '" + var + "'"
    result4 = g.conn.execute(text(cml4))
    acc_rating = []
    review_id_lst = []
    for line4 in result4:
      acc_rating.append(line4['rating'])
      #acc_rating.append(line4['review_id'])
    result4.close()

  #if need to change order of columns, change here
  all_product = []
  for i in range(0,len(product)):
    one_product_row = []
    one_product_row.append(product[i])
    one_product_row.append(category[i])
    one_product_row.append(brand[i])
    one_product_row.append(seller[i])
    one_product_row.append(price[i])
    one_product_row.append(pid[i])
    one_product_row.append(seller_name[i])
    if order_num == [] or order_num ==[None]: #number of order = 0
      one_product_row.append(0)
    else:
      one_product_row.append(order_num[i])
    one_product_row.append(acc_rating[i])
    #one_product_row.append(review_id_lst[i])
    all_product.append(one_product_row)
    one_product_row = []


  context = dict(data = product, price = price, brand = brand, all_product=all_product, pid=pid)
  return render_template("product_page.html", **context)


# 5. create review page
@app.route('/review', methods=['POST', 'GET'])
def review():
  pid = request.args.get('review_pid')
  un = request.args.get('username')
  if un==None:
    un = 8888


  cml = "SELECT * FROM Review WHERE product_id = '" + pid + "'"
  result = g.conn.execute(text(cml))

  time = []
  rating = []
  rev_text = []
  for line in result:
    time.append(line['review_time'])
    rating.append(line['review_rating'])
    rev_text.append(line['review_text'])
  result.close()

  all_review = []
  for i in range(0,len(rating)):
    one_review_row = []
    one_review_row.append(time[i])
    one_review_row.append(rating[i])
    one_review_row.append(rev_text[i])
    all_review.append(one_review_row)
    one_review_row = []
  un = [un]
  context = dict(pid = pid, all_review=all_review, result_username=un)
  return render_template("review_page.html", **context)


# 5. create seller info page
@app.route('/seller_info')
def seller_info():
  sellerid = request.args.get('seller_id')
  un = request.args.get('username')
  if un==None:
    un = 8888
  print un


  un = [un]
  cml = "SELECT * FROM Seller WHERE user_id = '" + sellerid + "'"
  result = g.conn.execute(text(cml))
  
  seller_name = []
  email = []
  create_date = []
  for line in result:
    seller_name.append(line['username']) 
    email.append(line['email']) 
    create_date.append(line['create_date'])
  result.close()

  all_seller = []
  for i in range(0,len(seller_name)):
    one_seller_row = []
    one_seller_row.append(seller_name[i])
    one_seller_row.append(email[i])
    one_seller_row.append(create_date[i])
    all_seller.append(one_seller_row)
    one_seller_row = []
  
  #second query: calculate seller's rating
  sellerid2 = str(sellerid)
  cml2 = "SELECT * FROM (SELECT * FROM Product, Review WHERE Review.product_id=Product.product_id) AS t1 WHERE t1.seller_id="+ sellerid2 + "" 
  result2 = g.conn.execute(text(cml2))

  output=[]
  seller_rating = []
  for line in result2:
    output.append(line['review_rating'])
    output.append(line['seller_id'])
    output.append(line['product_id'])
    seller_rating.append(line['review_rating'])
  result2.close()

  if seller_rating ==[]:
    avg_rating = 'Opps, no rating information yet'
  elif seller_rating != []:
    avg_rating = sum(seller_rating)/len(seller_rating)

  context = dict(all_seller=all_seller, rating_data = output, avg_rating=avg_rating, result_username=un)
  return render_template("seller_info.html", **context)

# Newly add: 04/14
# 6. Product page with user login
@app.route('/searchProduct_login', methods=['POST'])
def searchProduct_login():
  product_input = request.form['product']
  cml = "SELECT * FROM Product WHERE product_name LIKE '%" + product_input + "%'"
  #cml = "SELECT * FROM Product WHERE category_name LIKE '%product_input%'"
  result = g.conn.execute(text(cml))

  product = []
  price = []
  brand = []
  category = []
  seller = []
  pid = []
  #product.append(product + ' : ')
  for line in result:
    product.append(line['product_name']) 
    price.append(line['price'])
    brand.append(line['brand'])
    category.append(line['category_name'])
    seller.append(line['seller_id'])
    pid.append(line['product_id'])
  result.close()
 

  #find seller name  by seller_id 
  seller_name_list = []
  for item2 in seller:
    item2 = str(item2)
    cml2 = "SELECT * FROM Seller WHERE user_id = " + item2 + ""
    result2 = g.conn.execute(text(cml2))
    for line2 in result2:
      seller_name_list.append(line2['username'])
    result2.close()
 

  all_product = []
  for i in range(0,len(product)):
    one_product_row = []
    one_product_row.append(product[i])
    one_product_row.append(seller_name_list[i])
    one_product_row.append(category[i])
    one_product_row.append(brand[i])
    one_product_row.append(seller[i])
    one_product_row.append(price[i])
    one_product_row.append(pid[i])
    all_product.append(one_product_row)
    one_product_row = []
 

  username = request.args.get('username')
  result_username = [username]


  context = dict(data = product, price = price, brand = brand, all_product=all_product, pid=pid, result_username=result_username)
  return render_template("search_product_login.html", **context)

#7. create product pages (after log in)
@app.route('/product_login')
def product_1ogin():
  var = request.args.get('pid')
  cml10 = "SELECT * FROM Product WHERE product_id = '" + var + "'"
  result = g.conn.execute(text(cml10))

  product = []
  price = []
  brand = []
  category = []
  seller = []
  pid = []
  #product.append(product + ' : ')
  for line in result:
    product.append(line['product_name']) 
    price.append(line['price'])
    brand.append(line['brand'])
    category.append(line['category_name'])
    seller.append(line['seller_id'])
    pid.append(line['product_id'])
  result.close()

  #find seller name  by seller_id 
  for item in seller:
    item = str(item)
    cml2 = "SELECT * FROM Seller WHERE user_id = " + item + ""
    result2 = g.conn.execute(text(cml2))
    seller_name = []
    for line2 in result2:
      seller_name.append(line2['username'])
    result2.close()

  #count number of orders
  for item3 in pid:
    item3 = str(item3)
    #cml3 = "SELECT COUNT(product_id) as count FROM Buy WHERE product_id = 1001 GROUP BY product_id" 
    cml3 = "SELECT SUM(quantity) AS quant FROM Buy WHERE product_id = '" + var + "'"
    result3 = g.conn.execute(text(cml3))
    order_num = []
    for line3 in result3:
      order_num.append(line3['quant'])
    result3.close()

  #count rating of a product
  for item4 in pid:
    item4 = str(item4)
    cml4 = "SELECT AVG(review_rating) AS rating FROM Review WHERE product_id = '" + var + "'"
    result4 = g.conn.execute(text(cml4))
    acc_rating = []
    review_id_lst = []
    for line4 in result4:
      acc_rating.append(line4['rating'])
      #acc_rating.append(line4['review_id'])
    result4.close()

    #if need to change order of columns, change here
  all_product = []
  for i in range(0,len(product)):
    one_product_row = []
    one_product_row.append(product[i])
    one_product_row.append(category[i])
    one_product_row.append(brand[i])
    one_product_row.append(seller[i])
    one_product_row.append(price[i])
    one_product_row.append(pid[i])
    one_product_row.append(seller_name[i])
    if order_num == [] or order_num ==[None]: #number of order = 0
      one_product_row.append(0)
    else:
      one_product_row.append(order_num[i])
    one_product_row.append(acc_rating[i])
    #one_product_row.append(review_id_lst[i])
    all_product.append(one_product_row)
    one_product_row = []
  
    username= request.args.get('username')
   
    result_username = [username]

    

  context = dict(data = product, price = price, brand = brand, all_product=all_product, pid=pid, result_username= result_username)
  return render_template("product_page_login.html", **context)


#8. create add favoriate page
@app.route('/add_favorite', methods=['POST', 'GET'])
def add_favorite():
  name = request.args.get('username')
  #print name

  #if (int(name) == 8888) | (name == None):
  if (str(name) == '8888') | (name == None):
    return render_template("cannotAddFav_needLogin.html")
  else:
    fav_id = request.args.get('favoriate_pid')
    #print name
    #print fav_id
    
    #get user_id by username
    cml = "SELECT * FROM Customer WHERE username = '" + name + "'"
    result = g.conn.execute(text(cml))
    userid = []
    for line in result:
      userid.append(line['user_id']) 
    result.close()
    print userid #userid: [0]

    #show table
    cmd3 = "SELECT * FROM Favoriate WHERE user_id = " + str(userid[0]) + ""
    result3 = g.conn.execute(text(cmd3))
    user_curr_fav =[]
    for line3 in result3:
      user_curr_fav.append(line3['product_id']) 
    result3.close()
    #print int(fav_id)
    #print user_curr_fav
    #print int(fav_id) in user_curr_fav

    name = [name]
    #if already exist in favorite page, not insert value to table
    if int(fav_id) in user_curr_fav:
      context1 = dict(name = name)
      return render_template("favorite_already_exist.html", **context1)
    else:
      #if not in favorite, add to favorite
      cmd2 = 'INSERT INTO Favoriate VALUES (:user_id, :product_id, NOW())'
      result2 = g.conn.execute(text(cmd2), user_id = userid[0], product_id = fav_id)
      context = dict(data = user_curr_fav, result_username = name)
      return render_template("favorite_afteradd.html", **context)

#9. remove a product from favorite, from favorite.html
@app.route('/remove')
def remove_from_fav():
  remove_pid = request.args.get('remove_pid')
  username_fav = request.args.get('username')
  #print remove_pid
  #print username_fav

  #get user_id by username
  cml = "SELECT * FROM Customer WHERE username = '" + username_fav + "'"
  result = g.conn.execute(text(cml))
  userid = []
  for line in result:
    userid.append(line['user_id']) 
  result.close()
  #print userid

  # remove a product from favorite by product id and user id
  cml2 = "DELETE FROM Favoriate WHERE user_id = " + str(userid[0]) + "and product_id = " + str(remove_pid) + ""
  result2 = g.conn.execute(text(cml2))
  
  #Find current favorite table
  #cml22 = "SELECT * FROM Favoriate "
  #result22 = g.conn.execute(text(cml22))
  #curr_uid = []
  #curr_pid = []
  #curr_date = []
  #for line2 in result22:
    #curr_uid.append(line2['user_id'])
    #curr_pid.append(line2['product_id'])
    #curr_date.append(line2['add_date'])
  #result22.close()
  
  #print curr_uid
  #print curr_pid
  #print curr_date

  #find this user's current favorite list
  cml3 = "SELECT * FROM Favoriate WHERE user_id = " + str(userid[0]) + ""
  result3 = g.conn.execute(text(cml3))
  fav_pid_lst = []
  date = []
  for line3 in result3:
    fav_pid_lst.append(line3['product_id'])
    date.append(line3['add_date'])
  result3.close()
  
  #print fav_pid_lst
  #rint date

  #match this user's product id with product name
  prod_name_lst = []
  for item in fav_pid_lst:
    cml4 = "SELECT * FROM Product WHERE product_id = " + str(item) + ""
    result4 = g.conn.execute(text(cml4))
    for line4 in result4:
      prod_name_lst.append(line4['product_name'])
    result4.close()
  
  #print prod_name_lst

  all_fav = []
  for i in range(0,len(prod_name_lst)):
    one_fav_row = []
    one_fav_row.append(fav_pid_lst[i])
    one_fav_row.append(prod_name_lst[i])
    one_fav_row.append(date[i])
    all_fav.append(one_fav_row)
    one_fav_row = []

  #print all_fav

  context = dict(un=username_fav, all_fav=all_fav)
  return render_template("favorite.html", **context)




@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


@app.route('/myhome')
def myhome():
  var = request.args.get('variable')
  
  result=[var]
  context = dict(data = result)
  return render_template("myhome.html", **context)

#newly add
@app.route('/myhome_login')
def myhome_login():
  var = request.args.get('variable')

  result=[var]
  context = dict(data = result)
  return render_template("myhome.html", **context)
  
@app.route('/account')
def account_detail():
  un = request.args.get('username')
  cml = "SELECT * FROM Customer WHERE username = '" + un + "'"
  result = g.conn.execute(text(cml))

  output = []
  for line in result:
    output.append(line['username']) 
    output.append(line['email']) 
    output.append(line['create_date'])
    output.append(line['date_of_birth'])
  result.close()

  context = dict(data = output)
  return render_template("account.html", **context)

#updated
@app.route('/favorite')
def favorite_detail():
  un = request.args.get('username')
  cml = "SELECT F.product_id, P.product_name, F.add_date FROM Customer C, Favoriate F, Product P WHERE F.user_id = C.user_id AND P.product_id = F.product_id AND C.username = '" + un + "'"
  result = g.conn.execute(text(cml))

  pid = []
  pname = []
  ptime = []
  for line in result:
    pid.append(line['product_id']) 
    pname.append(line['product_name']) 
    ptime.append(line['add_date'])
  result.close()

  all_fav = []
  for i in range(0,len(pid)):
    one_fav_row = []
    one_fav_row.append(pid[i])
    one_fav_row.append(pname[i])
    one_fav_row.append(ptime[i])
    all_fav.append(one_fav_row)
    one_fav_row = []

  context = dict(un = un, pid = pid, pname = pname, ptime = ptime, all_fav=all_fav)
  return render_template("favorite.html", **context)

#create order page, to order.html
@app.route('/order')
def order_detail():
  un = request.args.get('username')
  cml = "SELECT P.product_id, P.product_name, B.quantity, B.order_time, B.shipping_address FROM Customer C, Buy B, Product P WHERE B.buyer_id = C.user_id AND P.product_id = B.product_id AND C.username = '" + un + "'"
  result = g.conn.execute(text(cml))
 
  pname = []
  pquantity = []
  padd = []
  ptime = []
  pid=[]
  for line in result:
    pname.append(line['product_name']) 
    pquantity.append(line['quantity'])
    padd.append(line['shipping_address'])
    ptime.append(line['order_time'])
    pid.append(line['product_id'])
  result.close()

  all_order = []
  for i in range(0,len(pname)):
    one_order_row=[]
    one_order_row.append(pname[i])
    one_order_row.append(pquantity[i])
    one_order_row.append(ptime[i])
    one_order_row.append(padd[i])
    all_order.append(one_order_row)
    one_order_row = []

  context = dict(pname = pname, pquantity = pquantity, padd = padd, all_order=all_order,pid=pid[0],un=un)
  return render_template("order.html", **context)

#write a review page, from order.html
@app.route('/order_review_write', methods=['POST','GET'])
def order_review_write():
  un = request.args.get('username')
  pid = request.args.get('pid')
  context = dict(username=un, pid=pid)
  return render_template("write_review.html", **context)

#write a review page, from order.html
@app.route('/order_review', methods=['POST','GET'])
def order_review():
  un = request.args.get('username')
  pid = request.args.get('pid')
  rating = request.form['rating']
  review = request.form['review']
  
  if float(rating)>5 or float(rating)<0:
    context = dict(result_username  = [un])
    return render_template("invalid_rating.html", **context)

  #select last line's review id
  cml = "SELECT * FROM Review ORDER BY review_id DESC LIMIT 1"
  result = g.conn.execute(text(cml))
  id_lst = []
  for line in result:
    id_lst.append(line['review_id'])
  result.close()

  #get user_id by username
  cml2 = "SELECT * FROM Customer WHERE username = '" + un + "'"
  result2 = g.conn.execute(text(cml2))
  userid = []
  for line2 in result2:
    userid.append(line2['user_id']) 
  result2.close()

  #insert value
  new_review_id = int(id_lst[0])+1
  cmd2 = 'INSERT INTO Review VALUES (:review_id, :product_id, :user_id, :review_rating, :review_text, NOW())'
  result2 = g.conn.execute(text(cmd2), review_id = new_review_id, product_id=pid,
    user_id=userid[0], review_rating = rating, review_text=review)
  
  #get this user's all reviews
  cml2 = "SELECT * FROM Review WHERE user_id = " + str(userid[0]) + ""
  result3 = g.conn.execute(text(cml2))
  prod_id = []
  review_rating = []
  review_text = []
  review_time = []
  for line3 in result3:
    prod_id.append(line3['product_id'])
    review_rating.append(line3['review_rating']) 
    review_text.append(line3['review_text'])
    review_time.append(line3['review_time'])
  result3.close()

  all_rev_prod = []
  for i in range(0,len(prod_id)):
    one_rev_prod = []
    one_rev_prod.append(prod_id[i])
    one_rev_prod.append(review_rating[i])
    one_rev_prod.append(review_text[i])
    one_rev_prod.append(review_time[i])
    all_rev_prod.append(one_rev_prod)
    one_rev_prod = []
    
  context = dict(all_rev_prod=all_rev_prod, un=un)
  return render_template("write_review_page.html", **context)

#all review, from write_review.html
@app.route('/allreview', methods=['POST','GET'])
def allreview():
  un = request.args.get('un')
  
  #get user_id by username
  cml12 = "SELECT * FROM Customer WHERE username = '" + un + "'"
  result2 = g.conn.execute(text(cml12))
  userid = []
  for line2 in result2:
    userid.append(line2['user_id']) 
  result2.close()

  #get this user's all reviews
  cml2 = "SELECT * FROM Review WHERE user_id = " + str(userid[0]) + ""
  result3 = g.conn.execute(text(cml2))
  prod_id = []
  review_rating = []
  review_text = []
  review_time = []
  for line3 in result3:
    prod_id.append(line3['product_id'])
    review_rating.append(line3['review_rating']) 
    review_text.append(line3['review_text'])
    review_time.append(line3['review_time'])
  result3.close()

  all_rev_prod = []
  for i in range(0,len(prod_id)):
    one_rev_prod = []
    one_rev_prod.append(prod_id[i])
    one_rev_prod.append(review_rating[i])
    one_rev_prod.append(review_text[i])
    one_rev_prod.append(review_time[i])
    all_rev_prod.append(one_rev_prod)
    one_rev_prod = []
    
  context = dict(all_rev_prod=all_rev_prod, un=un)
  return render_template("write_review_page.html", **context)

#create brand page, from search_product_login.html, to brand_page.html
@app.route('/brand_info')
def brand_info():
  brand = request.args.get('brand')
  un = request.args.get('username')
  cml = "SELECT * FROM Product WHERE brand = '" + brand + "'"
  result = g.conn.execute(text(cml))
  
  product = []
  price = []
  brand = []
  category = []
  seller = []
  pid = []
  for line in result:
    product.append(line['product_name']) 
    price.append(line['price'])
    brand.append(line['brand'])
    category.append(line['category_name'])
    seller.append(line['seller_id'])
    pid.append(line['product_id'])
  result.close()

  #find seller name  by seller_id 
  seller_name_list = []
  for item2 in seller:
    item2 = str(item2)
    cml2 = "SELECT * FROM Seller WHERE user_id = " + item2 + ""
    result2 = g.conn.execute(text(cml2))
    for line2 in result2:
      seller_name_list.append(line2['username'])
    result2.close()

  all_product = []
  for i in range(0,len(product)):
    one_product_row = []
    one_product_row.append(product[i])
    one_product_row.append(category[i])
    one_product_row.append(brand[i])
    one_product_row.append(seller_name_list[i])
    one_product_row.append(price[i])
    one_product_row.append(pid[i])
    all_product.append(one_product_row)
    one_product_row = []

   #if do not login, change the username to 8888
  if un == None:
    un = 8888

  un = [un]
  context = dict(data = product, price = price, brand = brand[0], all_product=all_product, pid=pid[0], result_username = un)
  return render_template("brand_page.html", **context)

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8200, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
