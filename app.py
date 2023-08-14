# Portfolio Optimization using Simplex Algorithm
from flask import Flask, render_template, request, redirect, url_for
import os
import numpy as np 

def gen_matrix(var,cons):    
    tab = np.zeros((cons+1, var+cons+2))   
    return tab

def next_round_r(table):    
    m = min(table[:-1,-1])    
    if m>= 0:        
        return False    
    else:        
        return True

def next_round(table):    
    lr = len(table[:,0])   
    m = min(table[lr-1,:-1])    
    if m>=0:
        return False
    else:
        return True

def find_neg_r(table):
    lc = len(table[0,:])
    m = min(table[:-1,lc-1])
    if m<=0:        
        n = np.where(table[:-1,lc-1] == m)[0][0]
    else:
        n = None
    return n

def find_neg(table):
    lr = len(table[:,0])
    m = min(table[lr-1,:-1])
    if m<=0:
        n = np.where(table[lr-1,:-1] == m)[0][0]
    else:
        n = None
    return n

def loc_piv_r(table):
    total = []        
    r = find_neg_r(table)
    row = table[r,:-1]
    m = min(row)
    c = np.where(row == m)[0][0]
    col = table[:-1,c]
    for i, b in zip(col,table[:-1,-1]):
        if i**2>0 and b/i>0:
            total.append(b/i)
        else:                
            total.append(10000)
    index = total.index(min(total))        
    return [index,c]

def loc_piv(table):
    if next_round(table):
        total = []
        n = find_neg(table)
        for i,b in zip(table[:-1,n],table[:-1,-1]):
            if b/i>=0 and i**2>=0:
                total.append(b/i)
            else:
                total.append(10000)
        index = total.index(min(total))
        return [index,n]

def pivot(row,col,table):
    lr = len(table[:,0])
    lc = len(table[0,:])
    t = np.zeros((lr,lc))
    pr = table[row,:]
    if table[row,col]**2>0:
        e = 1/table[row,col]
        r = pr*e
        for i in range(len(table[:,col])):
            k = table[i,:]
            c = table[i,col]
            if list(k) == list(pr):
                continue
            else:
                t[i,:] = list(k-r*c)
        t[row,:] = list(r)
        return t
    else:
        print('Cannot pivot on this element.')

def convert(eq):
    eq = eq.split(',')
    if 'G' in eq:
        g = eq.index('G')
        del eq[g]
        eq = [float(i)*-1 for i in eq]
        return eq
    if 'L' in eq:
        l = eq.index('L')
        del eq[l]
        eq = [float(i) for i in eq]
        return eq

def gen_var(table):
    lc = len(table[0,:])
    lr = len(table[:,0])
    var = lc - lr -1
    v = []
    for i in range(var):
        v.append('x'+str(i+1))
    return v

def add_cons(table):
    lr = len(table[:,0])
    empty = []
    for i in range(lr):
        total = 0
        for j in table[i,:]:                       
            total += j**2
        if total == 0: 
            empty.append(total)
    if len(empty)>1:
        return True
    else:
        return False
    
def constrain(table,eq):
    if add_cons(table) == True:
        lc = len(table[0,:])
        lr = len(table[:,0])
        var = lc - lr -1      
        j = 0
        while j < lr:            
            row_check = table[j,:]
            total = 0
            for i in row_check:
                total += float(i**2)
            if total == 0:                
                row = row_check
                break
            j +=1
        eq = convert(eq)
        i = 0
        while i<len(eq)-1:
            row[i] = eq[i]
            i +=1        
        row[-1] = eq[-1]
        row[var+j] = 1    
    else:
        print('Cannot add another constraint.')

def add_obj(table):
    lr = len(table[:,0])
    empty = []
    for i in range(lr):
        total = 0        
        for j in table[i,:]:
            total += j**2
        if total == 0:
            empty.append(total)    
    if len(empty)==1:
        return True
    else:
        return False

def obj(table,eq):
    if add_obj(table)==True:
        eq = [float(i) for i in eq.split(',')]
        lr = len(table[:,0])
        row = table[lr-1,:]
        i = 0        
        while i<len(eq)-1:
            row[i] = eq[i]*-1
            i +=1
        row[-2] = 1
        row[-1] = eq[-1]
    else:
        print('You must finish adding constraints before the objective function can be added.')

def maxz(table):
    while next_round_r(table)==True:
        table = pivot(loc_piv_r(table)[0],loc_piv_r(table)[1],table)
    while next_round(table)==True:
        table = pivot(loc_piv(table)[0],loc_piv(table)[1],table)       
    lc = len(table[0,:])
    lr = len(table[:,0])
    var = lc - lr -1
    i = 0
    val = {}
    for i in range(var):
        col = table[:,i]
        s = sum(col)
        m = max(col)
        if float(s) == float(m):
            loc = np.where(col == m)[0][0]            
            val[gen_var(table)[i]] = table[loc,-1]
        else:
            val[gen_var(table)[i]] = 0
    val['max'] = table[-1,-1]
    return val

app = Flask(__name__, template_folder='templates')


APP_ROOT = os.path.dirname(os.path.abspath('__file__'))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        rows = int(request.form["rows"])
        columns = int(4)
        return render_template("tablev2.html", columns=int(columns), rows=int(rows))
    return render_template("index.html")

@app.route("/result", methods=["POST"])
def table():
    try:
      data = []
      for i in range(int(request.form["rows"])):
          row = []
          for j in range(int(request.form["columns"])):
              row.append(float(request.form[f"r{i}c{j}"]))
          data.append(row)
      rows = int(request.form["rows"])
      columns = int(request.form["columns"])
      investments = []
      for k in range(rows):
          investments.append(request.form[f"invName{k}"])
      print("Rows: ", int(request.form["rows"]))
      print("Columns: ", int(request.form["columns"]))
      print(data)
      solution = solve(data, rows, columns)
      values = list(solution.values())
      values = [float("{:.2f}".format(i * 100)) for i in values]
      portfolioRet = []
      for i in range(rows):
          portfolioRet.append(float("{:.2f}".format((data[i][0] * values[i])/100)))
      print(portfolioRet)
      sumValues = float("{:.2f}".format(sum(values[:-1])))
      sumPort = float("{:.2f}".format((values[-1])))
      asset = float(request.form["asset"])
      allocAmnt = []
      for i in range(rows):
          allocAmnt.append(float("{:.2f}".format((asset * values[i])/100)))
      sumAlloc = float("{:.2f}".format(sum(allocAmnt)))
      estRet = []
      for i in range(rows):
          estRet.append(float("{:.2f}".format((asset * portfolioRet[i])/100)))
      sumRet = float("{:.2f}".format(sum(estRet)))
      return render_template("resultv2.html", data=data, rows=rows, columns=columns, investments=investments, values=values, portfolioRet=portfolioRet, sumValues=sumValues, sumPort=sumPort, allocAmnt=allocAmnt, sumAlloc=sumAlloc, estRet=estRet, sumRet=sumRet)
    except:
      return "There is an error calculating your input. Please make sure that there are no blank cells."

output = []
def print_diagonal_1(n):
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(1)
            else:
                row.append(0)
        output.append(row)

def solve(data, rows, columns):
    try:
      # Implement your solution here
      constraints = []
      m = gen_matrix(rows, (rows*2)+2)
      print_diagonal_1(rows)
      constraintsL = [None] * (rows)
      constraintsG = [None] * (rows)
      for i in range(rows):
        constraintsL[i] = ','.join(map(str, output[i])) + ",L," + str(data[i][3]/100)
      for i in range(rows):
        constraintsG[i] = ','.join(map(str, output[i])) + ",G," + str(data[i][2]/100)
      for i in range(rows):
        constrain(m,constraintsL[i])
      for i in range(rows):
        constrain(m,constraintsG[i])
      riskConst = ""
      for i in range(rows):
          riskConst += str(data[i][1]/100) + ","
      riskConst += "L," + str(rows)
      constrain(m,riskConst)
      allConst = ""
      for i in range(rows):
          allConst += "1,"
      allConst += "L,1"
      constrain(m,allConst)
      potentialRet = ""
      for i in range(rows):
        potentialRet += str(data[i][0]/100) + ","
      potentialRet += "0"
      obj(m,potentialRet)
      print("M", m)
      print("POT RETURN: ", potentialRet)
      print("CONSTRAINTS G: ", constraintsG)
      print("CONSTRAINTS L: ", constraintsL)
      print("CONSTRAINTS RISK: ", riskConst)
      print("CONSTRAINTS ALL: ", allConst)
      print("ANS: ", maxz(m))
      return maxz(m)
    except:
      return "There is an error calculating your input."

if __name__ == "__main__":
    app.run()