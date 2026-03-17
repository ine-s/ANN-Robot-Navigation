"""
TP2 - SUIVI D'OBJET
Reseau de neurones avec comportements multiples
"""

import sys
import os
import time
import numpy as np

try:
    from thymiodirect import Thymio
    from thymiodirect.thymio_serial_ports import ThymioSerialPort
except ImportError as e:
    print(f"ERREUR IMPORT: {e}")
    sys.exit(1)

# ============================================================================
# CLASSE COMPORTEMENTS - REPREND TP2 PARTIE 2
# ============================================================================

class PerceptronSuiviObjet:
    """Perceptron pour suivi d'objet avec 4 poids comportementaux"""
    
    def __init__(self, w_fond, w_back, w_pos, w_neg, nom="Comportement"):
        self.nom = nom
        self.w_fond = w_fond
        self.w_back = w_back
        self.w_pos = w_pos
        self.w_neg = w_neg
    
    def somme_ponderee(self, x_centre, x_gauche, x_droit):
        """Calcule les sommes pondérées pour les deux moteurs"""
        z_left = self.w_fond + self.w_back * x_centre + self.w_pos * x_gauche
        z_right = self.w_fond + self.w_back * x_centre + self.w_neg * x_droit
        return z_left, z_right
    
    def activation_saturee(self, z):
        """Fonction d'activation: tanh(z) ∈ [-1, +1]"""
        return np.tanh(z)
    
    def inference(self, x_centre, x_gauche, x_droit):
        """Passe avant complète"""
        z_left, z_right = self.somme_ponderee(x_centre, x_gauche, x_droit)
        y_left = self.activation_saturee(z_left)
        y_right = self.activation_saturee(z_right)
        return (y_left, y_right), (z_left, z_right)
    
    def afficher_config(self):
        """Affiche la configuration"""
        print(f"\n{self.nom}")
        print(f"  w_fond={self.w_fond:.2f}, w_back={self.w_back:.2f}, w_pos={self.w_pos:.2f}, w_neg={self.w_neg:.2f}\n")


# ============================================================================
# DÉFINITION DES COMPORTEMENTS
# ============================================================================

COMPORTEMENTS = {
    "SUIVEUR": PerceptronSuiviObjet(
        w_fond=0.6,      # Avancer solidement
        w_back=-1.2,     # Arrêt agressif si obstacle proche
        w_pos=0.5,       # Virage vers gauche
        w_neg=-0.5,      # Virage vers droite
        nom="SUIVEUR D'OBJET (doux)"
    ),
    "AGRESSIF": PerceptronSuiviObjet(
        w_fond=0.4,      # Avancer lentement
        w_back=-1.5,     # STOP TRÈS agressif
        w_pos=0.7,       # Virages rapides vers gauche
        w_neg=-0.7,      # Virages rapides vers droite
        nom="AGRESSIF (virages rapides)"
    )
}

COMPORTEMENT_ACTIF = "SUIVEUR"

# ============================================================================
# NORMALISATION CAPTEURS
# ============================================================================

def normaliser_capteur(valeur_raw, valeur_min=0, valeur_max=5000):
    """
    Normalise une valeur capteur en [0, 1]
    
    Thymio: capteurs IR retournent ~0 (loin) à ~5000 (proche)
    """
    normalized = (valeur_raw - valeur_min) / (valeur_max - valeur_min)
    return max(0.0, min(1.0, normalized))  # Clamp [0, 1]


def normaliser_capteurs_thymio(capteurs):
    """
    Normalise les 5 capteurs du Thymio
    
    Indices: 0=avant_gauche, 1=avant_centre_gauche, 2=avant_centre, 3=avant_centre_droit, 4=avant_droit
    On utilise: [gauche (0), centre (2), droit (4)]
    """
    # Extractnoyau
    x_gauche = normaliser_capteur(capteurs[0])  # Capteur avant-gauche
    x_centre = normaliser_capteur(capteurs[2])  # Capteur avant-centre
    x_droit = normaliser_capteur(capteurs[4])   # Capteur avant-droit
    
    return x_centre, x_gauche, x_droit


# ============================================================================
# CONFIGURATION THYMIO
# ============================================================================

def on_comm_error(error):
    """Gestion erreur communication"""
    print(f"ERREUR DE COMMUNICATION: {error}")
    os._exit(1)


# Variables globales
done = False
temps_debut = time.time()
iteration = 0
log_data = []

# Afficher les configurations au démarrage
print("\nSUP D'OBJET - RESEAU DE NEURONES")
for nom, comportement in COMPORTEMENTS.items():
    comportement.afficher_config()
print(f"Comportement actif: {COMPORTEMENT_ACTIF}")
print("Contrôles: Bouton avant=ARRÊTER | Bouton central=BASCULER comportement\n")


## Callback Thymio
def obs(node_id):
    """Callback appelé quand les données capteurs arrivent"""
    global done, iteration, COMPORTEMENT_ACTIF, temps_debut, log_data
    
    # Récupérer les données du Thymio
    node = thymio.nodes[node_id]
    
    # ========================================================================
    # BOUTONS DE CONTRÔLE
    # ========================================================================
    
    if node['button.forward']:  # Bouton avant = arrêter
        print("Arrêt du robot")
        done = True
        node['motor.left.target'] = 0
        node['motor.right.target'] = 0
        return
    
    if node['button.center']:  # Bouton central = basculer comportement
        if COMPORTEMENT_ACTIF == "SUIVEUR":
            COMPORTEMENT_ACTIF = "AGRESSIF"
        else:
            COMPORTEMENT_ACTIF = "SUIVEUR"
        print(f"Comportement: {COMPORTEMENT_ACTIF}")
        COMPORTEMENTS[COMPORTEMENT_ACTIF].afficher_config()
        time.sleep(0.5)
        return
    
    # ========================================================================
    # LECTURE ET NORMALISATION CAPTEURS
    # ========================================================================
    
    capteurs = node['prox.horizontal']  # [avant_gauche, ..., avant_centre, ..., avant_droit]
    x_centre, x_gauche, x_droit = normaliser_capteurs_thymio(capteurs)
    
    # ========================================================================
    # INFÉRENCE RÉSEAU
    # ========================================================================
    
    comportement = COMPORTEMENTS[COMPORTEMENT_ACTIF]
    (y_left, y_right), (z_left, z_right) = comportement.inference(x_centre, x_gauche, x_droit)
    
    # ========================================================================
    # CONVERSION EN VITESSE MOTEUR
    # ========================================================================
    
    # y ∈ [-1, +1] → vitesse ∈ [-500, +500]
    MAX_SPEED = 400  # Limiter pour sécurité
    
    v_left = int(y_left * MAX_SPEED)
    v_right = int(y_right * MAX_SPEED)
    
    # ========================================================================
    # ENVOI COMMANDES AUX MOTEURS
    # ========================================================================
    
    node['motor.left.target'] = v_left
    node['motor.right.target'] = v_right


# ============================================================================
# MAIN
# ============================================================================

try:
    # Connexion Thymio
    print("Connexion au Thymio...")
    port = ThymioSerialPort.search_for_thymio_serial_port()
    if port is None:
        print("Aucun Thymio trouvé!")
        sys.exit(1)
    
    thymio = Thymio(port=port, on_connect=lambda node_id: print(f"Connecté: {node_id}"))
    thymio.callback_update(obs)
    
    time.sleep(1)
    print("Démarrage...\n")
    
    while not done:
        time.sleep(0.1)
    
    # Arrêt propre
    print("\nSession terminée")
    thymio.close()

except KeyboardInterrupt:
    print("\nArrêt manuel")
    thymio.close()
    sys.exit(0)
except Exception as e:
    print(f"Erreur: {e}")
    try:
        thymio.close()
    except:
        pass
    sys.exit(1)
