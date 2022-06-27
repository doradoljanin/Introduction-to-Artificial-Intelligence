import sys

# zastavice
resolution = False
cooking = False
klauzule_filename = ""
korisnicke_naredbe_filename = ""

class Clause:

   def __init__(self, literals, parents):
    factorised = set(literals) #time je faktorizacija osigurana jer set nema duplikata
    self.literals = [] 
    for literal in factorised:
       self.literals += [literal]
    self.parents = []
    for parent in parents:
       self.parents += [parent]
   
   def __eq__(self, other):
    if isinstance(other, Clause):
       if(len(set(other.literals) - set(self.literals)) != 0):
          return False
       if(len(set(self.literals) - set(other.literals)) != 0):
          return False
       return True
    return False
   
   def __str__(self):
      if(len(self.literals) == 0):
         return ""
      clause_to_string = self.literals[0]
      for i in range(1, len(self.literals), 1):
         clause_to_string += " v " + self.literals[i]
      return clause_to_string

   def __hash__(self):
      frozen_clause = frozenset(self.literals)
      return hash(frozen_clause)


if(len(sys.argv) < 3):
   print("Invalid number of arguments")
   exit(1)
# Prvi argument bit ´ce kljuˇcna rijeˇc
# “resolution”, kojom se oznaˇcava da se treba pokrenuti algoritam rezolucije opovrgavanjem,
# a drugi argument bit ´ce putanja do datoteke s popisom klauzula.
if(sys.argv[1] == "resolution"):
   resolution = True
   klauzule_filename = sys.argv[2]
if(sys.argv[1] == "cooking"):
   if(len(sys.argv) < 4):
      print("Invalid number of arguments")
      exit(1)
   cooking = True
   klauzule_filename = sys.argv[2]
   korisnicke_naredbe_filename = sys.argv[3]

#1. Ucitavanje podataka
if(korisnicke_naredbe_filename!=""):
   #(1) datoteke s korisnickim naredbama
   try:
      f = open(korisnicke_naredbe_filename, encoding="utf8")
   except FileNotFoundError:
      print("File " + korisnicke_naredbe_filename + " not found.")
      exit(1)
   naredbe = []
   for line in f.readlines():
      if(line.startswith("#")): #zanemariti komentare
         continue
      #Svaki redak korisniˇckih naredbi sadrˇzi jednu klauzulu te identifikator namjere korisnika
      #zadnji znak u svakoj liniji je identifikator namjere
      identifikator_namjere = line[-2]
      line = line.lower() # klauzula je lista literala (atoma ili negiranih atoma)
      klauzula_array = line.split(" v ")
      klauzula = []
      for i in range(len(klauzula_array) - 1):
         klauzula += [klauzula_array[i]]
      klauzula += [(klauzula_array[len(klauzula_array) - 1])[:-3]]
      naredbe.append([Clause(klauzula, []), identifikator_namjere])

if(klauzule_filename!=""):
   #(1) datoteke s popisom klauzula
   try:
      f = open(klauzule_filename, encoding="utf8")
   except FileNotFoundError:
      print("File " + klauzule_filename + " not found.")
      exit(1)
   lineList = f.readlines()
   klauzule = []
   for line in lineList:
      if(line.startswith("#")): #zanemariti komentare
         continue
      #U svakom retku datoteke nalazi se po jedna klauzula zapisana u konjunktivnoj normalnoj formi (CNF)
      line = line.lower()
      line = line.split(" v ") # klauzula je lista literala (atoma ili negiranih atoma)
      if(line[-1][-1] == "\n"):
         line[-1] = line[-1][:-1] #maknuti \n
      klauzula = []
      for i in range(len(line)):
         klauzula += [line[i]]
      klauzule.append(Clause(klauzula, []))

def negacijaLiterala(literal):
   if(literal.startswith("~")):
      literal = literal[1:]
   else:
      literal = "~" + literal
   return literal

# izmedju literala u klauzuli je znak V (ili), nakon negacije je između negiranih literala znak I,
def negacijaKlauzule(klauzula):
   negirano = [] # to znaci da iz jedne klauzule moze nastati vise klauzula --> lista
   for literal in klauzula.literals:
      literal = negacijaLiterala(literal)
      novaklauzula = Clause([literal], [])
      negirano.append(novaklauzula)
   return negirano

def isNIL(resolvent):
   if(len(resolvent.literals) == 0):
      return True
   return False

def isTautology(clause):
   for i in range(len(clause.literals)):
      literal = negacijaLiterala(clause.literals[i])
      for j in range(len(clause.literals)):
         if(literal == clause.literals[j]):
            return True
   return False

#Strategija skupa potpore: barem jedna roditeljska klauzula uvijek dolazi iz SoS
def selectClauses(F, SoS, klauzule, already_combined):
   selectedClauses = []
   for klauzula1 in SoS:
      for klauzula2 in F+SoS:
         if((klauzule.index(klauzula1) + 1) in already_combined and (klauzule.index(klauzula2) + 1) in already_combined[(klauzule.index(klauzula1) + 1)]):
            continue
         for i in range(len(klauzula1.literals)):
            trazeni_literal = negacijaLiterala(klauzula1.literals[i])
            if(trazeni_literal in klauzula2.literals):
               selectedClauses.append([klauzula1, klauzula2])
   return selectedClauses

def plResolve(klauzula1, klauzula2):
   rezolventi = []
   komplementarni_parovi_literala = []
   for literal1 in klauzula1.literals:
      negirani = negacijaLiterala(literal1)
      for literal2 in klauzula2.literals:
         if(literal2 == negirani):
            komplementarni_parovi_literala.append([literal1, literal2])
   for par in komplementarni_parovi_literala:
      rezolvent = []
      for literal in klauzula1.literals:
         if(literal != par[0]):
            rezolvent += [literal]
      for literal in klauzula2.literals:
         if(literal != par[1]):
            rezolvent += [literal]
      novaklauzula = Clause(rezolvent, [klauzula1, klauzula2])
      rezolventi.append(novaklauzula)
   return rezolventi

def ispisFalse(klauzule, br_na_pocetku):
   rbr = 0
   for klauzula in klauzule:
      print(str(klauzule.index(klauzula) + 1) + ". " + str(klauzula))
      rbr += 1
      if(rbr == br_na_pocetku):
         print("===============")
         return

def podskup(kraca_klauzula, duza_klauzula):
   for literal in kraca_klauzula.literals:
      if(literal not in duza_klauzula.literals):
         return False
   return True

def ukloniRedundantne(klauzule):
   ociscene = []
   for i in range(len(klauzule)):
      trebaMaknut = False
      for j in range(len(klauzule)):
         if(len(klauzule[i].literals) > len(klauzule[j].literals)):
            if(podskup(klauzule[j], klauzule[i])):
               trebaMaknut = True
      if(trebaMaknut == False):
         ociscene.append(klauzule[i])
   return ociscene

def vratiSveKoristene(NILparent1, NILparent2, clauses):
   koristeni = {clauses.index(NILparent1) + 1, clauses.index(NILparent2) + 1}
   #koristeni = {(roditelji[tuple(sorted(NILparent1))])[0], (roditelji[tuple(sorted(NILparent1))])[1]}
   #clauses.index(klauzula) + 1 --> redni broj klauzule u listi clauses
   while(True):
      novi = set()
      for broj in koristeni:
         dijete = clauses[broj - 1]
         if(len(dijete.parents) != 0):
            novi.add( clauses.index(dijete.parents[0]) + 1 )
            novi.add( clauses.index(dijete.parents[1]) + 1 )
      svi_unutra = True
      for broj in novi:
         if(broj not in koristeni):
            svi_unutra = False
      if(svi_unutra):
         break
      for broj in novi:
         koristeni.add(broj)
   return koristeni #vraca redne brojeve klauzula koje su koristene na putu do cilja

#trebate koristiti (1) upravljaˇcku strategiju skupa potpore i (2) strategiju brisanja
def plResolution(F, G):
   #klauzule_ulaznih_premisa = F
   notG = negacijaKlauzule(G) # notG je lista klauzula (jedne ili vise njih)
   clauses = F + notG
   clauses = ukloniRedundantne(clauses)
   F = [] #mozda su se izbacile neke redundantne klauzule iz F pa ga updejtamo
   for clause in clauses:
      if clause not in notG:
         F.append(clause)
   vec_kombinirane_klauzule = {}
   new = []
   #Skup potpore (SoS): klauzule dobivene negacijom cilja (notG) i sve novoizvedene klauzule (new)
   SoS = notG + new
   while(True):
      #moramo kombinirati klauzule ulaznih premisa (F) s klauzulama iz SoS (notG i new)
      odabrani_parovi = selectClauses(F, SoS, clauses, vec_kombinirane_klauzule)
      for pair in odabrani_parovi: #pair je lista duljine 2
         for resolvent in plResolve(pair[0], pair[1]):
            if(pair[0] not in clauses or pair[1] not in clauses): #ako smo ih u medjuvremenu maknuli zbog redundancije
               continue
            bez_redundanata = ukloniRedundantne(clauses + [resolvent])
            if(clauses + [resolvent] != bez_redundanata):
               #ako je rezolvent redundantan samo ga zanemari
               if(resolvent not in bez_redundanata):
                  continue
               #ako dodavanjem ovog rezolventa neka druga klauzula postaje redundantna (osim naravno njegovih roditelja),
               #potrebno ju je izbaciti
               else:
                  redundanti_set = set(clauses) - set(bez_redundanata)
                  for redundant in (redundanti_set):
                     if(redundant != pair[0] and redundant != pair[1] and (clauses.index(redundant) + 1) not in vec_kombinirane_klauzule):
                        rbr = clauses.index(redundant) + 1
                        #update rednih brojeva u vec_kombinirane_klauzule
                        pom = {}
                        for broj in vec_kombinirane_klauzule:
                           if(broj > rbr):
                              pom[broj - 1] = vec_kombinirane_klauzule[broj]
                           else:
                              pom[broj] = vec_kombinirane_klauzule[broj]
                        vec_kombinirane_klauzule = pom.copy()
                        for broj in vec_kombinirane_klauzule:
                           for i in range(len(vec_kombinirane_klauzule[broj])):
                              if((vec_kombinirane_klauzule[broj])[i] > rbr):
                                 (vec_kombinirane_klauzule[broj])[i] -= 1
                        clauses.remove(redundant)
                  for clause in F:
                     if clause not in clauses:
                        F.remove(clause)
                  for clause in SoS:
                     if clause not in clauses:
                        SoS.remove(clause)
            #clauses.index(klauzula) + 1 --> redni broj klauzule u listi clauses
            # dodavanje rezolventa
            if(clauses.index(pair[0]) + 1 not in vec_kombinirane_klauzule):
               vec_kombinirane_klauzule[clauses.index(pair[0]) + 1] = []
            if(clauses.index(pair[1]) + 1 not in vec_kombinirane_klauzule):
               vec_kombinirane_klauzule[clauses.index(pair[1]) + 1] = []
            vec_kombinirane_klauzule[clauses.index(pair[0]) + 1] += [clauses.index(pair[1]) + 1]
            vec_kombinirane_klauzule[clauses.index(pair[1]) + 1] += [clauses.index(pair[0]) + 1]
            if(isNIL(resolvent)):
               #ako je uspjeˇsno dokazana, potrebno je ispisati i rezolucijski postupak koji je vodio do NIL.
               # smiju se ispisivati samo klauzule koje su koristene na putu do izvedenog NIL-a
               rbr = 0
               koristene_klauzule = vratiSveKoristene(pair[0], pair[1], clauses)
               redundanti_set = set()
               for index in range(len(clauses)):
                  if((index + 1) not in koristene_klauzule):
                     redundanti_set.add(clauses[index])
               for redundant in (redundanti_set):
                  clauses.remove(redundant)
               pomF = []
               pomSoS = []
               pomnotG = []
               for clause in F:
                  if clause in clauses:
                     pomF = pomF + [clause]
               for clause in SoS:
                  if clause in clauses:
                     pomSoS = pomSoS + [clause]
               for clause in notG:
                  if clause in clauses:
                     pomnotG = pomnotG + [clause]
               F = []
               SoS = []
               notG = []
               for clause in pomF:
                  F = F + [clause]
               for clause in pomSoS:
                  SoS = SoS + [clause]
               for clause in pomnotG:
                  notG = notG + [clause]
               #ispis za True
               rbr = 1
               for klauzula in clauses:
                  print()
                  print(str(clauses.index(klauzula) + 1) + ". " + str(klauzula), end="")
                  rbr += 1
                  if(rbr == len(F) + len(notG) + 1):
                     print()
                     print("===============", end="")
                  if( len(klauzula.parents) != 0):     
                     print( " (" + str(clauses.index(klauzula.parents[0]) + 1) + ", " + str(clauses.index(klauzula.parents[1]) + 1) + ")", end="") 
               print()
               print(str(len(clauses) + 1) + ". NIL (" + str(clauses.index(pair[1]) + 1) + ", " + str(clauses.index(pair[0]) + 1) + ")" )
               print("===============")
               return True
            #ako je tautologija (nevazna klauzula) : continue
            if(isTautology(resolvent)):
               continue
            if(resolvent not in new):
               new = new + [resolvent]
      svi_unutra = True
      for clause in new:
         if(clause not in clauses):
            SoS.append(clause)
            svi_unutra = False
      if(svi_unutra):
         ispisFalse(clauses, len(F) + len(notG))
         return False
      new = []
      for clause in SoS:
         if(clause not in clauses):
            clauses.append(clause)      

# Rezolucija opovrgavanjem
if(resolution == True):
   klauzule_ulaznih_premisa = klauzule[:-1]
   #zadnju klauzulu iz datoteke popisa klauzula smatramo
   #ciljnom klauzulom (onom koju pokuˇsavamo dokazati)
   ciljna_klauzula = klauzule[-1]
   if(plResolution(klauzule_ulaznih_premisa, ciljna_klauzula)):
      print("[CONCLUSION]: " + str(ciljna_klauzula) + " is true")
   else:
      print("[CONCLUSION]: " + str(ciljna_klauzula) + " is unknown")

#oznaˇcava da se treba pokrenuti sustav kuharskog asstenta
if(cooking == True):
   # klauzule su klauzule ulaznih premisa
   print("Constructed with knowledge:")
   for klauzula in klauzule:
      print(str(klauzula))
   for redak in naredbe:
      print()
      print("User’s command: ", end = "")
      print(str(redak[0]), end = "")
      print(" " + redak[1])
      if(redak[1] == "+"):
         klauzule.append(redak[0])
         print("Added ", end = "")
         print(str(redak[0]))
      if(redak[1] == "-"):
         klauzule.remove(redak[0])
         print("Removed ", end = "")
         print(str(redak[0]))
      if(redak[1] == "?"):
         ciljna_klauzula = redak[0]
         if(plResolution(klauzule, ciljna_klauzula)):
            print("[CONCLUSION]: " + str(ciljna_klauzula) + " is true")
         else:
            print("[CONCLUSION]: " + str(ciljna_klauzula) + " is unknown")