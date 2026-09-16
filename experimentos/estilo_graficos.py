"""Estilo visual comun para todas las figuras del Anexo — consistencia y legibilidad."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AZUL = "#2b6cb0"
ROJO = "#c0392b"
VERDE = "#2f855a"
GRIS = "#718096"
NARANJA = "#dd6b20"
MORADO = "#6b46c1"

def aplicar_estilo():
    plt.rcParams.update({
        "font.size": 12,
        "font.family": "DejaVu Sans",
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "axes.labelsize": 12.5,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "legend.fontsize": 11,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#333333",
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })
