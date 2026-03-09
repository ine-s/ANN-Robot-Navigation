# Implémentation d'un perceptron simple

def fonct_somme(x1, x2, w0, w1, w2):
    """
    Fonction de somme pondérée
    x = w0 + w1*x1 + w2*x2
    w0 = biais
    """
    x = w0 + w1 * x1 + w2 * x2
    return x


def fonct_activation(x):
    """
    Fonction d'activation échelon
    Retourne 1 si x >= 0, sinon 0
    """
    if x >= 0:
        y = 1
    else:
        y = 0
    return y


def perceptron(x1, x2, w0, w1, w2):
    """
    Combine somme pondérée et activation
    """
    x = fonct_somme(x1, x2, w0, w1, w2)
    y = fonct_activation(x)
    return y


# Table de vérité - toutes les combinaisons possibles
combinaisons = [
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1)
]

# Poids pour chaque opérateur logique
# Format: (w0, w1, w2) où w0 = biais
poids_AND = (-1.5, 1, 1)   # AND: seuil à 1.5, les deux entrées doivent être 1
poids_OR = (-0.5, 1, 1)    # OR: seuil à 0.5, une seule entrée suffit
poids_XOR = (0.5, 1, -1)   # XOR: impossible avec un perceptron simple

operateurs = {
    "AND": poids_AND,
    "OR": poids_OR,
    "XOR": poids_XOR,
}

# Test de la table de vérité pour chaque opérateur
print("=" * 50)
print("TEST DES OPÉRATEURS LOGIQUES AVEC PERCEPTRON")
print("=" * 50)

for nom_op, (w0, w1, w2) in operateurs.items():
    print(f"\n--- Opérateur {nom_op} ---")
    print(f"Poids: w0={w0}, w1={w1}, w2={w2}")
    print(f"{'x1':<5} {'x2':<5} {'Sortie y':<10}")
    print("-" * 20)
    
    for x1, x2 in combinaisons:
        y = perceptron(x1, x2, w0, w1, w2)
        print(f"{x1:<5} {x2:<5} {y:<10}")

print("\n--- Table de vérité attendue ---")
print("x1 | x2 | AND | OR  | XOR")
print(" 0 |  0 |  0 |  0  |  0")
print(" 0 |  1 |  0 |  1  |  1")
print(" 1 |  0 |  0 |  1  |  1")
print(" 1 |  1 |  1 |  1  |  0")
print("\n=> XOR est impossible avec un perceptron simple (non linéairement séparable)")



