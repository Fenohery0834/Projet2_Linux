"""
configuration.py -- Constantes globales et theme visuel de Check_file.
"""

APP_NAME    = "Check_file"
APP_VERSION = "2.0"

DEFAULT_DIRECTORY = "/etc"

# Historique max conserve en memoire pour le mot-cle
KEYWORD_HISTORY_MAX = 20

EXTENSIONS = [
    "Tous les fichiers",
    ".conf", ".txt", ".log", ".sh", ".py",
    ".json", ".yaml", ".yml", ".xml", ".cfg", ".ini", ".env",
]

# Theme
THEME = {
    "bg":           "#2b2b2b",
    "bg2":          "#333333",
    "bg3":          "#3c3c3c",
    "border":       "#555555",

    "text":         "#e2e8f0",
    "text2":        "#aaaaaa",
    "text3":        "#777777",

    "accent":       "#aaaaaa",

    "entry_bg":     "#ffffff",
    "entry_fg":     "#000000",
    "select_bg":    "#888888",

    "result_file":  "#cccccc",
    "result_match": "#e2e8f0",
    "result_ctx":   "#aaaaaa",
    "result_meta":  "#777777",
    "result_err":   "#ff6666",

    "btn_bg":       "#444444",
    "btn_fg":       "#e2e8f0",
    "btn_search_bg":"#555555",
    "btn_search_fg":"#ffffff",
    "btn_stop_bg":  "#3a3a3a",
    "btn_stop_fg":  "#ff9999",
    "btn_export_bg":"#3a3a3a",
    "btn_export_fg":"#aaddaa",
    "btn_clear_bg": "#3a3a3a",
    "btn_clear_fg": "#ffcc88",

    "success":      "#aaddaa",
    "danger":       "#ff6666",
    "warning":      "#ffcc88",
}

