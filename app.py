from ast import iter_child_nodes
from operator import methodcaller
from pickle import TRUE
from flask import Flask,render_template, request,session, redirect, url_for, flash, send_file
import pymysql.cursors
from datetime import datetime
import pytz
from fpdf import FPDF 
import os
import qrcode
import requests

app = Flask(__name__)

# url = "https://www.fast2sms.com/dev/bulkV2"
app.secret_key = "abdhghsbghddvbnbds"

con = pymysql.Connect(host="127.0.0.1",port=3307,user="root",passwd="",db="template")
con2 = pymysql.Connect(host="127.0.0.1",port=3307,user="root",passwd="",db="setupfood")
cur = con.cursor()
cur2 = con2.cursor()


# @app.route('<name>')
# def client_website():

IST = pytz.timezone("Asia/Kolkata")


    

@app.route('/')
def index():
    return render_template('index.html')

    
name = ""
type_of_service = ""

@app.route('/login', methods=["GET","POST"])
def login():
    global name
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        check_email = "SELECT * FROM users WHERE email = '"+email+"'"
        con.ping(reconnect = True)
        cur.execute(check_email)
        get_one_email = cur.fetchone()
        name = get_one_email[2]
        
        if (not get_one_email):
            flash("You entered wrong email address")
            return redirect(url_for('login'))
        elif(get_one_email[3]!=password):
            flash("Wrong Password")
            return redirect(url_for('login'))
        else:
            session['loggedin'] = True 
            session['myuserid'] = get_one_email[0]
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# sql = "CREATE TABLE orders(id INT AUTO_INCREMENT, resta_id INT, customer_name VARCHAR(100), mobile_number VARCHAR(12), table_no VARCHAR(10), order_items LONGTEXT, quantity LONGTEXT, price LONGTEXT, total_price LONGTEXT, order_time TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP, type VARCHAR(30), takeaway_time VARCHAR(30) DEFAULT '-', PRIMARY KEY(id), FOREIGN KEY(resta_id) REFERENCES users(user_id) ON DELETE CASCADE)"
# cur.execute(sql)
# con.commit()


# contact table for restaurants 

# sql = "CREATE TABLE contacts(id INT AUTO_INCREMENT, resta_id INT, name VARCHAR(100), mobile_number VARCHAR(12), message VARCHAR(600), PRIMARY KEY(id), FOREIGN KEY(resta_id) REFERENCES users(user_id) ON DELETE CASCADE)"
# cur.execute(sql)
# con.commit()

# sql = "CREATE TABLE final_orders (id INT AUTO_INCREMENT, resta_id INT, customer_name VARCHAR(100), mobile_number VARCHAR(12), table_no VARCHAR(10), type VARCHAR(30), order_items LONGTEXT, quantity LONGTEXT, price LONGTEXT, total_price LONGTEXT, order_time TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,  PRIMARY KEY(id), FOREIGN KEY(resta_id) REFERENCES users(user_id) ON DELETE CASCADE)"
# cur.execute(sql)
# con.commit()

@app.route('/90167544566352717157signup', methods=["GET", "POST"])
def signup():
    # this code is for creating the table in template database. Execute it only once 
    # sql = "CREATE TABLE users (user_id INT AUTO_INCREMENT, email VARCHAR(50), restaurant_name VARCHAR(60), password VARCHAR(30), PRIMARY KEY(user_id))"
    # cur.execute(sql)
    # con.commit()
    if request.method == "POST":
        email = request.form["email"]
        check_email = "SELECT email FROM users WHERE email = '"+email+"'"
        con.ping(reconnect = True)
        cur.execute(check_email)
        first_email = cur.fetchone()
        global name
        if(not first_email):
            restaurant_name = request.form["rname"]
            password = request.form["password"]
            sql = "INSERT INTO users(email, restaurant_name, password) VALUES (%s,%s,%s)"
            val = (email, restaurant_name, password)
            con.ping(reconnect = True)
            cur.execute(sql,val)
            con.commit()
            name = restaurant_name
            sql2 = "SELECT user_id FROM users WHERE email = '"+email+"'"
            con.ping(reconnect = True)
            cur.execute(sql2)
            myid = cur.fetchone()
            # session['id'] = myid[0]
            session['loggedin'] = True
            session['myuserid'] = myid[0]
            # print(session['id'])
            return redirect(url_for('details'))
        else:
            flash("The email is already in use! Try using another")
            return redirect(url_for('signup'))
    return render_template('signup.html')

@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template("home.html")
    else:
        return redirect(url_for('login'))


@app.route('/template')
def template():
    return render_template('landingpage.html')

@app.route('/book')
def book():
    return render_template('book.html')

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        resta_id = str(session['myuserid']) 

        date_time = datetime.now(IST)
        date = date_time.strftime("%x")

        sql = "SELECT COUNT(id) FROM final_orders WHERE resta_id = '"+resta_id+"' and order_date = '"+date+"'"
        con.ping(reconnect=True)
        cur.execute(sql)
        orders_today = cur.fetchone()[0]
        

        sql2 = "SELECT price_sum FROM final_orders WHERE resta_id = '"+resta_id+"' and order_date = '"+date+"'"
        con.ping(reconnect = True)
        cur.execute(sql2)
        payments_toady = cur.fetchall()
        

        total_today_amount = 0
     
        for i in range(len(payments_toady)):
            total_today_amount += int(payments_toady[i][0])


        today = datetime.now(IST)
        month_name = today.strftime("%B")

        sql3 = "SELECT COUNT(id) from final_orders where monthname(STR_TO_DATE(order_date, '%m/%d/%Y')) = '"+ month_name +"' and resta_id = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql3)
        total_orders_this_month = cur.fetchone()[0]

        sql4 = "SELECT price_sum from final_orders WHERE monthname(STR_TO_DATE(order_date, '%m/%d/%Y')) = '"+month_name+"' and resta_id = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql4)
        payments_month = cur.fetchall()

        total_payment = 0
     
        for i in range(len(payments_month)):
            total_payment += int(payments_month[i][0])
        

        # metrics 

        sql5 = "SELECT COUNT(id) FROM final_orders WHERE resta_id = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql5)
        overall_orders = cur.fetchone()[0]

        sql6 = "SELECT COUNT(DISTINCT mobile_number) FROM final_orders WHERE resta_id = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql6)
        total_users = cur.fetchone()[0]

        sql7 = "SELECT price_sum FROM final_orders WHERE resta_id = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql7)
        all_price = cur.fetchall()

        all_price_sum = 0
        for i in range(len(all_price)):
            all_price_sum += all_price[i][0]

        sql8 = "SELECT mobile_number, COUNT(id), SUM(price_sum) FROM final_orders WHERE resta_id = '"+resta_id+"' GROUP BY mobile_number HAVING COUNT(mobile_number) > 1"
        con.ping(reconnect = True)
        cur.execute(sql8)
        all_repeating_numbers = cur.fetchall()
       
        
        all_repeating_client = len(all_repeating_numbers)

        times_orders = 0
        total_amount = 0

        for i in range(len(all_repeating_numbers)):
            times_orders += int(all_repeating_numbers[i][1])
            total_amount += int(all_repeating_numbers[i][2])

        

        sql = "SELECT restaurant_name FROM users WHERE user_id = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        name = cur.fetchone()[0]

       
        return render_template('dashboard.html', resta_name = name, orders_today=orders_today, total_today_amount = total_today_amount, total_orders_this_month = total_orders_this_month, payment_this_month = total_payment, date=date, overall_orders=overall_orders, total_users = total_users, all_price_sum= all_price_sum, repeat_user = all_repeating_client, times_order=times_orders, total_amount=total_amount)
    else:
        return redirect(url_for('login'))   



@app.route('/menu')
def menu():
    return render_template('menu.html')

# @app.route("/about")
# def about():
#     return render_template('aboutus.html')

# @app.route("/blog")
# def blog():
#     return render_template('blog.html')

# @app.route("/career", methods=["GET",'POST'])
# def carrer():
#     return render_template('careers.html')



@app.route("/partner", methods=["GET","POST"])
def partner():
    # setupfood contact 
    # sql = "CREATE TABLE contact (id INT AUTO_INCREMENT, name VARCHAR(60), phone VARCHAR(13), message VARCHAR(1000), PRIMARY KEY(id))"
    # cur2.execute(sql)
    # con2.commit()
    if request.method=="POST":
        name = request.form["name"]
        phone = request.form["phone"]
        msg = request.form["msg"]
        sql = "INSERT INTO contact(name, phone, message) VALUES (%s, %s, %s)"
        val = (name, phone, msg)
        cur2.execute(sql, val)
        con2.commit()
        return redirect(url_for('partner'))
    return render_template('partnerWithUs.html')

@app.route("/demo", methods=["GET","POST"])
def demo():
    # sql = "CREATE TABLE demo (id INT AUTO_INCREMENT, phone VARCHAR(13), PRIMARY KEY(id))"
    # cur2.execute(sql)
    # con2.commit()
    if request.method == "POST":
        number = request.form["mobile_no"]

        sql = "INSERT INTO demo(phone) VALUES(%s)"
        val = (number)
        con2.ping(reconnect=True)
        cur2.execute(sql,val)
        con2.commit()

        return redirect(url_for('index'))
    return render_template('index.html')



def saveFormPicture(picture_file , restaurant_name , i):
    picture = restaurant_name + str(i) + picture_file.filename
    picture_path = os.path.join(app.root_path , 'static/formImage/' , picture)
    picture_file.save(picture_path)
    return picture

@app.route("/filltheform", methods=["GET","POST"])
def details():
    # sql = "CREATE TABLE tempdetails (temp_id INT AUTO_INCREMENT, userid INT, resta_name VARCHAR(40), tagline VARCHAR(80), opening DATETIME, closing DATETIME, about VARCHAR(300), logo LONGBLOB, banner LONGBLOB, img1 LONGBLOB, img2 LONGBLOB, img3 LONGBLOB, img4 LONGBLOB, PRIMARY KEY(temp_id), FOREIGN KEY(userid) REFERENCES users(user_id) ON DELETE CASCADE)"

    # cur.execute(sql)
    # con.commit()

    # sql = "ALTER TABLE tempdetails MODIFY closing VARCHAR(10)"
    # cur.execute(sql)
    # con.commit()

    # sql = "ALTER TABLE tempdetails MODIFY opening VARCHAR(10)"
    # cur.execute(sql)
    # con.commit()

    # sql = "ALTER TABLE tempdetails MODIFY banner VARCHAR(100)"
    # cur.execute(sql)
    # con.commit()

    # sql = "ALTER TABLE tempdetails MODIFY logo VARCHAR(100)"
    # cur.execute(sql)
    # con.commit()

    # sql = "ALTER TABLE tempdetails MODIFY img1 VARCHAR(100)"
    # cur.execute(sql)
    # con.commit()

    # sql = "ALTER TABLE tempdetails MODIFY img2 VARCHAR(100)"
    # cur.execute(sql)
    # con.commit()
    
    # sql = "ALTER TABLE tempdetails MODIFY img3 VARCHAR(100)"
    # cur.execute(sql)
    # con.commit()

    # sql = "ALTER TABLE tempdetails MODIFY img4 VARCHAR(100)"
    # cur.execute(sql)
    # con.commit()

    
    if 'loggedin' in session:
        if request.method=="POST":
            resta_name = request.form["rname"]
            tagline = request.form["tagline"]
            opening_time = request.form["ohour"]
            closing_time = request.form["chour"]
            about = request.form["about"]
            logo = request.files["logo"]
            gst = request.form["gst"]

            logoPath = saveFormPicture(logo , resta_name , 1)
            banner = request.files["banner"]
            bannerPath = saveFormPicture(banner , resta_name ,2)
            img1 = request.files["img1"]
            img1Path = saveFormPicture(img1 , resta_name ,3)
            img2 = request.files["img2"]
            img2Path = saveFormPicture(img2 , resta_name ,4)
            img3 = request.files["img3"]
            img3Path = saveFormPicture(img3 , resta_name ,5)
            img4 = request.files["img4"]
            img4Path = saveFormPicture(img4 , resta_name , 6)

            sql1 = "SELECT * FROM users WHERE restaurant_name = '"+resta_name+"'"
            con.ping(reconnect = True)
            cur.execute(sql1)
            myuser_id = cur.fetchone()
            myuser = myuser_id[0]
            

            sql = "INSERT INTO tempdetails(userid, resta_name, tagline, opening, closing, about, logo, banner, img1, img2, img3, img4, gst) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s)"
            val = (myuser, resta_name, tagline, opening_time, closing_time, about, logoPath, bannerPath, img1Path, img2Path, img3Path, img4Path,gst)
            con.ping(reconnect = True)
            cur.execute(sql, val)
            con.commit()
            
            sql = "SELECT * FROM tempdetails WHERE resta_name = '"+resta_name+"'"
            con.ping(reconnect = True)
            cur.execute(sql)
            user_id = cur.fetchone()

            qr = qrcode.QRCode(
                version = 1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=50,
                border=2
            )

            qr.add_data(f"https://setupfood.com/{resta_name}/dine-in/menu")
            qr.make(fit=True)
            img = qr.make_image(fit_color = "black", back_color="white")
            img.save(f"./static/QRcode/Dine-in/{resta_name}.png")


                # qr code Take Away
            qr2 = qrcode.QRCode(
                    version = 1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=50,
                    border=2
            )

            qr2.add_data(f"https://setupfood.com/{resta_name}/takeaway/menu")
            qr2.make(fit=True)
            img = qr2.make_image(fit_color = "black", back_color="white")
            img.save(f"./static/QRcode/Takeaway/{resta_name}.png")
            
            session['myuserid'] = user_id[1]

            return redirect(url_for('contactdetails'))
        else:
            return render_template('form.html')
    else:
        return redirect(url_for('login'))



@app.route("/contactdetails", methods=["GET","POST"])
def contactdetails():
    # sql = "CREATE TABLE tempcontact (contact_id INT AUTO_INCREMENT, contact_user_id INT, address VARCHAR(100), mobile VARCHAR(12), email VARCHAR(50), map_link VARCHAR(100), instagram_link VARCHAR(50), facebook_link VARCHAR(50), twitter_link VARCHAR(50) DEFAULT 'none', wp_link VARCHAR(50) DEFAULT 'none', PRIMARY KEY(contact_id), FOREIGN KEY(contact_user_id) REFERENCES tempdetails(userid) ON DELETE CASCADE)"
    # cur.execute(sql)
    # con.commit()
    if 'myuserid' in session:
        if request.method=="POST":
            address = request.form['address']
            phone = request.form['phone']
            email= request.form['email']
            google_map = request.form['googlemap']
            instalink = request.form['instalink']
            fblink = request.form['fblink']
            twitterlink = request.form['twitterlink']
            wplink = request.form['wplink']

            mynewid = session['myuserid']
            
            sql = "INSERT INTO tempcontact(contact_user_id, address, mobile, email, map_link, instagram_link, facebook_link, twitter_link, wp_link) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (mynewid, address, phone, email, google_map, instalink, fblink, twitterlink, wplink)
            con.ping(reconnect = True)
            cur.execute(sql, val)
            con.commit()
            return redirect(url_for('typesOfDishes'))
    else:
        return redirect(url_for('details'))
    return render_template('contactform.html')

# create table for the dishesh 

# sql = "CREATE TABLE dishtype (id INT AUTO_INCREMENT, resta_id INT, dish VARCHAR(50), PRIMARY KEY(id), FOREIGN KEY(resta_id) REFERENCES tempcontact(contact_user_id) ON DELETE CASCADE)"
# cur.execute(sql)
# con.commit()

@app.route("/typesofdishes", methods=["GET","POST"])
def typesOfDishes():
    if 'myuserid' in session:
        if request.method == "POST":
            dishType = request.form["dishType"]
            
            resta_id = session['myuserid']
           
            sql = "INSERT INTO dishtype(resta_id, dish) VALUES(%s, %s)"
            val = (resta_id, dishType)
            con.ping(reconnect = True)
            cur.execute(sql, val)
            
            con.commit()

            return redirect(url_for('typesOfDishes'))

    return render_template("TypesofDishes.html")
    # return redirect(url_for('menudetails'))

# for cretaing the menuitems table that stores the data of the dish types 

# sql = "CREATE TABLE menuitems (id INT AUTO_INCREMENT, dish_id INT, items LONGTEXT, price LONGTEXT, description LONGTEXT, PRIMARY KEY(id), FOREIGN KEY(dish_id) REFERENCES dishtype(id) ON DELETE CASCADE)"
# cur.execute(sql)
# con.commit()




@app.route('/completedOrders', methods=["GET", "POST"])
def completedOrders():
    if 'myuserid' in session:
        resta_id = str(session['myuserid'])  

        sql = "SELECT restaurant_name FROM users WHERE user_id = '"+str(session['myuserid'])+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        name = cur.fetchone()[0]

        date_time = datetime.now(IST)
        date = date_time.strftime("%x")

        sql3 = "SELECT * from final_orders where  order_date = '"+date+"' and  resta_id = '"+resta_id+"' ORDER BY `id` DESC"
        con.ping(reconnect = True)
        cur.execute(sql3)
        my_data = cur.fetchall()
      
        length = len(my_data)

        count = 0

        order_month = "Today's Completed"
        if request.method == "POST":
            order_month = request.form['months']
           
            sql = "SELECT * from final_orders where monthname(STR_TO_DATE(order_date, '%m/%d/%Y')) = '"+ order_month +"' and resta_id = '"+resta_id+"' ORDER BY `id` DESC"
            con.ping(reconnect = True)
            cur.execute(sql)
            new_data = cur.fetchall()
            length = len(new_data)
            count = 0
            return render_template('completedOrders.html', name=name,length=length, date=date , my_data = new_data , count = count , order_month = order_month)

        return render_template('completedOrders.html', name=name,length=length, date=date , my_data = my_data , count = count , order_month = order_month)

    return redirect(url_for('login'))


@app.route('/storeUpdate' , methods=["GET" , "POST"])
def storeUpdateMenu():
    if request.method == "POST":
        dish_id = request.form['dish_id']
        items = request.form['items_list']
        prices = request.form['price_list']
        description = request.form['descr_list']
        
        if items == '':
            sql = "DELETE from dishtype where id='"+dish_id+"'"
            con.ping(reconnect = True)
            cur.execute(sql)
            con.commit()

        else:
            sql = "UPDATE menuitems SET items='"+items+"',price='"+prices+"',description='"+description+"' WHERE dish_id='"+dish_id+"'"
            con.ping(reconnect = True)
            cur.execute(sql)
            con.commit()
        return redirect(url_for('updateMenu'))
    return redirect(url_for('updateMenu'))






@app.route('/updateMenu' , methods=["POST" , "GET"])
def updateMenu():
    if 'myuserid' in session:
        resta_id = str(session['myuserid'])       

        sql2 = "SELECT restaurant_name FROM users WHERE user_id = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql2)
        name = cur.fetchone()[0]

        sql3 = "SELECT id , dish from dishtype where resta_id = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql3)
        dishes = cur.fetchall()
        
        date_time = datetime.now(IST)
        date = date_time.strftime("%x")

        dish_items = []

        dish_name = []
        dish_price = []
        dish_desc = []
        count = 0
        mylen = 0
        if request.method == "POST":
            dish_id = request.form['dishtype']
           
            # sql4 = "SELECT items from menuitems where dish_id = '"+dish_id+"'"
            # cur.execute(sql4)
            # menu = cur.fetchall()
            # print(menu)

            sql4 = "SELECT * FROM menuitems WHERE dish_id = '"+dish_id+"'"
            con.ping(reconnect = True)
            cur.execute(sql4)
            dish_items.append(cur.fetchall()[0])

            for i in range(0, len(dish_items)):
                dish_name.append(dish_items[i][2].split(","))
                dish_price.append(dish_items[i][3].split(","))
                dish_desc.append(dish_items[i][4].split(","))

            # for j in range(0,len(dish_name)):
            #     dish_name = dish_name[j].pop()


            mylen = len(dish_name[0])
           



            return render_template('updateMenu.html' , name=name , date=date , dishes=dishes , mylen=mylen , dish_name=dish_name , dish_price=dish_price, dish_desc=dish_desc , count=count , dish_id = dish_id )
        return render_template('updateMenu.html' , name=name , date=date , dishes=dishes, mylen=mylen , dish_name=dish_name , dish_price=dish_price, dish_desc=dish_desc , count=count)
    return render_template('updateMenu.html')

@app.route('/storeUpdate' , methods=["GET" , "POST"])
def storeUpdate():
    if request.method == "POST":
        dish_id = request.form['dish_id']
        items = request.form['items_list']
        prices = request.form['price_list']
        description = request.form['descr_list']

        sql2 = "SELECT items FROM menuitems WHERE dish_id = '"+dish_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql2)
        dish_items = cur.fetchone()[0]
      

        if dish_items == " ":
            sql = "DELETE FROM menuitems WHERE dish_id = '"+dish_id+"'"
            con.ping(reconnect = True)
            cur.execute(sql)
            con.commit()
        else:
            sql = "UPDATE menuitems SET items='"+items+"',price='"+prices+"',description='"+description+"' WHERE dish_id='"+dish_id+"'"
            con.ping(reconnect = True)
            cur.execute(sql)
            con.commit()
        return redirect(url_for('updateMenu'))
    return redirect(url_for('updateMenu'))


@app.route('/addnewDishItem' , methods=["GET" , "POST"])
def addnewDishItem():
    if request.method == "POST":
        dish_id = request.form['dishtype']
        new_item_name = request.form['ItemName']
        new_item_price = request.form['ItemPrice']
        new_item_descr = request.form['ItemDesc']
        # print(dish_id)
        # print(new_item_name)
        # print(new_item_price)
        # print(new_item_descr)
        sql = "SELECT items , price , description from menuitems where dish_id='"+dish_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        # print(cur.fetchone())
        all_data = cur.fetchone()
   
        if all_data != None:
            all_items = all_data[0]
            all_prices = all_data[1]
            all_descr = all_data[2]

       

            all_items_array = all_items.split(',')
      
            all_items_array.append(new_item_name)

            all_items = ",".join(all_items_array)
            
       

            all_prices_array = all_prices.split(',')
            all_prices_array.append(new_item_price)
            all_prices = ",".join(all_prices_array)

        
            
            all_descr_array = all_descr.split(',')
            all_descr_array.append(new_item_descr)
            all_descr = ",".join(all_descr_array)

            sql = "UPDATE menuitems SET items='"+all_items+"',price='"+all_prices+"',description='"+all_descr+"' WHERE dish_id='"+dish_id+"'"
            con.ping(reconnect = True)
            cur.execute(sql)
            con.commit()
            return redirect(url_for('updateMenu'))

        else :
            sql2 = "INSERT into menuitems (dish_id , items , price , description) VALUES(%s,%s,%s,%s)"
            value = (dish_id , new_item_name , new_item_price , new_item_descr)
            con.ping(reconnect = True)
            cur.execute(sql2 , value)
            con.commit()
            return redirect(url_for('updateMenu'))
    return redirect(url_for('updateMenu'))


@app.route('/editDishItem' , methods=["GET" , "POST"])
def editDishItem():
    if 'myuserid' in session:
        resta_id = str(session['myuserid'])
        if request.method == 'POST':
            dish_id = request.form['dish_id']
            title_index = request.form['title_index']
            updated_item = request.form['editItem']
            updated_price = request.form['editPrice']
            updated_description = request.form['editDescr']
        

            sql = "SELECT items , price , description from menuitems where dish_id='"+dish_id+"'"
            con.ping(reconnect = True)
            cur.execute(sql)
            # print(cur.fetchone())
            data = cur.fetchone()
            items = data[0]
            price = data[1]
            descr = data[2]

            items_array = items.split(',')
           
            
            price_array = price.split(',')
      

            descr_array = descr.split(',')
         


            items_array[int(title_index)] = updated_item
            price_array[int(title_index)] = updated_price
            descr_array[int(title_index)] = updated_description

        

            
            all_item = ",".join(items_array)
            all_price = ",".join(price_array)
            all_descr = ",".join(descr_array)

            sql = "UPDATE menuitems SET items='"+all_item+"',price='"+all_price+"',description='"+all_descr+"' WHERE dish_id='"+dish_id+"'"
            con.ping(reconnect = True)
            cur.execute(sql)
            con.commit()
            return redirect(url_for('updateMenu'))


    return redirect(url_for('updateMenu'))


@app.route('/updateDish' , methods=["GET" , "POST"])
def updateDish():
    if 'myuserid' in session:
        resta_id = str(session['myuserid'])       
        if request.method == "POST":
            dish_id = request.form['dishtype']
            updated_name = request.form['updatedItem']
            
            sql = "UPDATE dishtype SET dish='"+updated_name+"' where id='"+dish_id+"'"
            con.ping(reconnect = True)
            cur.execute(sql)
            con.commit()
            return redirect(url_for('updateMenu'))
    return redirect(url_for('updateMenu'))

@app.route('/deleteDish' , methods=["GET" , "POST"])
def deleteDish():
    if 'myuserid' in session:
        resta_id = str(session['myuserid'])
        if request.method == 'POST' :
           dish_id  = request.form['dishtype']
          
           sql = "DELETE from menuitems where dish_id='"+dish_id+"'"
           con.ping(reconnect = True)
           cur.execute(sql)
           con.commit()
           sql1 = "DELETE from dishtype where id='"+dish_id+"'"
           con.ping(reconnect = True)
           cur.execute(sql1)
           con.commit()
           return redirect(url_for('updateMenu'))
    return redirect(url_for('updateMenu'))

@app.route('/addnewDish' , methods=["GET" , "POST"])
def addnewDish():
    if 'myuserid' in session:
        resta_id = str(session['myuserid'])
        if request.method == 'POST':
            new_item = request.form['newItem']
        
            sql = "INSERT INTO dishtype(resta_id, dish) VALUES(%s, %s)"
            val = (resta_id, new_item)
            con.ping(reconnect = True)
            cur.execute(sql, val)
            
            con.commit()
            return redirect(url_for('updateMenu'))
    return redirect(url_for('updateMenu'))

@app.route('/orders', methods=["GET", "POST"])
def booktabledetails():
    if 'myuserid' in session:
        resta_id = str(session['myuserid'])

        sql = "SELECT restaurant_name FROM users WHERE user_id = '"+str(session['myuserid'])+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        name = cur.fetchone()[0]

        date_time = datetime.now(IST)
        date = date_time.strftime("%x")
        

        sql3 = "SELECT * from orders where order_date = '"+date+"' and resta_id = '"+resta_id+"' and status = '"+"Accepted"+"' ORDER BY `id` DESC"
        con.ping(reconnect = True)
        cur.execute(sql3)
        my_data = cur.fetchall()
      
        length = len(my_data)

        count = 0
        global hidden

        if request.method == "POST":
            order_id = request.form['orderId']

            sql = "UPDATE orders SET status = 'Confirmed' WHERE id = '"+order_id+"'"
            con.ping(reconnect = True)
            cur.execute(sql)
            con.commit()
         

        return render_template('booktabledetails.html', name=name,length=length, date=date , my_data = my_data , count = count)

    return redirect(url_for('login')) 

@app.route("/generate-kot", methods=["GET","POST"])
def generateKot():
    if request.method == "POST":
        order_id = request.form['orderId'] #order number
        sql = "SELECT * FROM orders WHERE id = '"+order_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        
        order_details = cur.fetchone()

        resta_id = order_details[1]

        sql2 = "SELECT restaurant_name FROM users WHERE user_id = '"+str(resta_id)+"'"
        con.ping(reconnect = True)
        cur.execute(sql2)

        resta_name = cur.fetchone()[0]
        order_time = order_details[10]
        table_no = order_details[4]
        customer_name = order_details[2]
        customer_number = order_details[3]
        order_date = order_details[9]
        service_type1 = order_details[12]

        takeaway_time = order_details[13]

        list_item = order_details[5].split(",")
        list_qty = order_details[6].split(",")
        rate_item = order_details[7].split(",")

        kot_addons_list = order_details[15].split(",")

        

        pdf = FPDF('P', 'mm','A5')

        pdf.add_page()
        pdf.set_font('helvetica', 'B', 16)
        pdf.set_title(f"{resta_name}")

        pdf.cell(0,0, f"{resta_name}",ln=1, align='C')

        pdf.ln(8)
        pdf.set_font('helvetica', '', 12)
        pdf.cell(0,0, 'Order Details (KOT Bill)', align='C')

        pdf.ln(10)
        pdf.set_font('helvetica', '', 10)
        pdf.text(5, 30, f'Order No: {order_id}')

        pdf.set_font('helvetica', '', 10)
        pdf.text(5, 38, f'Order Time: {order_time}')

        pdf.set_font('helvetica', '', 10)
        pdf.text(5, 46, f'Table No: {table_no}')

        pdf.set_font('helvetica', '', 10)
        pdf.text(5, 54, f'Customer Name: {customer_name}')

        pdf.set_font('helvetica', '', 10)
        pdf.text(5, 62, f'Customer Number: {customer_number}')

        pdf.set_font('helvetica', '', 10)
        pdf.text(98, 30, f'Order Date: {order_date}')

        pdf.set_font('helvetica', '', 10)
     
        pdf.text(98, 38, f'Service Type: {service_type1}')

        if service_type1 == "takeaway":
            pdf.text(98,46, f'Take Away Time: {takeaway_time}')



        pdf.line(5,68,140,68)

        pdf.ln(45)
        pdf.set_font('helvetica', '', 12)
        pdf.cell(0,0, 'Order Items',ln=1, align='C')

        pdf.line(5,78,140,78)

        pdf.text(5,88,"Items")

        pdf.text(75,88, "Qty")

        pdf.text(95,88, "Rate")

        pdf.text(115,88, "Amount (Rs)")

        pdf.set_font('helvetica', '', 8)


        x_axis = 5
        y_axis = 90

        total_price = 0
        for i in range(len(list_qty)):
            total_price += (int(list_qty[i]) * int(rate_item[i]))

        sgst = (total_price * 2.5)/100

        if len(list_item) >= 14:
            for i in range(14):
                y_axis = y_axis+8
                pdf.text(x_axis,y_axis, list_item[i]+'       '+kot_addons_list[i])
                pdf.text(x_axis+73,y_axis, str(list_qty[i]))
                pdf.text(x_axis+73+18,y_axis, str(rate_item[i]))
                pdf.text(x_axis+73+46,y_axis, str(int(list_qty[i]) * int(rate_item[i])))
            pdf.add_page()
        else:
            for i in range(len(list_item)):
                y_axis = y_axis+8
                pdf.text(x_axis,y_axis, list_item[i]+'    '+kot_addons_list[i])
                pdf.text(x_axis+73,y_axis, str(list_qty[i]))
                pdf.text(x_axis+73+18,y_axis, str(rate_item[i]))
                pdf.text(x_axis+73+46,y_axis, str(int(list_qty[i]) * int(rate_item[i])))
            # pdf.add_page()

        y_axis = 5
        if len(list_item)>=14:
            for i in range(14, len(list_item)):
                y_axis = y_axis+8
                pdf.text(x_axis,y_axis, list_item[i]+'    '+kot_addons_list[i])
                pdf.text(x_axis+73,y_axis, str(list_qty[i]))
                pdf.text(x_axis+73+18,y_axis, str(rate_item[i]))
                pdf.text(x_axis+73+46,y_axis, str(int(list_qty[i]) * int(rate_item[i])))
            

        pdf.output("./static/KOTBill.pdf")

        return send_file('./static/KOTBill.pdf', attachment_filename='KOTBill.pdf')

    return redirect(url_for('booktabledetails'))

@app.route("/viewbill/<id>", methods=["GET", "POST"])
def viewbill(id):
    if request.method == "POST" or request.method=="GET":
        # order_id = request.form['orderId'] #order number
        sql = "SELECT * FROM orders WHERE id = '"+id+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        
        order_details = cur.fetchone()

        resta_id = order_details[1]

        sql2 = "SELECT restaurant_name FROM users WHERE user_id = '"+str(resta_id)+"'"
        con.ping(reconnect = True)
        cur.execute(sql2)

        resta_name = cur.fetchone()[0]
        # order_time = order_details[10]
        # table_no = order_details[4]
        # customer_name = order_details[2]
        # customer_number = order_details[3]
        order_date = order_details[9]
        service_type1 = order_details[12]

        

        list_item = order_details[5].split(",")
        list_qty = order_details[6].split(",")
        rate_item = order_details[7].split(",")

        kot_addons_list = order_details[15].split(",")

        service_type = ""
        service_type = service_type1
       

        mylength = len(list_item)
   

        calculated_rate = []
        for i in range(mylength):
            calculated_rate.append(int(list_qty[i]) * int(rate_item[i]))

        total_price = 0
        for i in range(mylength):
            total_price += calculated_rate[i]

        return render_template("viewbill.html",resta_name=resta_name, order_details=order_details, mylength=mylength,order_id=id, service_type=service_type, list_item=list_item, list_qty= list_qty, rate_item=rate_item, total_rate=calculated_rate, total_price=total_price,order_date=order_date , kot_addons_list = kot_addons_list)

    # return render_template("viewbill.html")

@app.route("/completeviewbill/<id>", methods=["GET", "POST"])
def completeviewbill(id):
    if request.method == "POST" or request.method=="GET":
        # order_id = request.form['orderId'] #order number
        sql = "SELECT * FROM final_orders WHERE id = '"+id+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        
        order_details = cur.fetchone()

        resta_id = order_details[1]

        sql2 = "SELECT restaurant_name FROM users WHERE user_id = '"+str(resta_id)+"'"
        con.ping(reconnect = True)
        cur.execute(sql2)

        resta_name = cur.fetchone()[0]
        # order_time = order_details[10]
        # table_no = order_details[4]
        # customer_name = order_details[2]
        # customer_number = order_details[3]
        # order_date = order_details[9]
        service_type1 = order_details[5]

        order_date = order_details[11]

        list_item = order_details[6].split(",")
        list_qty = order_details[7].split(",")
        rate_item = order_details[8].split(",")

        

        service_type = ""
        service_type = service_type1
       

        mylength = len(list_item)
   
        kot_addons_list = []*mylength

        calculated_rate = []
        for i in range(mylength):
            calculated_rate.append(int(list_qty[i]) * int(rate_item[i]))

        total_price = 0
        for i in range(mylength):
            total_price += calculated_rate[i]

        return render_template("viewbill.html",resta_name=resta_name, order_details=order_details, mylength=mylength,order_id=id, service_type=service_type, list_item=list_item, list_qty= list_qty, rate_item=rate_item, total_rate=calculated_rate, total_price=total_price,order_date=order_date ,kot_addons_list = kot_addons_list)

    # return render_template("viewbill.html")


@app.route('/finalBill')
def finalBill():
    if 'myuserid' in session:
        resta_id = str(session['myuserid'])       
        sql = "SELECT restaurant_name FROM users WHERE user_id = '"+str(session['myuserid'])+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        name = cur.fetchone()[0]

        date_time = datetime.now(IST)
        date = date_time.strftime("%x")
       

        return render_template('billing.html' , date=date , name=name)
    return redirect(url_for('login'))



@app.route('/takeawaybill' , methods=["GET" , "POST"])
def takeawaybill():
     if request.method=="POST":
        mobile_no = request.form['orderId']
        # order_id_list = tab.split(",")


        table_no = "-"

        resta_id = str(session['myuserid'])

        sql = "SELECT gst FROM tempdetails WHERE userid = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        gst_approved = cur.fetchone()[0]
        
        final_item_list = []
        final_qty_list = []
        final_rate_list = []
        final_total_list = []
        order_id_list = []
        
        total_price_list = []

        sql = "SELECT * FROM orders WHERE mobile_number = '"+mobile_no+"' and resta_id='"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        details = cur.fetchall()

        # if(details = none)
        if(len(details) != 0):
            customer_name  = details[0][2]
            order_time = details[0][10]
            customer_number  = details[0][3]
            order_date = details[0][9]
            service_type1 = details[0][12]
            takeaway_time  = details[0][13]






            for i in details:

                item_list = i[5].split(",")
                qty_list = i[6].split(",")
                rate_list = i[7].split(",")
                total_rate = i[8].split(",")
                order_id_list.append(str(i[0]))

                print(item_list)
                print(qty_list)
                print(rate_list)
                print(total_rate)

                for i in range(len(item_list)):
                    final_item_list.append(item_list[i])
                    final_qty_list.append(qty_list[i])
                    final_rate_list.append(rate_list[i])
                    final_total_list.append(total_rate[i])


                order_ids =  ",".join(order_id_list)
                all_items = ",".join(final_item_list)
                all_qty = ",".join(final_qty_list)
                all_price = ",".join(final_rate_list)
                all_total_price = ",".join(final_total_list)

                print(final_item_list)
                print(final_qty_list)
                print(final_rate_list)
                print(final_total_list)
                print(order_ids)
                print(all_items)
                print(all_qty)
                print(all_price)
                print(all_total_price)

            sql2 = "SELECT restaurant_name FROM users WHERE user_id = '"+str(details[0][1])+"'"
            con.ping(reconnect = True)
            cur.execute(sql2)
            resta_name = cur.fetchone()[0]


            print(resta_name)


            total_price = 0
            for i in range(len(final_total_list)):
                total_price += int(final_total_list[i])
            
            print(total_price)

            for i in range(len(final_item_list)):
                total_price_list.append((final_total_list[i].strip())) 

            sql3 = "INSERT INTO final_orders (resta_id , customer_name , mobile_number , table_no , type , order_items , quantity , price , total_price , order_time , order_date,takeaway_time ,price_sum) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            val = (int(resta_id), customer_name, customer_number, '-' , service_type1 , all_items, all_qty, all_price, all_total_price, order_time, order_date,takeaway_time, total_price)
            con.ping(reconnect = True)
            cur.execute(sql3,val)
            con.commit()

            sql4 = "DELETE from orders where mobile_number='"+mobile_no+"'"
            con.ping(reconnect = True)
            cur.execute(sql4)
            con.commit()



            pdf = FPDF('P', 'mm','A5')

            pdf.add_page()
            pdf.set_font('helvetica', 'B', 16)
            pdf.set_title(f"{resta_name}")

            pdf.cell(0,0, f"{resta_name}",ln=1, align='C')

            pdf.ln(8)
            pdf.set_font('helvetica', '', 12)
            pdf.cell(0,0, 'Order Details', align='C')

            pdf.ln(10)
            pdf.set_font('helvetica', '', 10)
            pdf.text(5, 30, f'All Order No: {order_ids}')

            pdf.set_font('helvetica', '', 10)
            pdf.text(5, 38, f'Order Time: {order_time}')

            pdf.set_font('helvetica', '', 10)
            pdf.text(5, 46, f'Table No: {table_no}')

            pdf.set_font('helvetica', '', 10)
            pdf.text(5, 54, f'Customer Name: {customer_name}')

            pdf.set_font('helvetica', '', 10)
            pdf.text(5, 62, f'Customer Number: {customer_number}')

            pdf.set_font('helvetica', '', 10)
            pdf.text(98, 30, f'Order Date: {order_date}')

            pdf.set_font('helvetica', '', 10)

            pdf.text(98, 38, f'Service Type: {service_type1}')

            if service_type1 == "takeaway":
                pdf.text(98,46, f'Take Away Time: {takeaway_time}')


            pdf.line(5,68,140,68)

            pdf.ln(45)
            pdf.set_font('helvetica', '', 12)
            pdf.cell(0,0, 'Order Items',ln=1, align='C')

            pdf.line(5,78,140,78)

            pdf.text(5,88,"Items")

            pdf.text(75,88, "Qty")

            pdf.text(95,88, "Rate")

            pdf.text(115,88, "Amount (Rs)")

            pdf.set_font('helvetica', '', 8)


            x_axis = 5
            y_axis = 90

            total_price = 0
            for i in range(len(final_qty_list)):
                total_price += (int(final_qty_list[i]) * int(final_rate_list[i]))

            sgst = (total_price * 2.5)/100

            if len(final_item_list) >= 10:
                for i in range(10):
                    y_axis = y_axis+8
                    pdf.text(x_axis,y_axis, final_item_list[i])
                    pdf.text(x_axis+73,y_axis, final_qty_list[i])
                    pdf.text(x_axis+73+18,y_axis, final_rate_list[i])
                    pdf.text(x_axis+73+46,y_axis, total_price_list[i])
                pdf.add_page()
            else:
                for i in range(len(final_item_list)):
                    y_axis = y_axis+8
                    pdf.text(x_axis,y_axis, final_item_list[i])
                    pdf.text(x_axis+73,y_axis, final_qty_list[i])
                    pdf.text(x_axis+73+18,y_axis, final_rate_list[i])
                    pdf.text(x_axis+73+46,y_axis, total_price_list[i])
                # pdf.add_page()

                pdf.line(5,y_axis+5,140,y_axis+5)

                pdf.set_font('helvetica', '', 11)
                pdf.text(100,y_axis+13, "Sub Total :- ")

                pdf.text(122,y_axis+13, f"{total_price}/-")

                if gst_approved == "Yes":
                    pdf.set_font('helvetica', '', 11)
                    pdf.text(95,y_axis+22, "SGST :- ")
                    pdf.text(95, y_axis+30, "CGST :- ")

                    pdf.text(113,y_axis+22, "2.5 % ")
                    pdf.text(113, y_axis+30, "2.5 % ")

                    pdf.text(127,y_axis+22, f"{sgst}/-")
                    pdf.text(127, y_axis+30, f"{sgst}/-")

                    pdf.line(5,y_axis+38,140,y_axis+38)

                    pdf.set_font('helvetica', 'B', 14)
                    pdf.text(80, y_axis+44, "Grand Total :- ")

                    grand_total = total_price + 2*(sgst)

                    pdf.text(118, y_axis+44, f"{grand_total}/-")
                else:
                    pdf.set_font('helvetica', 'B', 14)
                    pdf.text(80, y_axis+30, "Grand Total :- ")
                    grand_total = total_price
                    pdf.text(118, y_axis+30, f"{grand_total}/-")



            y_axis = 5
            if len(final_item_list)>=10:
                for i in range(10, len(final_item_list)):
                    y_axis = y_axis+8
                    pdf.text(x_axis,y_axis, final_item_list[i])
                    pdf.text(x_axis+73,y_axis, final_qty_list[i])
                    pdf.text(x_axis+73+18,y_axis, final_rate_list[i])
                    pdf.text(x_axis+73+46,y_axis, total_price_list[i])


                pdf.line(5,y_axis+5,140,y_axis+5)

                pdf.set_font('helvetica', '', 11)
                pdf.text(100,y_axis+13, "Sub Total :- ")

                pdf.text(122,y_axis+13, f"{total_price}/-")

                if gst_approved == "Yes":
                    pdf.set_font('helvetica', '', 11)
                    pdf.text(95,y_axis+22, "SGST :- ")
                    pdf.text(95, y_axis+30, "CGST :- ")

                    pdf.text(113,y_axis+22, "2.5 % ")
                    pdf.text(113, y_axis+30, "2.5 % ")

                    pdf.text(127,y_axis+22, f"{sgst}/-")
                    pdf.text(127, y_axis+30, f"{sgst}/-")

                    pdf.line(5,y_axis+38,140,y_axis+38)

                    pdf.set_font('helvetica', 'B', 14)
                    pdf.text(80, y_axis+44, "Grand Total :- ")

                    grand_total = total_price + 2*(sgst)

                    pdf.text(118, y_axis+44, f"{grand_total}/-")

                else:
                    pdf.set_font('helvetica', 'B', 14)
                    pdf.text(80, y_axis+44, "Grand Total :- ")

                    grand_total = total_price

                    pdf.text(118, y_axis+44, f"{grand_total}/-")


            pdf.output("./static/finalBill.pdf")

        return send_file('./static/finalBill.pdf', attachment_filename='finalBill.pdf')

    
@app.route('/generatedfinalbill', methods=["GET", "POST"])
def generatefinalbill():
    if request.method=="POST":
        table_no = request.form['orderId']
        # order_id_list = tab.split(",")

        resta_id = str(session['myuserid'])

        sql = "SELECT gst FROM tempdetails WHERE userid = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        gst_approved = cur.fetchone()[0]
        
        final_item_list = []
        final_qty_list = []
        final_rate_list = []
        final_total_list = []
        order_id_list = []

        total_price_list = []
        


        sql = "SELECT * FROM orders WHERE table_no = '"+table_no+"' and resta_id='"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        details = cur.fetchall()

        # if(details = none)
        if(len(details) != 0):
            customer_name  = details[0][2]
            order_time = details[0][10]
            customer_number  = details[0][3]
            order_date = details[0][9]
            service_type1 = details[0][12]
            takeaway_time  = details[0][13]

            for i in details:
                
                item_list = i[5].split(",")
                qty_list = i[6].split(",")
                rate_list = i[7].split(",")
                total_rate = i[8].strip().split(",")
                order_id_list.append(str(i[0]))

                print(item_list)
                print(qty_list)
                print(rate_list)
                print(total_rate)

                for i in range(len(item_list)):
                    final_item_list.append(item_list[i])
                    final_qty_list.append(qty_list[i])
                    final_rate_list.append(rate_list[i])
                    final_total_list.append(total_rate[i])

                    


                order_ids =  ",".join(order_id_list)
                all_items = ",".join(final_item_list)
                all_qty = ",".join(final_qty_list)
                all_price = ",".join(final_rate_list)
                all_total_price = ",".join(final_total_list)
                all_total_price = all_total_price.strip()

                print(final_item_list)
                print(final_qty_list)
                print(final_rate_list)
                print(final_total_list)
                print(order_ids)
                print(all_items)
                print(all_qty)
                print(all_price)
                print(all_total_price)

            sql2 = "SELECT restaurant_name FROM users WHERE user_id = '"+str(details[0][1])+"'"
            con.ping(reconnect = True)
            cur.execute(sql2)
            resta_name = cur.fetchone()[0]


            print(resta_name)


            total_price = 0
            for i in range(len(final_total_list)):
                total_price += int(final_total_list[i])
                


            for i in range(len(final_item_list)):
                total_price_list.append((final_total_list[i].strip())) 

            print(total_price_list) 
            
            print(total_price)

            sql3 = "INSERT INTO final_orders (resta_id , customer_name , mobile_number , table_no , type , order_items , quantity , price , total_price , order_time , order_date ,price_sum) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            val = (int(resta_id), customer_name, customer_number, str(table_no) , service_type1 , all_items, all_qty, all_price, all_total_price, order_time, order_date, total_price)
            con.ping(reconnect = True)
            cur.execute(sql3,val)
            con.commit()

            sql4 = "DELETE from orders where table_no='"+table_no+"' and resta_id='"+resta_id+"'"
            con.ping(reconnect = True)
            cur.execute(sql4)
            con.commit()



            pdf = FPDF('P', 'mm','A5')

            pdf.add_page()
            pdf.set_font('helvetica', 'B', 16)
            pdf.set_title(f"{resta_name}")

            pdf.cell(0,0, f"{resta_name}",ln=1, align='C')

            pdf.ln(8)
            pdf.set_font('helvetica', '', 12)
            pdf.cell(0,0, 'Order Details', align='C')

            pdf.ln(10)
            pdf.set_font('helvetica', '', 10)
            pdf.text(5, 30, f'All Order No: {order_ids}')

            pdf.set_font('helvetica', '', 10)
            pdf.text(5, 38, f'Order Time: {order_time}')

            pdf.set_font('helvetica', '', 10)
            pdf.text(5, 46, f'Table No: {table_no}')

            pdf.set_font('helvetica', '', 10)
            pdf.text(5, 54, f'Customer Name: {customer_name}')

            pdf.set_font('helvetica', '', 10)
            pdf.text(5, 62, f'Customer Number: {customer_number}')

            pdf.set_font('helvetica', '', 10)
            pdf.text(98, 30, f'Order Date: {order_date}')

            pdf.set_font('helvetica', '', 10)

            pdf.text(98, 38, f'Service Type: {service_type1}')

            if service_type1 == "takeaway":
                pdf.text(98,46, f'Take Away Time: {takeaway_time}')


            pdf.line(5,68,140,68)

            pdf.ln(45)
            pdf.set_font('helvetica', '', 12)
            pdf.cell(0,0, 'Order Items',ln=1, align='C')

            pdf.line(5,78,140,78)

            pdf.text(5,88,"Items")

            pdf.text(75,88, "Qty")

            pdf.text(95,88, "Rate")

            pdf.text(115,88, "Amount (Rs)")

            pdf.set_font('helvetica', '', 8)


            x_axis = 5
            y_axis = 90

            total_price = 0
            for i in range(len(final_qty_list)):
                total_price += (int(final_qty_list[i]) * int(final_rate_list[i]))

            sgst = (total_price * 2.5)/100

            if len(final_item_list) >= 10:
                for i in range(10):
                    y_axis = y_axis+8
                    pdf.text(x_axis,y_axis, final_item_list[i])
                    pdf.text(x_axis+73,y_axis, final_qty_list[i])
                    pdf.text(x_axis+73+18,y_axis, final_rate_list[i])
                    pdf.text(x_axis+73+46,y_axis, total_price_list[i])
                pdf.add_page()
            else:
                for i in range(len(final_item_list)):
                    y_axis = y_axis+8
                    pdf.text(x_axis,y_axis, final_item_list[i])
                    pdf.text(x_axis+73,y_axis, final_qty_list[i])
                    pdf.text(x_axis+73+18,y_axis, final_rate_list[i])
                    pdf.text(x_axis+73+46,y_axis, total_price_list[i])
                # pdf.add_page()

                pdf.line(5,y_axis+5,140,y_axis+5)

                pdf.set_font('helvetica', '', 11)
                pdf.text(100,y_axis+13, "Sub Total :- ")

                pdf.text(122,y_axis+13, f"{total_price}/-")

                if gst_approved == "Yes":
                    pdf.set_font('helvetica', '', 11)
                    pdf.text(95,y_axis+22, "SGST :- ")
                    pdf.text(95, y_axis+30, "CGST :- ")

                    pdf.text(113,y_axis+22, "2.5 % ")
                    pdf.text(113, y_axis+30, "2.5 % ")

                    pdf.text(127,y_axis+22, f"{sgst}/-")
                    pdf.text(127, y_axis+30, f"{sgst}/-")

                    pdf.line(5,y_axis+38,140,y_axis+38)

                    pdf.set_font('helvetica', 'B', 14)
                    pdf.text(80, y_axis+44, "Grand Total :- ")

                    grand_total = total_price + 2*(sgst)

                    pdf.text(118, y_axis+44, f"{grand_total}/-")
                else:
                    pdf.set_font('helvetica', 'B', 14)
                    pdf.text(80, y_axis+30, "Grand Total :- ")
                    grand_total = total_price
                    pdf.text(118, y_axis+30, f"{grand_total}/-")



            y_axis = 5
            if len(final_item_list)>=10:
                for i in range(10, len(final_item_list)):
                    y_axis = y_axis+8
                    pdf.text(x_axis,y_axis, final_item_list[i])
                    pdf.text(x_axis+73,y_axis, final_qty_list[i])
                    pdf.text(x_axis+73+18,y_axis, final_rate_list[i])
                    pdf.text(x_axis+73+46,y_axis, total_price_list[i])


                pdf.line(5,y_axis+5,140,y_axis+5)

                pdf.set_font('helvetica', '', 11)
                pdf.text(100,y_axis+13, "Sub Total :- ")

                pdf.text(122,y_axis+13, f"{total_price}/-")

                if gst_approved == "Yes":
                    pdf.set_font('helvetica', '', 11)
                    pdf.text(95,y_axis+22, "SGST :- ")
                    pdf.text(95, y_axis+30, "CGST :- ")

                    pdf.text(113,y_axis+22, "2.5 % ")
                    pdf.text(113, y_axis+30, "2.5 % ")

                    pdf.text(127,y_axis+22, f"{sgst}/-")
                    pdf.text(127, y_axis+30, f"{sgst}/-")

                    pdf.line(5,y_axis+38,140,y_axis+38)

                    pdf.set_font('helvetica', 'B', 14)
                    pdf.text(80, y_axis+44, "Grand Total :- ")

                    grand_total = total_price + 2*(sgst)

                    pdf.text(118, y_axis+44, f"{grand_total}/-")

                else:
                    pdf.set_font('helvetica', 'B', 14)
                    pdf.text(80, y_axis+44, "Grand Total :- ")

                    grand_total = total_price

                    pdf.text(118, y_axis+44, f"{grand_total}/-")


            pdf.output("./static/finalBill.pdf")

        else:
            return "The bill had already generated or the table number is invalid!"

        return send_file('./static/finalBill.pdf', attachment_filename='finalBill.pdf')


@app.route("/menudetails", methods=["GET","POST"])
def menudetails():
    resta_id = str(session['myuserid'])
 
    sql = "SELECT dish FROM dishtype WHERE resta_id = '"+(resta_id)+"'"
    con.ping(reconnect = True)
    cur.execute(sql)
    con.commit()

    all_dish_data = cur.fetchall()
    
    if request.method == "POST":
        return redirect(url_for('menudetails'))
    return render_template('menuinfo.html', dishes = all_dish_data)

@app.route("/menuinfo" , methods=["GET" , "POST"])
def menuinfo(): 
    if 'myuserid' in session:
        if request.method == "POST":
            resta_id = str(session['myuserid'])
            dish =  request.form["dishType"]
            sql = "SELECT id FROM dishtype WHERE resta_id = '"+(resta_id)+"' and dish = '"+(dish)+"'"
            con.ping(reconnect = True)
            cur.execute(sql)
            con.commit()

            dish_id = cur.fetchone()
      

            # dishes = request.form.getlist["dishes"]
            # print(dishes)
            
            n=int(request.form['hidden1'])
            dishes=""
            for i in range(0,n+1):
                dish = request.form["dishes["+str(i)+"]"]
                dishes=dishes+dish+","


           

            dishes_array = dishes.split(',')
            dishes_array.pop()
  
            dishes = ",".join(dishes_array)

            

       


            m=int(request.form['hidden'])
            prices=""
            for i in range(0,m+1):
                newPrice = request.form["price["+str(i)+"]"]
                prices=prices+newPrice+","
         

            prices_array = prices.split(',')
            prices_array.pop()
         
            prices = ",".join(prices_array)
 
            

            o=int(request.form['hidden2'])
            descriptions=""
            for i in range(0,o+1):
                newDescription = request.form["description["+str(i)+"]"]
                descriptions=descriptions+newDescription+","
            

            description_array = descriptions.split(',')
            description_array.pop()
       
            descriptions = ",".join(description_array)
    

            sql = "INSERT INTO menuitems(dish_id, items , price , description) VALUES(%s, %s, %s , %s)"
            val = (dish_id, dishes , prices , descriptions)
            con.ping(reconnect = True)
            cur.execute(sql, val)
            
            con.commit()

            return redirect(url_for('menudetails'))

    return render_template('dashboard.html')



@app.route("/updatewebsite", methods=["GET", "POST"])
def updatewebsite():
    if 'myuserid' in session:
        sql = "SELECT restaurant_name FROM users WHERE user_id = '"+str(session['myuserid'])+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        name = cur.fetchone()[0]

        date_time = datetime.now(IST)
        date = date_time.strftime("%x")

        sql2 = "SELECT * FROM tempdetails WHERE userid = '"+str(session['myuserid'])+"'"
        con.ping(reconnect = True)
        cur.execute(sql2)
        details = cur.fetchone()

        sql3 = "SELECT * FROM tempcontact WHERE contact_user_id = '"+str(session['myuserid'])+"'"
        con.ping(reconnect = True)
        cur.execute(sql3)
        contact_details = cur.fetchone()

        if request.method == "POST":
            resta_name = request.form['resta_name']
            resta_tagline = request.form['resta_tagline']
            opening_time = request.form['opening_time']
            closing_time = request.form['closing_time']
            about = request.form['about']
            gst = request.form['gst_status']

            # contact 

            phone = request.form['phone']
            email = request.form['email']
            google_map = request.form['google_map']
            # insta_link = request.form['insta_link']
            address = request.form['address']
            fb_link = request.form['fb_link']
            twitter_link = request.form['twitter_link']
            wp_link = request.form['wp_link']
            insta_link = request.form['insta_link']

            myid = str(session['myuserid'])

            # sql4 = "UPDATE tempdetails SET resta_name = '"+resta_name+"', tagline = '"+resta_tagline+"', opening = '"+opening_time+"', closing = '"+closing_time+"', about = '"+about+"' WHERE contact_user_id = '"+str(session['myuserid'])+"'"
            # cur.execute(sql4)
            # con.commit()

            sql4 = "UPDATE tempdetails SET resta_name = '"+resta_name+"', tagline = '"+resta_tagline+"', opening = '"+opening_time+"', closing = '"+closing_time+"', about = '"+about+"', gst = '"+gst+"' WHERE userid = '"+myid+"'"
            con.ping(reconnect = True)
            cur.execute(sql4)
            con.commit()

            sql5 = "UPDATE tempcontact SET address = '"+address+"', mobile = '"+phone+"', email = '"+email+"', map_link = '"+google_map+"', facebook_link = '"+fb_link+"', twitter_link = '"+twitter_link+"', wp_link = '"+wp_link+"', instagram_link = '"+insta_link+"' WHERE contact_user_id = '"+myid+"'"
            con.ping(reconnect = True)
            cur.execute(sql5)
            con.commit()

            return redirect(url_for('updatewebsite'))

        return render_template("updatewebsite.html", name=name, date=date, details=details, contact_details = contact_details)
    return redirect(url_for('login'))

@app.route("/personal-information", methods=["GET", "POST"])
def personalinformation():
    if 'myuserid' in session:
        sql = "SELECT restaurant_name FROM users WHERE user_id = '"+str(session['myuserid'])+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        name = cur.fetchone()[0]

        date_time = datetime.now(IST)
        date = date_time.strftime("%x")

        my_img = name+".png"
        
        qr = qrcode.QRCode(
                version = 1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=50,
                border=2
            )

        qr.add_data(f"https://setupfood.com/{name}/dine-in/menu")
        qr.make(fit=True)
        img = qr.make_image(fit_color = "black", back_color="white")
        img.save(f"./static/QRcode/Dine-in/{name}.png")


                # qr code Take Away
        qr2 = qrcode.QRCode(
                    version = 1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=50,
                    border=2
        )

        qr2.add_data(f"https://setupfood.com/{name}/takeaway/menu")
        qr2.make(fit=True)
        img = qr2.make_image(fit_color = "black", back_color="white")
        img.save(f"./static/QRcode/Takeaway/{name}.png")

      

        if request.method == "POST":
            old_pwd = request.form['old_pwd']
            new_pwd = request.form['new_pwd']
            sql = "SELECT password FROM users WHERE user_id = '"+str(session['myuserid'])+"'"
            con.ping(reconnect = True)
            cur.execute(sql)
            old_pwd2 = cur.fetchone()[0]

            if old_pwd2 == old_pwd:
                sql = "UPDATE users SET password = '"+new_pwd+"' WHERE user_id = '"+str(session['myuserid'])+"'"
                con.ping(reconnect = True)
                cur.execute(sql)
                con.commit()
            else:
                flash("You entered wrong password")
                return redirect(url_for('personalinformation'))
        
        return render_template("personal-information.html", name=name, date = date, id=session['myuserid'] , my_img  = my_img)
    return redirect(url_for('login'))


@app.route("/logout")
def logout():
    session.clear()
    return redirect('login')

# @app.route("/help", methods=["GET", "POST"])
# def help():
#     sql = "CREATE TABLE help (help_id INT AUTO_INCREMENT, name VARCHAR(30), email VARCHAR(40), msg VARCHAR(100), PRIMARY KEY(help_id))"
#     cur2.execute(sql)
#     con2.commit()

#     if request.method == "POST":
#         name = request.form["name"]
#         email = request.form["email"]
#         msg = request.form["msg"]
#         sql = "INSERT INTO help(name, email, msg) VALUES (%s, %s, %s)"
#         val = (name, email, msg)
#         cur2.execute(sql, val)
#         con2.commit()
#     return render_template("help.html")

@app.route("/newsletter", methods=["GET","POST"])
def newsletter():
    # sql = "CREATE TABLE newsletter (news_id INT AUTO_INCREMENT, email VARCHAR(40), PRIMARY KEY(news_id))"
    # cur2.execute(sql)
    # con2.commit()
    if request.method == "POST":
        email = request.form["email"]
        sql = "INSERT INTO newsletter(email) VALUES (%s)"
        val = (email)
        con2.ping(reconnect=True)
        cur2.execute(sql, val)
        con2.commit()
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route("/restaurant/<name>", methods = ["GET", "POST"])
def generate_website(name):
    if request.method == "POST":
        contact_name = request.form["name"]
        phone = request.form["phone"]
        message = request.form["msg"]

        sql = "SELECT user_id FROM users WHERE restaurant_name = '"+name+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        resta_id = cur.fetchone()[0]

        sql = "INSERT INTO contacts(resta_id, name, mobile_number, message) VALUES (%s,%s,%s,%s)"
        val = (resta_id, contact_name, phone, message)
        con.ping(reconnect = True)
        cur.execute(sql,val)
        con.commit()

    sql = "SELECT * FROM tempdetails WHERE resta_name = '"+name.capitalize()+"'"
    con.ping(reconnect = True)
    cur.execute(sql)
    website_about_details = cur.fetchone()
    sql2 = "SELECT * FROM tempcontact WHERE contact_user_id = '"+str(website_about_details[1])+"'"
    con.ping(reconnect = True)
    cur.execute(sql2)
    website_contact_details = cur.fetchone()
    
    return render_template('generate_website1.html', website_about_details = website_about_details, website_contact_details = website_contact_details)

@app.route("/<name>/menu")
def generate_menu(name):
    if 'servicetype' in  session:
        sql = "SELECT user_id FROM users WHERE restaurant_name = '"+name+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        resta_id = cur.fetchone()
        my_resta_id = resta_id[0]

       

        sql = "SELECT * FROM tempdetails WHERE resta_name = '"+name.capitalize()+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        website_about_details = cur.fetchone()
    

        sql2 = "SELECT dish FROM dishtype WHERE resta_id = '"+str(my_resta_id)+"'"
        con.ping(reconnect = True)
        cur.execute(sql2)
        dish_types = cur.fetchall()
        mylength = len(dish_types)

        id_list = []

        for i in range(0, mylength):
            sql3 = "SELECT id FROM dishtype WHERE resta_id= '"+str(my_resta_id)+"' and dish = '"+dish_types[i][0]+"'"
            con.ping(reconnect = True)
            cur.execute(sql3)
            id_list.append(cur.fetchone()[0])

       

        dish_items = []

        dish_name = []
        dish_price = []
        dish_desc = []

    
    # for j in range(0,len(dish_name)):
    #     dish_name[j].pop()

    # for a in range(0,len(dish_name)):
    #     dish_price[a].pop()
    
    # for b in range(0,len(dish_name)):
    #     dish_desc[b].pop()
        for i in range(0, len(id_list)):
            sql4 = "SELECT * FROM menuitems WHERE dish_id = '"+str(id_list[i])+"'"
            con.ping(reconnect = True)
            cur.execute(sql4)
            dish_items.append(cur.fetchall()[0])
        
        for i in range(0, len(dish_items)):
            dish_name.append(dish_items[i][2].split(","))
            dish_price.append(dish_items[i][3].split(","))
            dish_desc.append(dish_items[i][4].split(","))

        

        # for j in range(0,len(dish_name)):
        #     dish_name = dish_name[j].pop()

        count = 0

        return render_template("generate_website_menu.html", name = name, website_about_details = website_about_details,my_dish_items = dish_types, mylength= mylength, dish_names = dish_name, dish_prices = dish_price, dish_descs = dish_desc, count = count)

    return "Please enter the valid route! Thanks"

@app.route("/<name>/cart" , methods=["GET" , "POST"])
def cart(name):
    if 'servicetype' in session:
        if request.method == "POST":

            sql = "SELECT * FROM tempdetails WHERE resta_name = '"+name.capitalize()+"'"
            con.ping(reconnect = True)
            cur.execute(sql)
            website_about_details = cur.fetchone()
            item_list = request.form['item_list']
            price_list = request.form['price_list']
            quantity_list = request.form['quantity_list']
            item_list = item_list.split(',')
            price_list = price_list.split(',')
            quantity_list  = quantity_list.split(',')
            length = len(item_list)
            for i in range(0,length):
                price_list[i] = int(price_list[i])
                quantity_list[i] = int(quantity_list[i])
            return render_template('generate_website_cart.html',length = length, website_about_details=website_about_details, item_list = item_list , price_list = price_list , quantity_list = quantity_list, name=name)
    
        return render_template('generate_website_cart.html' )
    return "Enter the valid route"

addons_list = ""
cart_item_list = ""
cart_quantity_list = ""
cart_price_list = ""
cart_total_price_list = ""
total_price = 0

@app.route("/<name>/service-details", methods=["GET","POST"])
def servicedetails(name):
    if 'servicetype' in session:
        if request.method == "POST":
            global cart_item_list, cart_price_list, cart_quantity_list, cart_total_price_list,total_price,addons_list

            addons_list = request.form['final_addons_list_p']

            cart_item_list = request.form['final_item_list_p']
            cart_quantity_list = request.form['final_quantity_list_p']
            cart_price_list = request.form['final_price_list_p']
            cart_total_price_list = request.form['final_total_price_list_p']

            sql = "SELECT * FROM tempdetails WHERE resta_name = '"+name.capitalize()+"'"
            con.ping(reconnect = True)
            cur.execute(sql)
            website_about_details = cur.fetchone()

            mylist = cart_total_price_list.split(",")

            mynewlist = []

            for item in mylist:
                newitem = item.strip()
                mynewlist.append(newitem)

            cart_total_price_list = ",".join(mynewlist)

            total_price = 0

            for i in range(len(mylist)):
                total_price += int(mylist[i])

            if session['servicetype'] == 'dinein':
                return render_template("service-details.html", name=name ,website_about_details=website_about_details)
            else:
                return render_template("takeaway.html", name=name)
    return "Enter the valid Route"


@app.route("/<name>/confirm-order", methods=["GET", "POST"])
def confirm_order(name):
    if 'servicetype' in session:
        if request.method == "POST":
            # customer_name = request.form['name']
            customer_number = request.form['mobile']
            
            service_type = session['servicetype']
            if service_type == "dinein":
                table_no = request.form['table_number']

                sql = "SELECT user_id FROM users WHERE restaurant_name = '"+ name +"'"
                con.ping(reconnect = True)
                cur.execute(sql)

                resta_id = cur.fetchone()
                myresta_id = resta_id[0]

                current_date_time = datetime.now(IST)
                order_date = current_date_time.strftime("%x")
                order_time = current_date_time.strftime("%X")
                
                
                sql = "INSERT INTO orders(resta_id, mobile_number, table_no, order_items, quantity, price, total_price,price_sum,order_date, order_time, type ,addons) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                val = (resta_id, customer_number, table_no, cart_item_list, cart_quantity_list, cart_price_list, cart_total_price_list,total_price,order_date,order_time,service_type,addons_list)
                con.ping(reconnect = True)
                cur.execute(sql,val)
                con.commit()
                

            else:
                hour = request.form["st_time"]
                min = request.form["time_mm"]
                slot = request.form["st_slot"]

                mytime = []
                mytime.append(hour)
                mytime.append(min)
                mytime.append(slot)

                mynew_joint_time = ":".join(mytime)
               

                sql = "SELECT user_id FROM users WHERE restaurant_name = '"+ name +"'"
                con.ping(reconnect = True)
                cur.execute(sql)

                resta_id = cur.fetchone()[0]

               

                current_date_time = datetime.now(IST)
                order_date = current_date_time.strftime("%x")
                order_time = current_date_time.strftime("%X")
                
                sql = "INSERT INTO orders(resta_id, customer_name, mobile_number, order_items, quantity, price, total_price,price_sum,order_date, order_time, type, takeaway_time, addons) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                val = (resta_id, customer_name, customer_number, cart_item_list, cart_quantity_list, cart_price_list, cart_total_price_list,total_price,order_date,order_time,service_type, mynew_joint_time, addons_list)
                con.ping(reconnect = True)
                cur.execute(sql,val)
                con.commit()
                

           
            
            # sql2 = "SELECT mobile FROM tempcontact WHERE contact_user_id = '"+str(myresta_id)+"'"
            # cur.execute(sql2)
            
            # resta_number_tupel = cur.fetchone()
            # resta_number = resta_number_tupel[0]

            # numbers = customer_number + "," + resta_number
            # print(numbers)

            # queryatring = {"authorization" : "p6vyZ2tz5FIIAG0yG8nNPk1WGIj11H6W9JInS63xpiMWOCqgH7HcIfjpD9s3",
            # "route" : "v3","sender_id" : "FSTSMS","message":"Thanks for placing your order!\nYour order will be ready in minutes.\nYou can view the order details by tapping here!","language" : "english","numbers" :{numbers}}

            # headers = {
            #     'cache-control' : 'no-cache'
            # }
            # response = requests.request("GET",url,headers=headers, params=queryatring)
            # print(response.text)
            
            sql = "SELECT id FROM orders WHERE mobile_number = '"+customer_number+"' ORDER BY id DESC"
            con.ping(reconnect = True)
            cur.execute(sql)
            
            myid = cur.fetchone()[0]
            
            message = f"Thanks for the placing your order!\n Your order will be ready in minutes.\n\n You can view the order details by tapping here! https://www.setupfood.com/viewbill/{myid} \n\n You can give us a feedback by tapping here! https://www.setupfood.com/{name}/feedback"
            number = "91" + customer_number
            url = f"https://api4ws.com/sendMessage.php?AUTH_KEY=APIDEMO&message={message}&phone={number}"
            
            response = requests.request("GET", url)


            return render_template("confirmorder.html")

        return render_template("confirmorder.html")
    return "Enter the valid url!"


# @app.route("/dashboard/finalorders")
# def finalorders():
#     return redirect(url_for('booktabledetails'))

total_price = 0

@app.route("/knowyourcustomers")
def customers():
    if 'myuserid' in session:
        resta_id = str(session['myuserid'])
        sql = "SELECT restaurant_name FROM users WHERE user_id = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        resta_name = cur.fetchone()[0]

        date_time = datetime.now(IST)
        date = date_time.strftime("%x")

        sql2 = "SELECT COUNT(id) FROM contacts WHERE resta_id = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql2)
        total_contacts = cur.fetchone()[0]


        sql3 = "SELECT COUNT(id) FROM feedbacks WHERE experience = '"+str(4)+"' and resta_id = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql3)
        happy_customers = cur.fetchone()[0]

        sql4 = "SELECT COUNT(id) FROM feedbacks WHERE experience = '"+str(5)+"' and resta_id = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql4)
        satisfied_customers = cur.fetchone()[0]

        sql5 = "SELECT COUNT(id) FROM feedbacks WHERE experience = '"+str(3)+"' and resta_id = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql5)
        unhappy_customers = cur.fetchone()[0]

        sql6 = "SELECT * FROM feedbacks WHERE resta_id = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql6)
        all_feedback = cur.fetchall()

        feedback_length = len(all_feedback)

        sql7 = "SELECT * FROM contacts WHERE resta_id = '"+resta_id+"'"
        con.ping(reconnect = True)
        cur.execute(sql7)

        contact_details = cur.fetchall()
   

        contact_list_length = len(contact_details)


        return render_template("customers.html", resta_name=resta_name, date=date, total_contacts = total_contacts, happy_customers = happy_customers, satisfied_customers = satisfied_customers, unhappy_customers = unhappy_customers, feedback_length=feedback_length, all_feedback=all_feedback, contact_details=contact_details, contact_length=contact_list_length)

# sql = "CREATE TABLE feedbacks(id INT AUTO_INCREMENT, resta_id INT, name VARCHAR(100), mobile_number VARCHAR(12), experience VARCHAR(100),message VARCHAR(400), PRIMARY KEY(id), FOREIGN KEY(resta_id) REFERENCES users(user_id) ON DELETE CASCADE)"
# cur.execute(sql)
# con.commit()

@app.route("/<name>/feedback", methods=["GET","POST"])
def feedback(name):
    if request.method == "POST":
        user_name= request.form['name']
        phone = request.form['mobile']
        experience = request.form['experience']
        msg = request.form['msg']

        sql2 = "SELECT user_id FROM users WHERE restaurant_name = '"+name+"'"
        con.ping(reconnect = True)
        cur.execute(sql2)
        resta_id = cur.fetchone()[0]
       

        sql = "INSERT INTO feedbacks(resta_id, name, mobile_number,experience, message) VALUES  (%s,%s,%s,%s,%s)"
        val = (resta_id, user_name, phone, experience, msg)
        con.ping(reconnect = True)
        cur.execute(sql,val)
        con.commit()

        return render_template("feedback.html", name=name)
        
    return render_template("feedback.html", name=name)


@app.route("/terms")
def terms():
    return render_template('termsandconditions.html')

@app.route("/privacy")
def privacy():
    return render_template('privacypolicy.html')

@app.route("/<name>/dine-in/menu")
def dineinmenu(name):
    global type_of_service
    type_of_service = request.url.split("/")[-2]
    
    session['servicetype'] = 'dinein'
    return redirect(f'/{name}/menu')

@app.route("/<name>/takeaway/menu")
def takeawaymenu(name):
    global type_of_service
    type_of_service = request.url.split("/")[-2]
    session['servicetype'] = 'takeaway'
    return redirect(f'/{name}/menu')

@app.route("/refund")
def refund():
    return render_template('refund.html')



# sql = "CREATE TABLE user (id INT AUTO_INCREMENT, username VARCHAR(40), password VARCHAR(40), PRIMARY KEY(id))"
# cur2.execute(sql)
# con2.commit()

# sql = "INSERT INTO user (username , password) values(%s,%s)"
# values = ("setupfood" , "setupfood123")
# cur2.execute(sql , values)
# con2.commit()

@app.route("/901675445663527171577861984482login" , methods = ["GET" , "POST"])
def setupFoodLogin():
    if request.method == "POST":
        uname = request.form["uname"]
        password = request.form["pwd"]
        check_email = "SELECT * FROM user WHERE username = '"+uname+"'"
        con.ping(reconnect = True)
        cur2.execute(check_email)
        get_one_uname = cur2.fetchone()
        # password = get_one_uname[2]
        
        if (not get_one_uname):
            flash("You entered wrong username")
            return redirect(url_for('setupFoodLogin'))
        elif(get_one_uname[2]!=password):
            flash("Wrong Password")
            return redirect(url_for('setupFoodLogin'))
        else:
            session['admin_loggedin'] = True 
            return redirect(url_for('setupFoodDashboard'))
    return render_template('setupfood_login.html')



@app.route("/setupfoodDashboard")
def setupFoodDashboard():
    if 'admin_loggedin' in session:
        date_time = datetime.now(IST)
        date = date_time.strftime("%x")

        current_month = date_time.strftime("%B")
        

        sql = "SELECT count(*) from users"
        con.ping(reconnect = True)
        cur.execute(sql)
        total_users = cur.fetchone()[0]

        

        sql1 = "SELECT count(*) from orders"
        con.ping(reconnect = True)
        cur.execute(sql1)
        payments_this_month = cur.fetchone()[0]

        sql4 = "select count(orders.id) from orders  where monthname(STR_TO_DATE(order_date, '%m/%d/%Y')) = '"+ current_month +"'"
        con.ping(reconnect = True)
        cur.execute(sql4)
        kots_this_month = cur.fetchone()[0]

        sql2 = "select count(orders.id) from orders  where monthname(STR_TO_DATE(order_date, '%m/%d/%Y')) = '"+ current_month +"' group by resta_id"
        con.ping(reconnect = True)
        cur.execute(sql2)
        total_kot = cur.fetchall()
        

        sql3 = "select DISTINCT users.email , users.restaurant_name from users join orders on users.user_id = orders.resta_id "
        con.ping(reconnect = True)
        cur.execute(sql3)
        data = cur.fetchall()
        
        return render_template('setupfood_dashboard.html' , total_users=total_users , date=date , payments_this_month=payments_this_month , data=data , total_kot=total_kot , kots_this_month=kots_this_month)
    else:
        return redirect(url_for('setupFoodLogin'))


@app.route("/adminLogout")
def adminLogout():
    session.clear()
    return redirect(url_for('setupFoodLogin'))


name = ""

@app.route("/login/takeorder", methods=["GET", "POST"])
def takeorder():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        sql = "SELECT * FROM users WHERE email = '"+email+"'"
        con.ping(reconnect=True)
        cur.execute(sql)
       
        
        get_email = cur.fetchone()

        name = get_email[2].lower()
    

        if (not get_email):
            flash("You entered wrong email address")
            return redirect(url_for('takeorder'))
        elif (get_email[3] != password):
            flash("You entered wrong password")
            return redirect(url_for('takeorder'))
        else:
            session['waiter'] = True
            return redirect(f'/{name}/takemyorder')

    return render_template("takeorder-login.html")

price_sum = 0

@app.route("/<name>/takemyorder", methods=["GET", "POST"])
def waitertakeorder(name):
    if 'waiter' in session:
 
        sql = "SELECT * FROM users WHERE restaurant_name = '"+name+"'"
        con.ping(reconnect=True)
        cur.execute(sql)
        resta_id = cur.fetchone()[0]

        sql = "SELECT logo FROM tempdetails WHERE userid = '"+str(resta_id)+"'"
        con.ping(reconnect=True)
        cur.execute(sql)
        
        logo = cur.fetchone()[0]

        sql2 = "SELECT * FROM dishtype WHERE resta_id = '"+str(resta_id)+"'"
        con.ping(reconnect=True)
        cur.execute(sql2)
        dish_ids = cur.fetchall()

        # print(dish_ids)
        dish_id_list = []

        for i in range(len(dish_ids)):
            dish_id_list.append(dish_ids[i][0])

        dish_items = []
        dish_price = []

        for i in dish_id_list:
            sql3 = "SELECT * FROM menuitems WHERE dish_id = '"+str(i)+"'"
            con.ping(reconnect=True)
            cur.execute(sql3)
            fetch_data = cur.fetchone()
            dish_item = fetch_data[2].split(",")
            for item in dish_item:
                dish_items.append(item)
            dish_prices = fetch_data[3].split(",")
            for price in dish_prices:
                dish_price.append(price)

        if request.method == "POST":
            n=int(request.form['hidden1'])
            qty=""
            table_no = request.form["table"]

            for i in range(0,n+1):
                new_qty = request.form["myqty["+str(i)+"]"]
                qty=qty+new_qty+","

            
            qty_array = qty.split(',')
            qty_array.pop()
  
            qty = ",".join(qty_array)


            m=int(request.form['hidden'])
            dish=""
            for i in range(0,m+1):
                new_dish = request.form["dish["+str(i)+"]"]
                dish=dish+new_dish+","


            dishes_array = dish.split(',')
            dishes_array.pop()
  
            dish = ",".join(dishes_array)

            j=int(request.form['hidden2'])
            addon=""
            for i in range(0,j+1):
                new_addon = request.form["myaddon["+str(i)+"]"]
                addon=addon+new_addon+","


            addons_array = addon.split(',')
            addons_array.pop()
  
            addon = ",".join(addons_array)

            date_time = datetime.now(IST)
            date = date_time.strftime("%x")

            ordertime = date_time.strftime("%X")
           

         
            sql = "SELECT mobile FROM tempcontact WHERE contact_user_id = '"+str(resta_id)+"'"
            con.ping(reconnect=True)
            cur.execute(sql)
            
            resta_number = cur.fetchone()[0]

            dish_list = dish.split(",")
            qty_list = qty.split(",")
    
            price_list_of_dishes = []

            total_price_of_dish = []

            for i in dish_list:
                dish_index = dish_items.index(i)
                price_of_the_dish = dish_price[dish_index]
                price_list_of_dishes.append(price_of_the_dish)


            for i in range(len(qty_list)):
                total_price_of_dish.append(str(int(qty_list[i]) * int(price_list_of_dishes[i])))

            mytype = "dinein" 
            myprice = ",".join(price_list_of_dishes)
            mytotal_price = ",".join(total_price_of_dish)

            global price_sum 
            
            for i in total_price_of_dish:
                price_sum += int(i)

            sql = "INSERT INTO orders(resta_id, customer_name, mobile_number, table_no, order_items, quantity, price, total_price, order_date, order_time, type, price_sum,addons) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val = (resta_id, name, resta_number, table_no, dish, qty, myprice, mytotal_price, date, ordertime, mytype, price_sum,addon)
            con.ping(reconnect = True)
            cur.execute(sql, val)
            con.commit()

            price_sum = 0


        return render_template('takeorder.html', dish_items=dish_items , name=name, logo=logo)
    return redirect(url_for('takeorder'))

mylength = 0
myitem_list = []
myquantity_list = []
myprice_list= []
mytotalprice_list = []
resta_name = ""
resta_id = ""
customer_name = ""
customer_mobile = ""
table_no = ""
status = ""
type = ""
addons = []


length_of_items = 0

@app.route("/<name>/changeorder", methods=["GET","POST"])
def changeoeder(name):
    if 'waiter' in session:
        global mylength, myitem_list, myquantity_list, myprice_list, mytotalprice_list, resta_name,length_of_items, resta_id, customer_name, customer_mobile, table_no, status, type,addons
        sql = "SELECT user_id FROM users WHERE restaurant_name = '"+name+"'"
        con.ping(reconnect=True)
        cur.execute(sql)
        resta_id = cur.fetchone()[0]

        sql = "SELECT logo FROM tempdetails WHERE userid = '"+str(resta_id)+"'"
        con.ping(reconnect=True)
        cur.execute(sql)
        
        logo = cur.fetchone()[0]
        
        if request.method == "POST":
            myitem_list = []
            myquantity_list = []
            myprice_list= []
            mytotalprice_list = []
            addons = []
            table_no = request.form["table"]

            sql = "SELECT * FROM orders WHERE resta_id = '"+str(resta_id)+"' and table_no = '"+table_no+"'"
            con.ping(reconnect=True)
            cur.execute(sql)
            all_items = cur.fetchall()

            if len(all_items) > 1:

                resta_id = all_items[0][1]
                customer_name = all_items[0][2]
                customer_mobile = all_items[0][3]
                table_no = all_items[0][4]
                status = all_items[0][11]
                type = all_items[0][12]

                mylength = len(all_items)
                
                for item in all_items:
                    dish_item = item[5].split(",")
                    quantity = item[6].split(",")
                    price = item[7].split(",")
                    total_price = item[8].split(",")
                    addons_type = item[15].split(",")


                    for i in dish_item:
                        myitem_list.append(i)
                    for j in quantity:
                        myquantity_list.append(j)
                    for k in price:
                        myprice_list.append(k)
                    for l in total_price:
                        mytotalprice_list.append(l)
                    for a in addons_type:
                        addons.append(a)

                length_of_items = len(myitem_list)
                myindex = 0

                # for item in all_items:
                #     myitem = item[0].split(",")
                #     for i in myitem:
                #         myitem_list.append(i)

                resta_name = name


                return render_template("deleteitem.html", name=name, mylength=mylength, table_no=table_no, myitem_list = myitem_list, len_of_item = length_of_items, myquantity_list=myquantity_list, myindex=myindex, logo=logo)
            else:
                return "No order is made from this table number!"

        myitem_list.clear()
        myquantity_list.clear()
        myprice_list.clear()
        mytotalprice_list.clear()
        mylength = 0
           
        return render_template("deleteitem.html",name=name, mylength=mylength, myitem_list = myitem_list, len_of_item = length_of_items, myquantity_list=myquantity_list, logo=logo)

    

@app.route("/storeItems", methods=["GET", "POST"])
def storeItems():
    if request.method == "POST":
        deleted_item = request.form["items"]
        print(deleted_item)
        print(myitem_list)
        
        item_index = myitem_list.index(deleted_item)

        myitem_list.pop(item_index)
        myquantity_list.pop(item_index)
        myprice_list.pop(item_index)
        mytotalprice_list.pop(item_index)
        addons.pop(item_index)

        date_time = datetime.now(IST)
        date = date_time.strftime("%x")

        ordertime = date_time.strftime("%X")

        myitem_str = ",".join(myitem_list)
        myqty_str = ",".join(myquantity_list)
        myprice_str = ",".join(myprice_list)
        mytotalprice_str = ",".join(mytotalprice_list)
        addons_str = ",".join(addons)

        total_sum = 0

        for i in mytotalprice_list:
            total_sum+= int(i)

        sql = "DELETE FROM orders WHERE table_no = '"+table_no+"' and resta_id = '"+str(resta_id)+"'"
        con.ping(reconnect = True)
        cur.execute(sql)
        con.commit()

        if len(myitem_list) >= 1:
            sql = "INSERT INTO orders (resta_id, customer_name, mobile_number, table_no, order_items, quantity, price, total_price, order_date, order_time, status, type, price_sum, addons) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            val = (resta_id, customer_name, customer_mobile, table_no, myitem_str, myqty_str, myprice_str, mytotalprice_str, date, ordertime, status, type, total_sum, addons_str)

            con.ping(reconnect=True)
            cur.execute(sql, val)
            con.commit()
        

    return redirect(f"/{resta_name}/changeorder")


if __name__ == '__main__':
    app.run(debug=True)
