import sys
import time
import heapq

'''
kod se mora moci pokrenuti tako da prima iduce argumente putem komandne linije:
• --alg: kratica za algoritam za pretrazivanje (vrijednosti: bfs, ucs, ili astar), -->za algoritme BFS i UCS
• --ss: putanja do opisnika prostora stanja, -->za algoritme BFS i UCS,  provjere optimisticnosti i konzistentnosti heuristika
• --h: putanja do opisnika heuristike, -->za algoritme BFS, UCS i A*,  provjere optimisticnosti i konzistentnosti heuristika
• --check-optimistic: zastavica koja signalizira da se za danu heuristiku zeli provjeriti optimisticnost,
• --check-consistent: zastavica koja signalizira da se za danu heuristiku zeli provjeriti konsistentnost
rjesenje prima argumente neovisno o njihovom redoslijedu
'''

broj_argumenata = len(sys.argv)
alg = ""
ss = ""
h = ""
check_optimistic = False
check_consistent = False

for i in range(1,broj_argumenata,1):
   if(sys.argv[i].startswith("--") == False):
      if(sys.argv[i-1].startswith("--") == False):
         print("Incorrect use of arguments.")
         exit(1)
   if(sys.argv[i] == "--alg"):
      alg = sys.argv[i+1]
      continue
   if(sys.argv[i] == "--ss"):
      ss = sys.argv[i+1]
      continue
   if(sys.argv[i] == "--h"):
      h = sys.argv[i+1]
      continue
   if(sys.argv[i] == "--check-optimistic"):
      check_optimistic = True
      continue
   if(sys.argv[i] == "--check-consistent"):
      check_consistent = True
      continue

#REDOSLIJED JE NEBITAN
#KOD ODREDJENOG ALGORITMA OBAVEZNO SE ZADAJE ALGORITAM i --ss
#python solution.py --alg bfs --ss istra.txt
#python solution.py --alg ucs --ss istra.txt
#kod A* se zadaje i --h
#python solution.py --alg astar --ss istra.txt --h istra_heuristic.txt
if(alg=="bfs" or alg=="ucs" or alg=="astar" or alg == "" and (check_consistent == True or check_optimistic == True)):
   if(ss==""):
      print("Incorrect use of arguments.")
      exit(1)  
   if(alg=="astar"):
      if(h==""):
         print("Incorrect use of arguments.")
         exit(1)
else:
   print("Incorrect algorithm name.")
   exit(1)
#KOD PROVJERE OPTIMISTICNOSTI I KONZISTENTNOSTI NE ZADAJE SE ALGORITAM, ali se obavezno zadaje --ss i --h
#python solution.py --ss istra.txt --h istra_heuristic.txt --check-optimistic
#python solution.py --ss istra.txt --h istra_heuristic.txt --check-consistent
if(check_consistent or check_optimistic):
   if(alg!="" or ss=="" or h==""):
      print("Incorrect use of arguments.")
      exit(1)

#1. Ucitavanje podataka
if(ss!=""):
   #(1) opisnik prostora stanja
   prostor_stanja_filename = ss
   try:
      f = open(prostor_stanja_filename, encoding="utf8")
   except FileNotFoundError:
      print("File " + h + " not found.")
      exit(1)
   pocetno_stanje = ""
   druga_linija = ""
   ciljna_stanja = set()
   funkcija_prijelaza = {} #dictionary
   for line in f.readlines():
      if(line.startswith("#")): #zanemariti komentare
         continue
      #Prva linija datoteke koja nije komentar sadrzi pocetno stanje
      if(pocetno_stanje == ""):
         pocetno_stanje = line
         pocetno_stanje = pocetno_stanje[:-1]
         continue
      #u drugoj liniji nalaze ciljna stanja odvojena s jednim razmakom
      if(druga_linija == ""):
         druga_linija = line
         druga_linija = druga_linija.split()
         for stanje in druga_linija:
            ciljna_stanja.add(stanje)
         continue
      #Preostale linije opisnika prostora stanja sastoje se od zapisa funkcije prijelaza
      prijelaz = line.split()
      stanje = prijelaz[0]
      stanje = stanje[:-1]
      d = len(prijelaz)
      sljedbenici_i_cijene = {} #dictionary
      for i in range(1,d,1):
         sljedbenik = prijelaz[i].split(",")
         sljedece = sljedbenik[0]
         cijena = sljedbenik[1]
         sljedbenici_i_cijene[sljedece] = cijena
      funkcija_prijelaza[stanje] = sljedbenici_i_cijene

#(2) opisnik heuristike
if(h!=""):
   heuristika_filename = h
   try:
      f = open(heuristika_filename, encoding="utf8")
   except FileNotFoundError:
      print("File " + h + " not found.")
      exit(1)
   heuristicka_funkcija = {} #dictionary
   for line in f.readlines():
      stanje_heuristika = line.split()
      stanje = stanje_heuristika[0]
      stanje = stanje[:-1]
      heuristika = stanje_heuristika[1]
      heuristicka_funkcija[stanje] = heuristika

#Algoritmi pretrazivanja

paths = {}
costs = {}
posjecena_stanja = set()

class Node:
   def __init__(self, name, costsum):
      self.name = name
      self.costsum = costsum
   def __lt__(self, other):
      return (self.costsum, self.name) < (other.costsum, other.name)
   def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.costsum == other.costsum
        else:
            return False
   def __hash__(self):
    return hash(self.name) ^ hash(self.costsum)

#f(n) = g(n) + h(state(n))
class Nodef:
   def __init__(self, name, costsum, heuristic):
      self.name = name
      self.f = costsum + float(heuristic)
   def __lt__(self, other):
      return (self.f, self.name) < (other.f, other.name)
   def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.f == other.f
        else:
            return False
   def __hash__(self):
    return hash(self.name) ^ hash(self.f)


def breadthFirstSearch(pocetno_stanje,funkcija_prijelaza,ciljna_stanja):
   lista_otvorenih_cvorova = [pocetno_stanje]
   paths[pocetno_stanje] = [pocetno_stanje]
   costs[pocetno_stanje] = 0.0
   while(len(lista_otvorenih_cvorova) != 0):
      n = lista_otvorenih_cvorova.pop(0)
      posjecena_stanja.add(n) 
      if(n in ciljna_stanja):
         return n
      sljedbenici_dict = funkcija_prijelaza[n] #dictionary
      for m in sljedbenici_dict:
         if(m not in posjecena_stanja):
            lista_otvorenih_cvorova.append(m)
            if m not in paths:
               paths[m] = paths[n] + [m]
               costs[m] = round(float(costs[n]), 1) + round(float(sljedbenici_dict[m]), 1)
   return ""

def uniformCostSearch(pocetno_stanje,funkcija_prijelaza, ciljna_stanja):
   lista_otvorenih_cvorova = [Node(pocetno_stanje, 0.0)]
   heapq.heapify(lista_otvorenih_cvorova) # using heapify to convert list into heap
   paths[pocetno_stanje] = [pocetno_stanje]
   costs[pocetno_stanje] = 0.0
   while(len(lista_otvorenih_cvorova) != 0):
      n = heapq.heappop(lista_otvorenih_cvorova).name
      posjecena_stanja.add(n)
      if(n in ciljna_stanja):
         return n
      sljedbenici_dict = funkcija_prijelaza[n] #dictionary
      for m in sljedbenici_dict:
         if(m not in posjecena_stanja): 
            # cvorovi se u listi open sortiraju po cijeni 
            #U slucaju vise cvorova s istim prioritetom u listi open u algoritmima UCS i A*, 
            # redoslijed njihovog otvaranja definiran je prema abecednom redu gledajuci nazive cvora
            if( (m in costs) and (costs[m] > costs[n] + int(sljedbenici_dict[m])) or (m not in costs) ):
                  costs[m] = costs[n] + round(float(sljedbenici_dict[m]), 1)
                  paths[m] = paths[n] + [m]
            M = Node(m, costs[m])
            heapq.heappush(lista_otvorenih_cvorova,M)
   return ""

def aStarSearch(pocetno_stanje,funkcija_prijelaza, ciljna_stanja, heuristicka_funkcija):
   costs[pocetno_stanje] = 0.0
   paths[pocetno_stanje] = [pocetno_stanje]
   lista_otvorenih_cvorova = [Nodef(pocetno_stanje, costs[pocetno_stanje], heuristicka_funkcija[pocetno_stanje])]
   heapq.heapify(lista_otvorenih_cvorova)
   zatvoreni = set()
   while(len(lista_otvorenih_cvorova) != 0):
      n = heapq.heappop(lista_otvorenih_cvorova).name
      posjecena_stanja.add(n)
      if(n in ciljna_stanja):
         return n
      sljedbenici_dict = funkcija_prijelaza[n] #dictionary
      zatvoreni.add(n)
      for m in sljedbenici_dict:
         if(m not in posjecena_stanja): 
            # cvorovi se u listi open sortiraju po cijeni 
            #U slucaju vise cvorova s istim prioritetom u listi open u algoritmima UCS i A*,
            #  redoslijed njihovog otvaranja definiran je prema abecednom redu gledajuci nazive cvora
            if( (m in costs) and (costs[m] > costs[n] + int(sljedbenici_dict[m])) or (m not in costs) ):
                  costs[m] = costs[n] + round(float(sljedbenici_dict[m]), 1)
                  paths[m] = paths[n] + [m]
            M = Nodef(m, costs[m], heuristicka_funkcija[m])
            heapq.heappush(lista_otvorenih_cvorova,M)
   return ""

#Heuristika h je optimisticna ili dopustiva (engl. optimistic, admissible)
#akko nikad ne precjenuje, tj. nikad nije veca od prave cijene do cilja
def checkOptimistic(funkcija_prijelaza, heuristicka_funkcija):
   optimisticna = True
   for stanje in funkcija_prijelaza:
      global posjecena_stanja
      posjecena_stanja = set()
      global costs
      costs = {}
      rjesenje = uniformCostSearch(stanje,funkcija_prijelaza, ciljna_stanja)
      if(rjesenje == ""):
         return False
      stvarne_cijene[stanje] = costs[rjesenje]
      if( round(float(heuristicka_funkcija[stanje]), 1) > round(float(costs[rjesenje]), 1) ):
         print("[CONDITION]: [ERR] h(" + stanje + ") <= h*: " + str(round(float(heuristicka_funkcija[stanje]), 1)) + " <= " + str(round(float(costs[rjesenje]), 1)))
         optimisticna = False
      else:
         print("[CONDITION]: [OK] h(" + stanje + ") <= h*: " + str(round(float(heuristicka_funkcija[stanje]), 1)) + " <= " + str(round(float(costs[rjesenje]), 1)))
   return optimisticna

#Heuristika h je konzistentna ili monotona akko:
#∀(s2, c) ∈ succ(s1). h(s1) ≤ h(s2) + c
def checkConsistent(funkcija_prijelaza, heuristicka_funkcija):
   konzistentna = True
   for stanje in funkcija_prijelaza:
      sljedbenici_dict = funkcija_prijelaza[stanje] #dictionary
      for sljedbenik in sljedbenici_dict:
         #ISPIS!!!
         if(round(float(heuristicka_funkcija[stanje]), 1) > round(float(heuristicka_funkcija[sljedbenik]), 1) + round(float(sljedbenici_dict[sljedbenik]), 1)):
            konzistentna = False
            
            print("[CONDITION]: [ERR] h(" + stanje + ") <= h(" + sljedbenik + ") + c: " + str(round(float(heuristicka_funkcija[stanje]), 1)) + " <= " + str(round(float(heuristicka_funkcija[sljedbenik]), 1)) + " + " + str(round(float(sljedbenici_dict[sljedbenik]), 1)))
         else:
            print("[CONDITION]: [OK] h(" + stanje + ") <= h(" + sljedbenik + ") + c: " + str(round(float(heuristicka_funkcija[stanje]), 1)) + " <= " + str(round(float(heuristicka_funkcija[sljedbenik]), 1)) + " + " + str(round(float(sljedbenici_dict[sljedbenik]), 1)))
   return konzistentna

if(alg!=""):
   #1. Algoritam pretrazivanja u sirinu (BFS)
   if(alg=="bfs"):
      print("# BFS")
      #Kod BFS algoritma, potrebno je sortirati abecednim redom susjede pojedinog cvora,
      #  pa ih onda tim poretkom dodavati u listu open
      for stanje in funkcija_prijelaza:
         sljedbenici_dict = funkcija_prijelaza[stanje]
         dictionary_items = sljedbenici_dict.items()
         sorted_items = sorted(dictionary_items)
         sljedbenici_dict_sorted_by_key = {}
         for item in sorted_items:
            sljedbenici_dict_sorted_by_key[item[0]] = item[1]
         funkcija_prijelaza[stanje] = sljedbenici_dict_sorted_by_key
      rjesenje = breadthFirstSearch(pocetno_stanje,funkcija_prijelaza,ciljna_stanja)
      if(rjesenje != ""):
         print("[FOUND_SOLUTION]: yes")
      else:
         print("[FOUND_SOLUTION]: no")
      print("[STATES_VISITED]: " + str(len(posjecena_stanja)))
      print("[PATH_LENGTH]: " + str(len(paths[rjesenje])))
      print("[TOTAL_COST]: " + str(costs[rjesenje]))
      path = "" + paths[rjesenje].pop(0)
      for cvor in paths[rjesenje]:
         path = path + " => " + cvor
      print("[PATH]: " + path)
      
   #2. Algoritam pretrazivanja s jednolikom cijenom (UCS)
   if(alg=="ucs"):
      print("# UCS")
      rjesenje = uniformCostSearch(pocetno_stanje,funkcija_prijelaza,ciljna_stanja)
      if(rjesenje != ""):
         print("[FOUND_SOLUTION]: yes")
      else:
         print("[FOUND_SOLUTION]: no")
      print("[STATES_VISITED]: " + str(len(posjecena_stanja)))
      print("[PATH_LENGTH]: " + str(len(paths[rjesenje])))
      print("[TOTAL_COST]: " + str(costs[rjesenje]))
      path = "" + paths[rjesenje].pop(0)
      for cvor in paths[rjesenje]:
         path = path + " => " + cvor
      print("[PATH]: " + path)
      
   #3. Algoritam A* (A-STAR)
   if(alg=="astar"):
      print("# A-STAR " + heuristika_filename)
      #U slucaju vise cvorova s istim prioritetom u listi open u algoritmima UCS i A*, 
      # redoslijed njihovog otvaranja definiran je prema abecednom redu gledajuci nazive cvora
      rjesenje = aStarSearch(pocetno_stanje,funkcija_prijelaza,ciljna_stanja,heuristicka_funkcija)
      if(rjesenje != ""):
         print("[FOUND_SOLUTION]: yes")
      else:
         print("[FOUND_SOLUTION]: no")
      print("[STATES_VISITED]: " + str(len(posjecena_stanja)))
      print("[PATH_LENGTH]: " + str(len(paths[rjesenje])))
      print("[TOTAL_COST]: " + str(costs[rjesenje]))
      path = "" + paths[rjesenje].pop(0)
      for cvor in paths[rjesenje]:
         path = path + " => " + cvor
      print("[PATH]: " + path)

if(check_consistent):
   print("# HEURISTIC-CONSISTENT " + heuristika_filename)
   if(checkConsistent(funkcija_prijelaza, heuristicka_funkcija)):
      print("[CONCLUSION]: Heuristic is consistent.")
   else:
      print("[CONCLUSION]: Heuristic is not consistent.")

if(check_optimistic):
   print("# HEURISTIC-OPTIMISTIC " + heuristika_filename)
   stvarne_cijene = {}
   if(checkOptimistic(funkcija_prijelaza, heuristicka_funkcija)):
      print("[CONCLUSION]: Heuristic is optimistic.")
   else:
      print("[CONCLUSION]: Heuristic is not optimistic.")