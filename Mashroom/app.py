from flask import Flask,request,render_template
import numpy as  np
import pandas  as pd
import pickle 
from sklearn.tree import DecisionTreeClassifier
from Logger.logger import Logs
from flask_mysqldb import MySQL





app=Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password123'
app.config['MYSQL_DB'] = 'mushroom'


# creating object of MySQL 


mysql = MySQL(app)




gillcolor_list = {0:"Buff", 1:"Red", 2:"Gray", 3:"Chocolate", 4:"Black", 5:"Brown", 6:"Orange", 7:"Pink", 8:"Green", 9:"Purple", 10:"White", 11:"Yellow"}
sporeprintcolor_list = {0:"Yellow", 1:"Chocolate", 2:"Black", 3:"Brown", 4:"Buff", 5:"Green", 6:"Purple", 7:"White", 8:"Orange"}
population_list = {0:"Abundant", 1:"Clustered", 2:"Numerous", 3:"Scattered", 4:"Several", 5:"Solitary"}
gillsize_list = {0:"Broad", 1:"Narrow"}
stalk_root_list = {0:"Missing", 1:"Bulbous", 2:"Club", 3:"Equal", 4:"Rooted"}
bruises_list = {0:"NO", 1:"Yes"}
stalkshape_list = {0:"Enlarging", 1:"Tapering"}


model=pickle.load(open("../Mushroom_Classification_Model.pkl","rb"))




@app.route("/")
def home():

    return render_template('index.html')
    #return render_template('index.html', result='r')


@app.route('/predict', methods=['GET','POST'])
def predict():



    if request.method=="POST":
        gillcolor=float(request.form["gill-color"])
        sporeprintcolor=float(request.form["spore-print-color"])
        population=float(request.form['population'])
        gillsize=float(request.form['gill-size'])
        stalk_root = float(request.form["stalk-root"])
        bruises=float(request.form['bruises'])
        stalkshape=float(request.form['stalk-shape'])

        print(gillcolor, sporeprintcolor, population, gillsize, stalk_root, bruises, stalkshape)
        

        gillcolor_str = gillcolor_list[int(request.form["gill-color"])]
        sporeprintcolor_str = sporeprintcolor_list[int(request.form["spore-print-color"])]
        population_str = population_list[int(request.form['population'])]
        gillsize_str = gillsize_list[int(request.form['gill-size'])]
        stalk_root_str = stalk_root_list[int(request.form["stalk-root"])]
        bruises_str = bruises_list[int(request.form['bruises'])]
        stalkshape_str = stalkshape_list[int(request.form['stalk-shape'])]

        print(gillcolor_str, sporeprintcolor_str, population_str, gillsize_str, stalk_root_str, bruises_str, stalkshape_str)



        
        x=pd.DataFrame({"gill_color":[gillcolor],"spore_print_color":[sporeprintcolor],"population":[population],
        "gill_size":[gillsize],"stalk_root":[stalk_root],"bruises":[bruises],"stalk_shape":[stalkshape]})
        ml=model.predict(x)
        m=round(ml[0],2)
        
        if m==0:
            predicted_result = "Edible"
        else:
            predicted_result = "Poisonous"


        try:
            # creating a cursor to add info to database MySQL  

            crsr = mysql.connection.cursor()

            crsr.execute(f"INSERT INTO prediction_record(gillcolor, sporeprintcolor, population, gillsize, stalk_root, bruises, stalkshape, predicted_result) VALUES('{gillcolor_str}', '{sporeprintcolor_str}','{population_str}','{gillsize_str}','{stalk_root_str}','{bruises_str}', '{stalkshape_str}', '{predicted_result}')")

            mysql.connection.commit()

            crsr.close()
            print("Inserted values successfully !")

        except Exception as error:
            print("Error occured !\n", error)


        if m==0:

            return render_template("index.html", result='Your mushroom is edible !')
        else:

            return render_template("index.html", result='Your mushroom is poisnous !')



        # log.addLog("INFO", "Prediction completed Successfully !")
        # log.addLog("INFO", "Rendering tamplate <index.html> with Predection !")

        #return render_template('index.html', result='Your mushroom is {}!'.format(g))
        #return render_template('index.html', result='Error !')




@app.route("/database")
def database():

    heading = ("Gill Color", "Spore Print Color", "Population", "Gill Size", "Stalk Root", "Bruises", "Stalk Shape", "Predicted Result")
    all_data = ""
    try:

        crsr = mysql.connection.cursor()

        all_prediction_data = crsr.execute("SELECT * FROM prediction_record")


        if all_prediction_data > 0:
            all_data = crsr.fetchall()

            print("All prediction data retrived successfully !")
        
        crsr.close()


    except Exception as error:
        print("Error occured while fetching all data from Database MySQL !", error)

    return render_template('database.html', heading = heading, data = all_data)



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080,debug=True)
