# Implémentation d'un perceptron simple
import matplotlib.pyplot as plt

def fonct_somme(x1, x2, w0, w1, w2):
    x = w0 + w1 * x1 + w2 * x2
    return x

def fonct_activation(x):
    if x >= 0:
        y = 1
    else:
        y = 0
    return y

def perceptron(x1, x2, w0, w1, w2):
    #Combine somme pondérée et activation
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



# Création du graphique
fig, axes = plt.subplots(1, 3, figsize=(12, 4))

for idx, (nom_op, (w0, w1, w2)) in enumerate(operateurs.items()):
    ax = axes[idx]
    
    # Calculer les sorties pour chaque combinaison
    for x1, x2 in combinaisons:
        y = perceptron(x1, x2, w0, w1, w2)
        color = 'green' if y == 1 else 'red'
        marker = 'o' if y == 1 else 'x'
        ax.scatter(x1, x2, c=color, s=200, marker=marker, label=f'y={y}' if (x1, x2) == (0, 0) else "")
    
    # Tracer la frontière de décision: w0 + w1*x1 + w2*x2 = 0
    # => x2 = (-w0 - w1*x1) / w2
    if w2 != 0:
        x1_line = [-0.5, 1.5]
        x2_line = [(-w0 - w1*x) / w2 for x in x1_line]
        ax.plot(x1_line, x2_line, 'b--', linewidth=2, label='Frontière')
    
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.5, 1.5)
    ax.set_xlabel('x1')
    ax.set_ylabel('x2')
    ax.set_title(f'{nom_op}\nw0={w0}, w1={w1}, w2={w2}')
    ax.grid(True, alpha=0.3)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])

# Légende
fig.suptitle('Perceptron: Test des opérateurs logiques\n(vert/o = y=1, rouge/x = y=0, ligne = frontière de décision)', fontsize=10)
plt.tight_layout()
plt.savefig('perceptron_resultats.png', dpi=150)
plt.show()
print("\nGraphique sauvegardé: perceptron_resultats.png")



