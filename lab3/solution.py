import sys
import csv
import math

D_whole = set()
learning_examples = sys.argv[1]
testing_examples = sys.argv[2]
depth_restriction = -1000
if(len(sys.argv) > 3):
   depth_restriction = int(sys.argv[3])

class Combination:
   def __init__(self, list_of_column_names, list_of_values):
      self.values = dict() # dictionary[znacajka] = vrijednost_znacajke
      self.class_label = list_of_column_names[-1]
      for i in range(len(list_of_column_names)):
         self.values[list_of_column_names[i]] = list_of_values[i]
   def __str__(self):
      combination_string = ""
      for key in self.values:
         combination_string += key + ":" + self.values[key] + " "
      return combination_string
   def __hash__(self):
      frozen_clause = frozenset(self.values.values())
      return hash(frozen_clause)

class Node:
  def __init__(self, x, subtrees):
    self.x = x
    self.subtrees = set()
    for subtree in subtrees:
       self.subtrees.add(subtree)

class Leaf:
  def __init__(self, decision):
    self.decision = decision

def printBranches(rezultat,nadopuna):
   if(isinstance(rezultat, Leaf)):
      nadopuna.append(rezultat.decision)
      br = 1
      for i in range(0, len(nadopuna), 2):
         if(i == len(nadopuna) - 1):
            print(nadopuna[i])
            break
         print(str(br) + ":" + nadopuna[i] + "=" + nadopuna[i + 1], end = " ")
         br += 1
      return  
   nadopuna.append(rezultat.x)
   for subtree in rezultat.subtrees:
      nadopuna.append(subtree[0])
      printBranches(subtree[1], nadopuna)
      nadopuna.pop()
      nadopuna.pop()
   return

def createBranches(rezultat):
   if(isinstance(rezultat, Leaf)):
         return [rezultat.decision]
   grane = []
   for subtree in rezultat.subtrees:
      podgrane = createBranches(subtree[1])
      for podgrana in podgrane:
         if(isinstance(podgrana, str)):
            grane.append([rezultat.x] + [subtree[0]] + [podgrana])
         else:
            a = [rezultat.x] + [subtree[0]]
            for i in range(len(podgrana)):
               a = a + [podgrana[i]]
            grane.append(a)
   return grane
 
# vraca sve class_labele iz skupa S
def classes(S):
   cl = set()
   for comb in S:
      cl.add(comb.values[comb.class_label])
   return cl

# vrati broj pojavljivanja klase c unutar skupa S
def freq_of_class(S, c):
   freq = 0
   for comb in S:
      if(comb.values[comb.class_label] == c):
         freq += 1
   return freq

# entropija
def E(S):
   cl = classes(S)
   entropy = 0
   for c in cl:
      freq = freq_of_class(S, c)
      entropy = entropy + ((freq/len(S)) * math.log2(freq/len(S)))
   entropy = -1*entropy
   return entropy

# vratiti podskup od D gdje je x=v
def filter(D, x, v):
   Dxv = set()
   for comb in D:
      if(comb.values[x] == v):
         Dxv.add(comb)
   return Dxv

# vratiti IG za zadani x unutar D
def IG(D, x):
   Vx = values_of(D, x)
   sum = 0
   for v in Vx:
      Dxv = filter(D, x, v)
      sum = sum + ((len(Dxv)/len(D)) * E(Dxv))
   ig = E(D) - sum
   return ig

# pronaci i vratiti najcesci y unutar D
# Ako postoji vise vrijednosti
# ciljne varijable s najcescim brojem pojavljivanja, trebate vratiti onu vrijednost koja je
# prva prema abecednom poretku 
def mostFrequent(D):
   cl = classes(D)
   cl_list = list(cl)
   cl_list.sort()
   max = 0
   most_frequent = ""
   for i in range(len(cl_list)):
      freq = freq_of_class(D, cl_list[i])
      if(freq > max):
         max = freq
         most_frequent = cl_list[i]
   return most_frequent

# pronaci i vratiti onu znacajku x iz skupa X koja ima najveci IG(D, x)
def mostDiscriminating(D, X):
   max = -1
   most_discriminating = ""
   X = list(X)
   X.sort()
   for i in range(len(X)):
      ig = IG(D, X[i])
      print("IG(" + X[i] + ")=" + str(ig), end = " ")
      if(ig > max):
         max = ig
         most_discriminating = X[i]
   print()
   return most_discriminating

# vratiti skup vrijednosti od x unutar D
def values_of(D, x):
   Vx = set()
   for comb in D:
      Vx.add(comb.values[x])
   return Vx

def id3(D, Dparent, X, y, depth): #-- pocetno Dparent = D
   depth += 1
   global depth_restriction, D_whole
   if (len(D) == 0):
      v = mostFrequent(Dparent) #najcesca oznaka primjera u nadcvoru
      depth -= 1
      return Leaf(v)
   if(depth == depth_restriction):
      v = mostFrequent(D)
      depth -= 1
      return Leaf(v)
   v = mostFrequent(D) # najcesca oznaka primjera u cvoru
   if (len(X) == 0 or D == filter(D, y, v)):
      depth -= 1
      return Leaf(v)
   x = mostDiscriminating(D, X) # najdiskriminativnija znacajka
   print(x)
   subtrees = set()
   Vx = values_of(D_whole, x)
   for v in Vx:
      t = id3(filter(D, x, v), D, X - {x}, y, depth)
      subtrees.add((v, t))
   depth -= 1
   return Node(x, subtrees)

def Predictions(P):
   predictions = []
   for p in P:
      #p.values[znacajka]=vrijednost_znacajke
      for branch in branches:
         match = True
         for i in range(0,len(branch) - 1, 2):
            if(branch[i] in p.values):
               if(p.values[branch[i]] != branch[i+1]):
                  match = False
                  break
         if(match):
            predictions.append(branch[-1])
            break
   return predictions

def predictFromBranches(comb, rezultat, grane):
   if(isinstance(rezultat, Leaf)):
         return rezultat.decision
   znacajka = rezultat.x
   vrijednost = comb.values[znacajka]
   nepostojeci = True
   for subtree in rezultat.subtrees:
      if(subtree[0] == vrijednost):
         nepostojeci = False
         odgovarajuce_grane = []
         for grana in grane:
            if znacajka in grana:
               index = grana.index(znacajka)
               if(grana[index + 1] == vrijednost):
                  odgovarajuce_grane.append(grana)
         return predictFromBranches(comb, subtree[1], odgovarajuce_grane)
   # slucaj kada nijedna vrijednost ne odgovara
   # res = list(test_dict.keys())[0]
   if(nepostojeci):
      vrijednosti = dict()
      for grana in grane:
         odluka = grana[-1]
         if odluka in vrijednosti:
            vrijednosti[odluka] += 1
         else:
            vrijednosti[odluka] = 1
      res = list({val[0] : val[1] for val in sorted(vrijednosti.items(), key = lambda x: (-x[1], x[0]))}.keys())[0]
      return res
            

def ConfusionMatrix(real_classes, predicted_classes, values_of_y):
   confusion_matrix = []
   n = len(values_of_y)
   for i in range(n):
      confusion_matrix.append([0]*n)
   for i in range(len(real_classes)):
      confusion_matrix[values_of_y.index(real_classes[i])][values_of_y.index(predicted_classes[i])] += 1
   return confusion_matrix

def Accuracy(confusion_matrix, n):
   total = 0
   true = 0
   for i in range(n):
      for j in range(n):
         total += confusion_matrix[i][j]
         if(i==j):
            true += confusion_matrix[i][j]
   return true/total

with open(learning_examples) as csvfile:
   csv_reader = csv.reader(csvfile, delimiter = ',')
   list_of_column_names = []
   D = set()
   first = True
   for row in csv_reader:
      if(first):
         list_of_column_names.append(row)
         first = False
         continue
      combination = Combination(list_of_column_names[0], row)
      D.add(combination) 
      D_whole.add(combination) 
   class_label = list_of_column_names[0][-1]

   X = set(list_of_column_names[0])
   X_whole = set(list_of_column_names[0])
   values_of_y = values_of(D, class_label)
   X.remove(class_label)
   X_whole.remove(class_label)

result = id3(D, D, X, class_label, -1)
branches = createBranches(result)
print("[BRANCHES]:")
printBranches(result,[])

with open(testing_examples) as csvfile:
   csv_reader = csv.reader(csvfile, delimiter = ',')
   P = []
   real_classes = []
   first = True
   for row in csv_reader:
      if(first):
         first = False
         continue
      combination = Combination(list_of_column_names[0][:-1], row[:-1])
      P.append(combination)
      real_classes.append(row[-1])

predicted_classes = []
for p in P:
  predicted_classes.append(predictFromBranches(p, result, branches))
#predicted_classes = Predictions(P)
print("[PREDICTIONS]:", end = " ")
for p in predicted_classes:
   print(p, end = " ")
print()

values_of_y = list(values_of_y)
values_of_y.sort()
confusion_matrix = ConfusionMatrix(real_classes, predicted_classes, values_of_y)
n = len(values_of_y)
accuracy = Accuracy(confusion_matrix, n)
print("[ACCURACY]: {:.5f}".format(accuracy))
print("[CONFUSION_MATRIX]:")
for i in range(n):
   for j in range(n):
      print(confusion_matrix[i][j], end = " ")
   print()
