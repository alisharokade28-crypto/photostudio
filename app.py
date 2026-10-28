from flask import Flask, render_template_string, request, redirect, session
import pandas as pd, os

app = Flask(__name__)
app.secret_key = "photo123"
FILE = "bookings.csv"

if not os.path.exists(FILE):
    pd.DataFrame(columns=["ID", "Customer", "Event", "Date", "Package", "Price", "User"]).to_csv(FILE, index=False)

LOGIN = """
<style>body{font-family:sans-serif;background:#f0f2f5;display:flex;justify-content:center;align-items:center;height:100vh}.box{background:white;padding:30px;border-radius:15px;box-shadow:0 5px 20px #0002;width:300px;text-align:center}input{width:90%;padding:10px;margin:8px;border-radius:8px;border:1px solid #ccc}button{width:95%;padding:10px;background:#6C5CE7;color:white;border:none;border-radius:8px;font-weight:bold;cursor:pointer}</style>
<div class="box"><h2>📸 Studio Login</h2><form method="post"><input name="username" placeholder="Username: admin" required><input type="password" name="password" placeholder="Password: admin123" required><button>Login</button></form></div>
"""

DASH = """
<style>body{font-family:sans-serif;background:#f5f6fa;margin:0;padding:20px}.header{background:linear-gradient(90deg,#6C5CE7,#a29bfe);color:white;padding:15px 25px;border-radius:12px;display:flex;justify-content:space-between}.card{background:white;padding:20px;border-radius:12px;margin-top:20px;box-shadow:0 2px 10px #0001}input,select{padding:8px;margin:5px;border-radius:6px;border:1px solid #ccc}button{background:#6C5CE7;color:white;border:none;padding:8px 15px;border-radius:6px;cursor:pointer}.del{background:#ff7675}table{width:100%;border-collapse:collapse;margin-top:10px}th{background:#6C5CE7;color:white;padding:10px}td{padding:8px;border-bottom:1px solid #eee;text-align:center}.income{font-size:22px;font-weight:bold;color:#00b894}</style>
<div class="header"><h3>Welcome, {{user}}! 📸 Photo Studio</h3><a href="/logout" style="color:white">Logout</a></div>
<div class="card"><h3>➕ New Booking Add Kara</h3><form method="post" action="/add"><input name="cust" placeholder="Customer Name" required><input name="event" placeholder="Wedding / Birthday" required><input type="date" name="date" required><select name="package"><option>Basic - 3000</option><option>Standard - 7000</option><option>Premium - 15000</option></select><button>Book Now</button></form></div>
<div class="card"><h3>Tumche Bookings ({{count}}) - <span class="income">Total: Rs. {{income}}</span></h3>
<table><tr><th>ID</th><th>Customer</th><th>Event</th><th>Date</th><th>Package</th><th>Price</th><th>Action</th></tr>
{% for i, row in bookings.iterrows() %}
<tr><td>{{row['ID']}}</td><td>{{row['Customer']}}</td><td>{{row['Event']}}</td><td>{{row['Date']}}</td><td>{{row['Package']}}</td><td>{{row['Price']}}</td><td><a href="/delete/{{loop.index0}}"><button class="del">Delete</button></a></td></tr>
{% endfor %}
</table></div>
"""

@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        if request.form['username']=='admin' and request.form['password']=='admin123':
            session['user']=request.form['username']
            return redirect("/dashboard")
        return "<h3>Wrong Password! <a href='/'>Back</a></h3>"
    if 'user' in session: return redirect("/dashboard")
    return render_template_string(LOGIN)

@app.route("/dashboard")
def dashboard():
    if 'user' not in session: return redirect("/")
    df=pd.read_csv(FILE)
    my=df[df['User']==session['user']] if not df.empty else df
    income = my['Price'].astype(int).sum() if len(my)>0 else 0
    return render_template_string(DASH, user=session['user'], bookings=my, count=len(my), income=int(income))

@app.route("/add", methods=["POST"])
def add():
    if 'user' not in session: return redirect("/")
    df=pd.read_csv(FILE)
    price=request.form['package']
    new={"ID":len(df)+1,"Customer":request.form['cust'],"Event":request.form['event'],"Date":request.form['date'],"Package":price,"Price":price.split("-")[-1].strip(),"User":session['user']}
    pd.concat([df,pd.DataFrame([new])]).to_csv(FILE,index=False)
    return redirect("/dashboard")

@app.route("/delete/<int:id>")
def delete(id):
    df=pd.read_csv(FILE)
    my=df[df['User']==session['user']]
    other=df[df['User']!=session['user']]
    my=my.drop(my.index[id])
    pd.concat([other,my]).to_csv(FILE,index=False)
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.pop('user',None)
    return redirect("/")

if __name__=="__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)