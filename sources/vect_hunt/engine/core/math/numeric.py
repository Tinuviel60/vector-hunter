import math
import random


def hex_to_rgb(hex_color):
    """
    Convertit une couleur hexadécimale en tuple RGB.

    Parameters
    ----------
    hex_color : str
        Couleur au format "RRGGBB" ou "#RRGGBB".

    Returns
    -------
    tuple[int, int, int]
        Valeurs rouge, verte et bleue comprises entre 0 et 255.

    Raises
    ------
    ValueError
        Si la chaîne fournie n'est pas au format hexadécimal valide.
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError("La couleur hex doit être au format RRGGBB")

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)


def clamp(value, min_value, max_value):
    """
    Contraint une valeur dans un intervalle fermé [min_value, max_value].

    Parameters
    ----------
    value : float
        Valeur à contraindre.
    min_value : float
        Borne inférieure.
    max_value : float
        Borne supérieure.

    Returns
    -------
    float
        Valeur contrainte dans l'intervalle.
    """
    return max(min_value, min(value, max_value))


def normalize(value: float, min_val: float, max_val: float, cap: bool = True) -> float:
    """
    Normalise une valeur entre 0 et 1 selon un minimum et un maximum donnés.

    Parameters
    ----------
    value : float
        La valeur à normaliser.
    min_val : float
        La valeur correspondant à 0 après normalisation.
    max_val : float
        La valeur correspondant à 1 après normalisation.
    cap : bool
        Si True, limite la valeur normalisée entre 0 et 1.
        Sinon, elle peut dépasser.
        Par défaut, True.

    Returns
    -------
    float
        La valeur normalisée entre 0 et 1 (ou au-delà si pas de cap).
    """
    norm = (value - min_val) / (max_val - min_val) if max_val != min_val else 0.0
    if cap:
        norm = max(0.0, min(1.0, norm))
    return norm


def normalize_ratio(val1: float, val2: float) -> float:
    """
    Calcule le ratio normalisé de deux valeurs, c'est-à-dire la proportion d'une valeur
    par rapport au total.

    Parameters
    ----------
    val1 : float
        Première valeur.
    val2 : float
        Deuxième valeur.

    Returns
    -------
    float
        Ratio de val1 sur (val1 + val2), compris entre 0 et 1.
        Retourne 0.5 si les deux valeurs sont nulles.
    """
    total = val1 + val2
    if total == 0:
        ratio = 0.5  # valeur neutre si aucune donnée
    else:
        ratio = val1 / total

    return ratio


def normalize_log(
    value: float, min_val: float, max_val: float, cap: bool = True
) -> float:
    """
    Normalise une valeur selon un minimum et un maximum donnés
    sur une échelle logarithmique.

    Cette méthode accentue les écarts faibles et réduit l'effet
    des grandes valeurs.

    Parameters
    ----------
    value : float
        Valeur à normaliser.
    min_val : float
        Valeur correspondant à 0 après normalisation.
    max_val : float
        Valeur correspondant à 1 après normalisation.
    cap : bool
        Si True, limite le résultat entre 0 et 1.
        Par défaut, True.

    Returns
    -------
    float
        Valeur normalisée logarithmiquement entre 0 et 1.
    """
    # Ajuste pour éviter log(0)
    adj_value = max(value - min_val, 0.0)
    adj_max = max(max_val - min_val, 1e-6)  # éviter division par zéro
    norm = math.log1p(adj_value) / math.log1p(adj_max)  # log(1 + x)
    if cap:
        norm = max(0.0, min(1.0, norm))
    return norm


def normalize_ratio_log(val1: float, val2: float) -> float:
    """
    Calcule un ratio normalisé sur deux valeurs avec transformation logarithmique.

    Cette méthode met plus en valeur les petites différences
    et réduit l'effet des grandes valeurs.

    Le ratio est compris entre 0 et 1.

    Parameters
    ----------
    val1 : float
        Première valeur.
    val2 : float
        Deuxième valeur.

    Returns
    -------
    float
        Ratio normalisé log-transformé, entre 0 et 1.
        Retourne 0.5 si les deux valeurs sont nulles.
    """
    # On ajoute 1 pour éviter log(0)
    log1 = math.log(1 + val1)
    log2 = math.log(1 + val2)

    # Ratio log normalisé
    if log1 + log2 == 0:
        return 0.5  # valeur neutre si les deux sont nuls
    return log1 / (log1 + log2)


def exponential_scale(value: float, threshold: float = 1.0, rate: float = 1.5) -> float:
    """
    Calcule un facteur d'échelle avec croissance exponentielle continue.

    La fonction est lisse, continue et croît exponentiellement au-delà du seuil.
    - value < threshold : facteur = 0
    - value = threshold : facteur = 0
    - value > threshold : croissance exponentielle

    Utilisation neutre : stress, bonus, coût énergétique, gain d'expérience, etc.

    Parameters
    ----------
    value : float
        Valeur à transformer (densité, niveau, température, etc.).
    threshold : float
        Seuil à partir duquel l'effet exponentiel commence.
        Par défaut 1.0.
    rate : float
        Taux de croissance exponentielle (plus élevé = croissance plus rapide).
        Par défaut 1.5.

    Returns
    -------
    float
        Facteur d'échelle entre 0 et l'infini.
    """
    if value <= threshold:
        return 0.0

    # Croissance exponentielle: e^(rate * delta) - 1
    delta = value - threshold
    return math.exp(rate * delta) - 1.0


def gaussian_between(low: float, high: float, rng=None) -> float:
    """
    Tire une valeur selon une gaussienne centrée sur la moyenne
    de low et high, avec écart-type = (high - low)/4 pour rester
    majoritairement entre low et high.

    Parameters
    ----------
    low : float
        Borne inférieure.
    high : float
        Borne supérieure.
    rng : random.Random, optional
        Générateur aléatoire à utiliser.
        Si None, un nouveau générateur est créé.
        Par défaut, None.

    Returns
    -------
    float
        Valeur tirée selon la gaussienne, contrainte entre low et high.
    """

    if rng is None:
        rng = random.Random()

    mean = (low + high) / 2
    std = (high - low) / 4
    value = rng.gauss(mean, std)
    # Clamp pour rester entre low et high
    return max(low, min(high, value))
