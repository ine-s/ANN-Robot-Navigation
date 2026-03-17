from thymiodirect import Thymio
from thymiodirect.thymio_serial_ports import ThymioSerialPort
import sys
import os
import time

# === Perceptron Analogique ===
# la sortie est proportionnelle à l'entrée , pas d'échelon

# --- Perceptron à 1 entrée (Fig. 2) ---
def perceptron_1_entree(x1, w1):
    """
    y = w1 * x1
    Sortie proportionnelle à l'entrée
    """
    y = w1 * x1
    return y

# --- Perceptron à 2 entrées (Fig. 3) ---
def perceptron_2_entrees(x1, x2, w1, w2):
    """
    y = w1 * x1 + w2 * x2
    Le capteur avec le poids plus fort a plus d'influence
    """
    y = w1 * x1 + w2 * x2
    return y

# === Configuration ===
# Choisir le mode: '1_ENTREE' ou '2_ENTREES'
MODE = '1_ENTREE'

# Poids pour perceptron 1 entrée
W1_SIMPLE = -0.1  # Négatif pour reculer quand obstacle détecté

# Poids pour perceptron 2 entrées (capteur gauche et droit)
W1_GAUCHE = -0.15  # Poids plus fort = plus d'influence
W2_DROIT = -0.05   # Poids plus faible

# Vitesse max de recul
VITESSE_MAX = 300

def limiter_vitesse(v):
    """Limite la vitesse entre -VITESSE_MAX et VITESSE_MAX"""
    if v > VITESSE_MAX:
        return VITESSE_MAX
    elif v < -VITESSE_MAX:
        return -VITESSE_MAX
    return int(v)

def on_comm_error(error):
    print(error)
    os._exit(1)

## Thymio callback
def obs(node_id):
    global done
    if not(done):
        
        if MODE == '1_ENTREE':
            # Perceptron à 1 entrée: capteur avant central (indice 2)
            x1 = th[node_id]["prox.horizontal"][2]
            
            # Calcul perceptron analogique
            y = perceptron_1_entree(x1, W1_SIMPLE)
            vitesse = limiter_vitesse(y)
            
            # Appliquer aux moteurs (même vitesse gauche/droite = recul droit)
            th[node_id]["motor.left.target"] = vitesse
            th[node_id]["motor.right.target"] = vitesse
            
            print(f"C={x1} | y={y:.1f} | v={vitesse}")
            
        else:
            # Perceptron à 2 entrées: capteurs avant gauche et droit
            x1 = th[node_id]["prox.horizontal"][0]  # Capteur gauche
            x2 = th[node_id]["prox.horizontal"][4]  # Capteur droit
            
            # Calcul perceptron analogique
            y = perceptron_2_entrees(x1, x2, W1_GAUCHE, W2_DROIT)
            vitesse = limiter_vitesse(y)
            
            # Appliquer aux moteurs
            th[node_id]["motor.left.target"] = vitesse
            th[node_id]["motor.right.target"] = vitesse
            
            print(f"G={x1} D={x2} | y={y:.1f} | v={vitesse}")
        
        if th[node_id]["button.center"]:
            print("button.center pressed")
            th[node_id]["motor.left.target"] = 0
            th[node_id]["motor.right.target"] = 0
            done = True

#################
## Code principal
#################
thymio_serial_ports = ThymioSerialPort.get_ports()
if len(thymio_serial_ports) > 0:
    serial_port = thymio_serial_ports[0].device
try:
    th = Thymio(use_tcp=False,
                serial_port=serial_port,
                refreshing_coverage={"prox.horizontal", "button.center"},
               )
except Exception as error:
    print(error)
    exit(1)

th.on_comm_error = on_comm_error
th.connect()
id = th.first_node()
done = False

print(f"\nPerceptron analogique - Mode: {MODE}")
if MODE == '1_ENTREE':
    print(f"w1 = {W1_SIMPLE}")
else:
    print(f"w1 (gauche) = {W1_GAUCHE} | w2 (droit) = {W2_DROIT}")
print("Appuyer sur le bouton central pour arrêter\n")

th.set_variable_observer(id, obs)

while not done:
    time.sleep(0.1)
print("Thymio disconnecting")
th.disconnect()
