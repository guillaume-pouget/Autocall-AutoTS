import numpy as np


class Autocall:
    def __init__(self, spot_initial, coupon, barriere_autocall, barriere_protection, 
                 maturite, observation_dates, nominal):
        
        self.spot_initial = spot_initial
        self.coupon = coupon
        self.barriere_autocall = barriere_autocall
        self.barriere_protection = barriere_protection
        self.maturite = maturite
        self.observation_dates = observation_dates
        self.nominal = nominal

    def spot_paths(self, rate, vol, nombre_paths):
        nombre_observations = len(self.observation_dates)
        dt = self.maturite / nombre_observations
        
        paths = np.zeros((nombre_paths, nombre_observations + 1))

        paths[:, 0] = self.spot_initial #rempli la première colonne avec le niveau initial

        for observation in range(1, nombre_observations + 1):
            random_numbers = np.random.normal(0,1,nombre_paths) #crée un vecteur aléatoire

            paths[:, observation] = (paths[:, observation - 1]* np.exp((rate - 0.5 * vol ** 2) * dt
                    + vol * np.sqrt(dt) * random_numbers)) #ajoute les valeurs des modélisations dans la matrice
            

        return paths

    def payoff(self, path):
        nombre_observations = len(self.observation_dates)
        dt = self.maturite / nombre_observations

        # On ignore path[0], qui correspond au spot initial
        for position, prix in enumerate(path[1:], start=1):
            rendement = (prix / self.spot_initial) * 100

            if rendement >= self.barriere_autocall:
                payoff_autocall = self.nominal * (1 + self.coupon)
                date_paiement = position * dt

                return payoff_autocall, date_paiement

        # Si aucun autocall n'a été déclenché,
        # on analyse le dernier prix à maturité
        dernier_prix = path[-1]
        dernier_rendement = (
            dernier_prix / self.spot_initial) * 100

        if dernier_rendement >= self.barriere_protection:
            payoff_final = self.nominal
        else:
            payoff_final = (self.nominal* dernier_prix/ self.spot_initial)

        return payoff_final, self.maturite

    def price(self, rate, vol, nombre_paths):
        paths = self.spot_paths(rate, vol, nombre_paths)

        discounted_payoffs = []

        for path in paths:
            payoff, payment_date = self.payoff(path)

            discounted_payoff = (payoff* np.exp(-rate * payment_date))

            discounted_payoffs.append(discounted_payoff)

        return np.mean(discounted_payoffs)

    def parametres_TS(self, prix):
        Parametres  = {"Reference Price": self.spot_initial , "Nominal": self.nominal, "Coupon": self.coupon,
                       "Barrière d'autocall": self.barriere_autocall, "Barrière de protection" : self.barriere_protection,
                       "Maturité":self.maturite, "Prix": prix}
        return Parametres

#REMPLIR UNE TS
#Ici c'est un fichier texte que je remplis mais avec le système de balise 
#on pourrait aussi modifier une TS sur Word et en créer un PDF.

def remplir_template(file_location, output_location, parametres):
    with open(file_location, "r", encoding="utf-8") as fichier:
        contenu = fichier.read()

    print("Contenu lu :", repr(contenu))
    print("Paramètres :", parametres)

    for cle, valeur in parametres.items():
        marqueur = "{{" + cle + "}}"
        contenu = contenu.replace(marqueur, str(valeur))

    with open(output_location, "w", encoding="utf-8") as fichier:
        fichier.write(contenu)

    print("TS créée")



autocall_01 = Autocall(100, 0.08, 100, 60, 5,[1,2,3,4,5], 1000)

prix_autocall = autocall_01.price(rate=0.05, vol=0.25, nombre_paths=10000)

parametres = autocall_01.parametres_TS(prix_autocall)

remplir_template("TS_template.txt", "term_sheet_remplie.txt", parametres)