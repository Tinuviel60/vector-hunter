import math
import random
from typing import Optional


class Numeric:
    """
    Utilitaires numériques.

    Cette classe expose des fonctions simples et centrales
    pour les opérations mathématiques récurrentes.
    """

    @staticmethod
    def clamp(value: float, min_value: float, max_value: float) -> float:
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

    @staticmethod
    def lerp(a: float, b: float, t: float) -> float:
        """
        Interpolation lineaire entre a et b selon t.

        Parameters
        ----------
        a : float
            Valeur de depart.
        b : float
            Valeur d'arrivee.
        t : float
            Facteur d'interpolation.

        Returns
        -------
        float
            Valeur interpolee.
        """
        return a + (b - a) * t

    @staticmethod
    def inverse_lerp(a: float, b: float, value: float) -> float:
        """
        Calcule le facteur t d'une interpolation inverse.

        Parameters
        ----------
        a : float
            Borne basse.
        b : float
            Borne haute.
        value : float
            Valeur a normaliser.

        Returns
        -------
        float
            Facteur d'interpolation.
        """
        if a == b:
            return 0.0
        return (value - a) / (b - a)

    @staticmethod
    def remap(
        value: float, in_min: float, in_max: float, out_min: float, out_max: float
    ) -> float:
        """
        Convertit une valeur d'un intervalle a un autre.

        Parameters
        ----------
        value : float
            Valeur a convertir.
        in_min : float
            Borne basse d'entree.
        in_max : float
            Borne haute d'entree.
        out_min : float
            Borne basse de sortie.
        out_max : float
            Borne haute de sortie.

        Returns
        -------
        float
            Valeur remappee.
        """
        t = Numeric.inverse_lerp(in_min, in_max, value)
        return Numeric.lerp(out_min, out_max, t)

    @staticmethod
    def saturate(value: float) -> float:
        """
        Clamp rapide dans [0..1] pour normaliser des valeurs (alpha, pourcentage).

        Parameters
        ----------
        value : float
            Valeur a contraindre.

        Returns
        -------
        float
            Valeur entre 0 et 1.
        """
        return Numeric.clamp(value, 0.0, 1.0)
    
    # TODO : Espilon par default global
    @staticmethod
    def is_close(a: float, b: float, eps: float = 1e-9) -> bool:
        """
        Compare deux flottants avec tolerance pour eviter les erreurs de precision.

        Parameters
        ----------
        a : float
            Premiere valeur.
        b : float
            Seconde valeur.
        eps : float
            Tolerance.

        Returns
        -------
        bool
            True si les valeurs sont proches.
        """
        return abs(a - b) <= eps

    # TODO : Espilon par default global
    @staticmethod
    def nearly_zero(value: float, eps: float = 1e-9) -> bool:
        """
        Test si une valeur est proche de zero.

        Parameters
        ----------
        value : float
            Valeur a tester.
        eps : float
            Tolerance.

        Returns
        -------
        bool
            True si la valeur est proche de zero.
        """
        return abs(value) <= eps

    @staticmethod
    def sign(value: float) -> int:
        """
        Retourne le signe d'une valeur.

        Parameters
        ----------
        value : float
            Valeur a evaluer.

        Returns
        -------
        int
            -1 si negatif, 1 si positif, 0 si nul.
        """
        if value > 0:
            return 1
        if value < 0:
            return -1
        return 0

    @staticmethod
    def treshold(edge: float, value: float) -> float:
        """
        Fonction de seuil binaire, qui retourne 0 ou 1 selon que la valeur
        depasse le seuil.

        Parameters
        ----------
        edge : float
            Seuil.
        value : float
            Valeur a tester.

        Returns
        -------
        float
            0.0 ou 1.0.
        """
        return 0.0 if value < edge else 1.0

    @staticmethod
    def smoothstep(edge0: float, edge1: float, value: float) -> float:
        """
        Produit une interpolation avec transition douce entre 0 et 1.

        Parameters
        ----------
        edge0 : float
            Borne basse.
        edge1 : float
            Borne haute.
        value : float
            Valeur a interpoler.

        Returns
        -------
        float
            Valeur lisse entre 0 et 1.
        """
        if edge0 == edge1:
            return 0.0
        t = Numeric.saturate((value - edge0) / (edge1 - edge0))
        return t * t * (3.0 - 2.0 * t)

    @staticmethod
    def wrap(value: float, min_value: float, max_value: float) -> float:
        """
        Reboucle une valeur dans un intervalle.

        Explication
        -----------
        Permet de boucler des angles ou positions cycliques.

        Parameters
        ----------
        value : float
            Valeur a boucler.
        min_value : float
            Borne basse.
        max_value : float
            Borne haute.

        Returns
        -------
        float
            Valeur dans [min_value, max_value).
        """
        span = max_value - min_value
        if span == 0:
            return min_value
        return ((value - min_value) % span) + min_value

    @staticmethod
    def oscilate(value: float, length: float) -> float:
        """
        Mouvement aller-retour entre 0 et length.

        Parameters
        ----------
        value : float
            Valeur d'entree.
        length : float
            Amplitude du pingpong.

        Returns
        -------
        float
            Valeur oscillee entre 0 et length.
        """
        if length <= 0:
            return 0.0
        cycle = value % (2.0 * length)
        if cycle < length:
            return cycle
        else:
            return 2.0 * length - cycle

    