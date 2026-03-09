# Perceptron simple

def fonct_somme(x1, x2, w0, w1, w2):
    """Somme pondérée: x = w0 + w1*x1 + w2*x2"""
    return w0 + w1*x1 + w2*x2

def fonct_activation(x):
    """Fonction échelon: 1 si x >= 0, sinon 0"""
    return 1 if x >= 0 else 0

# Toutes les combinaisons d'entrées
entrees = [(0,0), (0,1), (1,0), (1,1)]

# Poids: (biais, w1, w2)
poids = {
    "AND": (-1.5, 1, 1),
    "OR":  (-0.5, 1, 1),
}

# Test AND et OR
for nom, (w0, w1, w2) in poids.items():
    print(f"\n{nom}:")
    for x1, x2 in entrees:
        x = fonct_somme(x1, x2, w0, w1, w2)
        y = fonct_activation(x)
        print(f"  {x1}, {x2} -> {y}")

# XOR = AND(OR, NAND) - nécessite 2 couches
print("\nXOR:")
for x1, x2 in entrees:
    y_or   = fonct_activation(fonct_somme(x1, x2, -0.5, 1, 1))    # OR
    y_nand = fonct_activation(fonct_somme(x1, x2, 1.5, -1, -1))   # NAND
    y_xor  = fonct_activation(fonct_somme(y_or, y_nand, -1.5, 1, 1))  # AND
    print(f"  {x1}, {x2} -> {y_xor}")
