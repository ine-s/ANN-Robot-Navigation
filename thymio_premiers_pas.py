
from thymiodirect import Thymio
from thymiodirect.thymio_serial_ports import ThymioSerialPort
import sys
import os
import time

# === Fonctions du perceptron ===
def fonct_somme(x1, x2, w0, w1, w2):
    """Somme pondérée: s = w0 + w1*x1 + w2*x2"""
    s = w0 + w1 * x1 + w2 * x2
    return s

def fonct_activation(s):
    """Fonction échelon: 1 si s >= 0, sinon 0"""
    if s >= 0:
        y = 1
    else:
        y = 0
    return y

def perceptron(x1, x2, w0, w1, w2):
    """Perceptron complet"""
    s = fonct_somme(x1, x2, w0, w1, w2)
    y = fonct_activation(s)
    return y

# Poids pour AND
W0_AND = -1.5
W1_AND = 1
W2_AND = 1

# Seuils de détection
SEUIL_PROXIMITE = 1000
SEUIL_SOL = 500

def capteur_vers_binaire(valeur, seuil):
    """Convertit une valeur de capteur en 0 ou 1"""
    return 1 if valeur > seuil else 0

def set_leds(th, id, R, G, B):
    src = """
        dc end_toc                  ; total size of event handler table
        dc _ev.init, init           ; id and address of init event
    end_toc:

    init:                           ; code executed on init event
        push.s 0                    ; initialize counter
        store counter
        push.s """
    src2="""
        store _userdata
        push.s _userdata
        push.s """
    src3="""
        store _userdata+1
        push.s _userdata+1
        push.s """
    src4="""
        store _userdata+2
        push.s _userdata+2
        callnat _nf."""
    src5="""
        stop                        ; stop program

    counter:
        equ _userdata+3
    """
    th.run_asm(id, src+str(B)+src2+str(G)+src3+str(R)+src4+'leds.top'+src5)

def on_comm_error(error):
    # loss of connection: display error and exit
    print(error)
    os._exit(1) # forced exit despite coroutines

# Choisir le comportement: 'A' ou 'B'
COMPORTEMENT = 'A'

## Thymio callback
def obs(node_id):
        global done
        if not(done):
            
            if COMPORTEMENT == 'A':
                # Comportement A: avancer si les 2 capteurs ARRIÈRE détectent un obstacle (AND)
                # Capteurs arrière: prox.horizontal[5] et prox.horizontal[6]
                capt_gauche = th[node_id]["prox.horizontal"][5]
                capt_droit = th[node_id]["prox.horizontal"][6]
                x1 = capteur_vers_binaire(capt_gauche, SEUIL_PROXIMITE)
                x2 = capteur_vers_binaire(capt_droit, SEUIL_PROXIMITE)
            else:
                # Comportement B: avancer si les 2 capteurs AU SOL détectent une surface (AND)
                capt_gauche = th[node_id]["prox.ground.delta"][0]
                capt_droit = th[node_id]["prox.ground.delta"][1]
                x1 = capteur_vers_binaire(capt_gauche, SEUIL_SOL)
                x2 = capteur_vers_binaire(capt_droit, SEUIL_SOL)
            
            # Perceptron AND
            y = perceptron(x1, x2, W0_AND, W1_AND, W2_AND)
            
            # Debug: afficher les valeurs
            print(f"Capteurs: G={capt_gauche}, D={capt_droit} | x1={x1}, x2={x2} | y={y}")
            
            if y == 1:
                # Avancer
                th[node_id]["motor.left.target"] = 100
                th[node_id]["motor.right.target"] = 100
                # set_leds(th, id, 0, 255, 0)  # LED verte - désactivé pour test
            else:
                # Arrêter
                th[node_id]["motor.left.target"] = 0
                th[node_id]["motor.right.target"] = 0
                # set_leds(th, id, 255, 0, 0)  # LED rouge - désactivé pour test
            
            if th[node_id]["button.center"]:
                print("button.center pressed")
                #Arret du robot
                th[node_id]["motor.left.target"] = 0
                th[node_id]["motor.right.target"] = 0
                set_leds(th, id, 0, 0, 0)
                done = True

#################
## Code principal
#################
## Recherche du port
thymio_serial_ports = ThymioSerialPort.get_ports()
if len(thymio_serial_ports) > 0:
    serial_port = thymio_serial_ports[0].device
    print("Thymio serial ports:")
    for thymio_serial_port in thymio_serial_ports:
        print(" ", thymio_serial_port, thymio_serial_port.device)
try:
    th = Thymio(use_tcp=False,
                    serial_port=serial_port,
                    refreshing_coverage={"prox.horizontal", "prox.ground.delta", "button.center"},
                   )
        # constructor options: on_connect, on_disconnect, on_comm_error,
        # refreshing_rate, refreshing_coverage, discover_rate, loop
except Exception as error:
    print(error)
    exit(1)


th.on_comm_error = on_comm_error
th.connect()
id = th.first_node()
done = False

set_leds(th, id, 0, 0, 255)
th.set_variable_observer(id, obs)
print("Thymio executing code")

while not done:
    time.sleep(0.1)        #Sampling routine
print("Thymio disconnecting")
th.disconnect()
