"""
TP2 - ÉVITEMENT D'OBSTACLES
Stratégie: Recul progressif quand obstacle détecté
"""

import sys
import os
import time
import numpy as np

try:
    from thymiodirect import Thymio
    from thymiodirect.thymio_serial_ports import ThymioSerialPort
except ImportError:
    print("❌ Erreur: thymiodirect non trouvé")
    print("Assurez-vous de lancer ce script avec l'environnement Thymio correct!")
    sys.exit(1)


# ============================================================================
# CLASSE PERCEPTRON - ÉVITEMENT D'OBSTACLES
# ============================================================================

class PerceptronEvitementObstacles:
    """Perceptron pour évitement d'obstacles avec 2 poids comportementaux"""
    
    def __init__(self, w_biais, w_capteur, nom="Comportement"):
        self.nom = nom
        self.w_biais = w_biais      # w0
        self.w_capteur = w_capteur  # w1, w2
    
    def somme_ponderee(self, x_gauche, x_droit):
        """Calcule les sommes pondérées pour les deux moteurs"""
        # Moteur gauche réagit au capteur gauche
        z_left = self.w_biais + self.w_capteur * x_gauche
        # Moteur droit réagit au capteur droit
        z_right = self.w_biais + self.w_capteur * x_droit
        return z_left, z_right
    
    def activation_saturee(self, z):
        """Fonction d'activation: tanh(z) ∈ [-1, +1]"""
        return np.tanh(z)
    
    def inference(self, x_gauche, x_droit):
        """Passe avant complète"""
        z_left, z_right = self.somme_ponderee(x_gauche, x_droit)
        y_left = self.activation_saturee(z_left)
        y_right = self.activation_saturee(z_right)
        return (y_left, y_right), (z_left, z_right)


# ============================================================================
# DÉFINITION DES STRATÉGIES D'ÉVITEMENT
# ============================================================================

STRATEGIES = {
    "BIAIS_TRÈS_FAIBLE": PerceptronEvitementObstacles(
        w_biais=-0.2,
        w_capteur=-0.5,
        nom="Biais très faible (-0.2)"
    ),
    "BIAIS_FAIBLE": PerceptronEvitementObstacles(
        w_biais=-0.5,
        w_capteur=-0.5,
        nom="Biais faible (-0.5)"
    ),
    "BIAIS_NORMAL": PerceptronEvitementObstacles(
        w_biais=-1.0,
        w_capteur=-0.5,
        nom="Biais normal (-1.0)"
    ),
    "BIAIS_FORT": PerceptronEvitementObstacles(
        w_biais=-1.5,
        w_capteur=-0.5,
        nom="Biais fort (-1.5)"
    ),
    "BIAIS_TRÈS_FORT": PerceptronEvitementObstacles(
        w_biais=-2.0,
        w_capteur=-0.5,
        nom="Biais très fort (-2.0)"
    ),
    "RÉACTIF": PerceptronEvitementObstacles(
        w_biais=-1.0,
        w_capteur=-1.0,
        nom="Très réactif (capteur fort)"
    ),
    "LENT": PerceptronEvitementObstacles(
        w_biais=-0.8,
        w_capteur=-0.2,
        nom="Réaction lente (capteur faible)"
    )
}

# 🎯 CHOIX DE LA STRATÉGIE À TESTER (change la clé)
# Options: "BIAIS_TRÈS_FAIBLE", "BIAIS_FAIBLE", "BIAIS_NORMAL", "BIAIS_FORT", "BIAIS_TRÈS_FORT", "RÉACTIF", "LENT"
STRATEGIE_A_TESTER = "BIAIS_NORMAL"


# ============================================================================
# NORMALISATION CAPTEURS
# ============================================================================

def normaliser_capteur(valeur_raw, valeur_min=0, valeur_max=5000):
    """Normalise une valeur capteur en [0, 1]"""
    normalized = (valeur_raw - valeur_min) / (valeur_max - valeur_min)
    return max(0.0, min(1.0, normalized))


def normaliser_capteurs_thymio(capteurs):
    """
    Normalise les 5 capteurs du Thymio
    Utilise: [gauche (0), centre (2), droit (4)]
    Pour l'ÉVITEMENT: on ignore le centre, on utilise gauche et droit
    """
    x_gauche = normaliser_capteur(capteurs[0])
    x_droit = normaliser_capteur(capteurs[4])
    return x_gauche, x_droit


# ============================================================================
# VARIABLES GLOBALES ET CALLBACKS
# ============================================================================

done = False
iteration = 0
temps_debut = time.time()
strategie = STRATEGIES[STRATEGIE_A_TESTER]


def on_comm_error(error):
    """Gestion erreur communication"""
    print(f"❌ Erreur communication: {str(error)}")
    sys.exit(1)


# ============================================================================
# MAIN
# ============================================================================

# Affichage initial
print("TP2 - ÉVITEMENT D'OBSTACLES")
print(f"Stratégie: {strategie.nom}")
print(f"w_biais={strategie.w_biais:.2f}, w_capteur={strategie.w_capteur:.2f}")
print("Contrôles: Bouton FORWARD = Arrêter\n")

try:
    print("Connexion...")
    
    thymio_serial_ports = ThymioSerialPort.get_ports()
    if len(thymio_serial_ports) == 0:
        print("Aucun Thymio trouvé!")
        sys.exit(1)
    
    serial_port = thymio_serial_ports[0].device
    
    th = Thymio(
        use_tcp=False,
        serial_port=serial_port,
        refreshing_coverage={"prox.horizontal", "button.forward"}
    )
    th.on_comm_error = on_comm_error
    th.connect()
    
    node_id = th.first_node()
    if node_id is None:
        print("Impossible de trouver le noeud Thymio!")
        sys.exit(1)
    
    print("Démarrage...\n")
    
    # Boucle principale
    while not done:
        node = th[node_id]
        
        # BOUTONS DE CONTRÔLE
        if node['button.forward']:
            print("Arrêt")
            done = True
            node['motor.left.target'] = 0
            node['motor.right.target'] = 0
            break
        
        # LECTURE CAPTEURS
        try:
            capteurs = node['prox.horizontal']
            x_gauche, x_droit = normaliser_capteurs_thymio(capteurs)
        except:
            time.sleep(0.05)
            continue
        
        # INFÉRENCE
        (y_left, y_right), (z_left, z_right) = strategie.inference(x_gauche, x_droit)
        
        # VITESSE
        MAX_SPEED = 350
        v_left = int(y_left * MAX_SPEED)
        v_right = int(y_right * MAX_SPEED)
        
        # MOTEURS
        node['motor.left.target'] = v_left
        node['motor.right.target'] = v_right
        
        time.sleep(0.05)
    
    print("Session terminée")
    th.close()

except KeyboardInterrupt:
    print("\n\nArret manuel (Ctrl+C)")
    try:
        th.close()
    except:
        pass
    sys.exit(0)

except Exception as e:
    print(f"\nErreur: {e}")
    import traceback
    traceback.print_exc()
    try:
        th.close()
    except:
        pass
    sys.exit(1)
