from typing import Tuple
from vect_hunt.engine.core.math.numeric import Numeric

ColorRGB = Tuple[int, int, int]
ColorRGBA = Tuple[int, int, int, int]


class RenderOps:
    """
    Utilitaires liés au rendu.
    """

    @staticmethod
    def _clamp_channel(value: float) -> int:
        """
        Contraint une valeur de canal couleur entre 0 et 255.

        Parameters
        ----------
        value : float
            Valeur du canal couleur.

        Returns
        -------
        int
            Valeur contrainte entre 0 et 255.
        """
        return int(Numeric.clamp(round(value), 0, 255))

    @staticmethod
    def hex_to_rgb(hex_color: str) -> ColorRGB:
        """
        Convertit une couleur hexadecimale en tuple RGB.

        Parameters
        ----------
        hex_color : str
            Couleur au format "RRGGBB" ou "#RRGGBB".

        Returns
        -------
        tuple[int, int, int]
            Valeurs rouge, verte et bleue comprises entre 0 et 255.
        """
        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6:
            raise ValueError("La couleur hex doit être au format RRGGBB")

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)

    @staticmethod
    def rgb_to_hex(color: ColorRGB) -> str:
        """
        Convertit un tuple RGB en couleur hexadecimale.

        Parameters
        ----------
        color : tuple[int, int, int]
            Couleur au format RGB (0..255).

        Returns
        -------
        str
            Couleur au format "#RRGGBB".
        """
        r, g, b = color
        return f"#{r:02X}{g:02X}{b:02X}"

    @staticmethod
    def hex_to_rgba(hex_color: str) -> ColorRGBA:
        """
        Convertit une couleur hexadecimale en tuple RGBA.

        Parameters
        ----------
        hex_color : str
            Couleur hexadecimale.

        Returns
        -------
        tuple[int, int, int, int]
            Valeurs RGBA (0..255).
        """
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 6:
            r, g, b = RenderOps.hex_to_rgb(hex_color)
            return (r, g, b, 255)

        if len(hex_color) == 8:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            a = int(hex_color[6:8], 16)
            return (r, g, b, a)
        raise ValueError("La couleur hex doit être au format RRGGBB ou RRGGBBAA")

    @staticmethod
    def rgba_to_hex(color: ColorRGBA) -> str:
        """
        Convertit un tuple RGBA en couleur hexadecimale.

        Parameters
        ----------
        color : tuple[int, int, int, int]
            Couleur au format RGBA (0..255).

        Returns
        -------
        str
            Couleur au format "#RRGGBBAA".
        """
        r, g, b, a = color
        return f"#{r:02X}{g:02X}{b:02X}{a:02X}"

    @staticmethod
    def lerp_color(color_a: ColorRGB, color_b: ColorRGB, t: float) -> ColorRGB:
        """
        Interpole lineairement deux couleurs RGB.

        Parameters
        ----------
        color_a : tuple[int, int, int]
            Couleur de depart.
        color_b : tuple[int, int, int]
            Couleur d'arrivee.
        t : float
            Facteur d'interpolation (0..1).

        Returns
        -------
        tuple[int, int, int]
            Couleur interpolee.
        """
        r = round(Numeric.lerp(color_a[0], color_b[0], t))
        g = round(Numeric.lerp(color_a[1], color_b[1], t))
        b = round(Numeric.lerp(color_a[2], color_b[2], t))

        return (r, g, b)

    # TODO : Enum pour les modes
    @staticmethod
    def blend_colors(
        color_a: ColorRGB,
        color_b: ColorRGB,
        mode: str = "alpha",
        amount: float = 0.5,
    ) -> ColorRGB:
        """
        Melange deux couleurs selon un mode.

        Mode "alpha" sert a un melange lineaire classique, avec amount entre 0 et 1.
        Mode "add" additionne les canaux RGB.
        Mode "multiply" multiplie les canaux RGB.
        Mode "screen" applique un melange en écran.

        Parameters
        ----------
        color_a : tuple[int, int, int]
            Couleur de base.
        color_b : tuple[int, int, int]
            Couleur a melanger.
        mode : str
            Mode de melange (alpha, add, multiply, screen).
        amount : float
            Intensite pour le mode alpha.

        Returns
        -------
        tuple[int, int, int]
            Couleur melangée.
        """
        if mode == "alpha":
            return RenderOps.lerp_color(color_a, color_b, amount)
        if mode == "add":
            return (
                RenderOps._clamp_channel(color_a[0] + color_b[0]),
                RenderOps._clamp_channel(color_a[1] + color_b[1]),
                RenderOps._clamp_channel(color_a[2] + color_b[2]),
            )
        if mode == "multiply":
            return (
                RenderOps._clamp_channel(color_a[0] * color_b[0] / 255.0),
                RenderOps._clamp_channel(color_a[1] * color_b[1] / 255.0),
                RenderOps._clamp_channel(color_a[2] * color_b[2] / 255.0),
            )
        if mode == "screen":
            return (
                RenderOps._clamp_channel(
                    255 - (255 - color_a[0]) * (255 - color_b[0]) / 255.0
                ),
                RenderOps._clamp_channel(
                    255 - (255 - color_a[1]) * (255 - color_b[1]) / 255.0
                ),
                RenderOps._clamp_channel(
                    255 - (255 - color_a[2]) * (255 - color_b[2]) / 255.0
                ),
            )
        raise ValueError("Mode de melange non supporte")

    @staticmethod
    def adjust_brightness(color: ColorRGB, factor: float) -> ColorRGB:
        """
        Ajuste la luminosite d'une couleur.
        factor > 1 eclaircit, factor < 1 assombrit.

        Parameters
        ----------
        color : tuple[int, int, int]
            Couleur de base.
        factor : float
            Facteur de luminosite.

        Returns
        -------
        tuple[int, int, int]
            Couleur ajustee.
        """
        return (
            RenderOps._clamp_channel(color[0] * factor),
            RenderOps._clamp_channel(color[1] * factor),
            RenderOps._clamp_channel(color[2] * factor),
        )

    @staticmethod
    def adjust_contrast(color: ColorRGB, factor: float) -> ColorRGB:
        """
        Ajuste le contraste d'une couleur.
        factor > 1 renforce le contraste, < 1 l'adoucit.

        Parameters
        ----------
        color : tuple[int, int, int]
            Couleur de base.
        factor : float
            Facteur de contraste.

        Returns
        -------
        tuple[int, int, int]
            Couleur ajustee.
        """
        r = RenderOps._clamp_channel((color[0] - 128) * factor + 128)
        g = RenderOps._clamp_channel((color[1] - 128) * factor + 128)
        b = RenderOps._clamp_channel((color[2] - 128) * factor + 128)

        return (r, g, b)

    @staticmethod
    def tint(color: ColorRGB, tint_color: ColorRGB, amount: float) -> ColorRGB:
        """
        Applique une teinte a une couleur.

        Parameters
        ----------
        color : tuple[int, int, int]
            Couleur de base.
        tint_color : tuple[int, int, int]
            Couleur de teinte.
        amount : float
            Intensite de teinte (0..1).

        Returns
        -------
        tuple[int, int, int]
            Couleur teintee.
        """
        return RenderOps.lerp_color(color, tint_color, amount)

    @staticmethod
    def with_alpha(color: ColorRGB | ColorRGBA, alpha: int) -> ColorRGBA:
        """
        Fixe l'alpha d'une couleur.
        Permet d'imposer une transparence sans changer le RGB.

        Parameters
        ----------
        color : tuple[int, int, int] | tuple[int, int, int, int]
            Couleur de base.
        alpha : int
            Valeur alpha (0..255).

        Returns
        -------
        tuple[int, int, int, int]
            Couleur avec alpha force.
        """
        if len(color) == 4:
            return (color[0], color[1], color[2], alpha)
        return (color[0], color[1], color[2], alpha)
