#project: p2
#submitter: kmconrad3
#partner: none
#hours: 12

import csv
from io import TextIOWrapper
from zipfile import ZipFile
import pandas as pd
from csv import reader



class ZippedCSVReader:
    
    def __init__(self, zipf):
        self.zipf=zipf
        self.paths=[]
        
        with ZipFile(zipf) as zf:
            for name in zf.namelist():
                self.paths.append(name)
                
    def rows(self, path=None):
        if path:
            with ZipFile(self.zipf) as zf:
                with zf.open(path,"r") as f:
                    tio=TextIOWrapper(f)
                    read= csv.DictReader(tio)
                    for row in read:
                        yield row
        else:
            for p in self.paths:
                with ZipFile(self.zipf) as zf:
                    with zf.open(p,"r") as f:
                        tio=TextIOWrapper(f)
                        reader=csv.DictReader(tio)
                        for row in reader:
                            yield row
            
            
                   
class Loan:
    
    def __init__(self, amount, purpose, race, sex, income, decision):
        self.amount=amount
        self.purpose=purpose
        self.race=race
        self.sex=sex
        self.income=income
        self.decision=decision
        
    def __repr__(self):
        return f"Loan({repr(self.amount)}, {repr(self.purpose)}, {repr(self.race)}, {repr(self.sex)}, {repr(self.income)}, {repr(self.decision)})"

    def __getitem__(self, lookup):
        if hasattr(self, lookup):
            return getattr(self, lookup)
        else:
            values = (self.amount, self.purpose, self.race,
                      self.sex, self.income, self.decision)
            return int(lookup in values)

            
            
class Bank:
    
    def __init__(self, name, reader):
        self.name=name
        self.reader=reader
        
    def loans(self):
        diclis=list(self.reader.rows())
        for d in diclis:
            if self.name in (None, d["agency_abbr"]):
                if (int(d['action_taken'])==1):
                    d['action_taken']='approve'
                else:
                    d['action_taken']='deny'
                if d['loan_amount_000s']:
                    d['loan_amount_000s']=int(d['loan_amount_000s'])
                else:
                    d['loan_amount_000s']=0
                if d['applicant_income_000s']:
                    d['applicant_income_000s']=int(d['applicant_income_000s'])
                else:
                    d['applicant_income_000s']=0
                loan=Loan(d['loan_amount_000s'], d['loan_purpose_name'], d['applicant_race_name_1'], d['applicant_sex_name'], d['applicant_income_000s'], d['action_taken'])
                yield loan
            
            
def get_bank_names(reader):
    names=[]
    for path in reader.paths:
        with ZipFile(reader.zipf) as zf:
            with zf.open(path, "r") as f:
                tiow=TextIOWrapper(f)
                dic=csv.DictReader(tiow)
                for row in dic:
                    if row['agency_abbr'] not in names:
                        names.append(row['agency_abbr'])
    return sorted(names)
            
                
                
class SimplePredictor():
    
    def __init__(self):
        self.approved=0
        self.denied=0
   
                    
    def predict(self, loan):
        if loan.purpose=="Refinancing":
            self.approved+=1
            return True
        else:
            self.denied+=1
            return False
        
    def get_approved(self):
        return int(self.approved)
    
    def get_denied(self):
        return int(self.denied)
    

    
class Node(SimplePredictor):
    
    def __init__(self, field, threshold, left=None, right=None):
        SimplePredictor.__init__(self)
        self.field=field
        self.threshold=threshold
        self.left=left
        self.right=right
    
    def dump(self, indent=0):
        if self.field=='class':
            line='class=' + str(self.threshold)
        else:
            line=self.field + " <= " + str(self.threshold)
        print("   "*indent+line)
        if self.left != None:
            self.left.dump(indent+1)
        if self.right != None:
            self.right.dump(indent+1)
            
    def node_count(self):
        count=1
        if self.left != None:
            count += self.left.node_count()
        if self.right != None:
            count += self.right.node_count()
        return count
    
    def predict(self, loan):
        if self.field=='class':
            if int(self.threshold)==1:
                self.approved+=1
                return True
            else:
                self.denied+=1
                return False
        else:
            if float(loan[self.field]) <= float(self.threshold):
                if self.left.predict(loan) == True:
                    self.approved+=1
                    return True
                else:
                    self.denied+=1
                    return False
            if float(loan[self.field]) > float(self.threshold):
                if self.right.predict(loan) == True:
                    self.approved+=1
                    return True
                else:
                    self.denied+=1
                    return False
        
        

def build_tree(rows, root_inx=0):
    if int(rows[root_inx]['left'])>=0:
        node_left=build_tree(rows, int(rows[root_inx]['left']))
    else:
        node_left=None
    if int(rows[root_inx]['right'])>=0:
        node_right=build_tree(rows, int(rows[root_inx]['right']))
    else:
        node_right=None
    node=Node(rows[root_inx]['field'], rows[root_inx]['threshold'],node_left, node_right)
    return node
    


    
def bias_test(bank, predictor, field, value_override):
    dif=0
    for i in bank.loans():
        result=predictor.predict(i)
        if field=='sex':
            i.sex=value_override
        if field=='race':
            i.race=value_override
        result2=predictor.predict(i)
        if result != result2:
            dif+=1
    return dif/len(list(bank.loans()))