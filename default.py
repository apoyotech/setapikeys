# -*- coding: utf-8 -*-
import xbmcaddon
import xbmcgui

# ====== TUS CLAVES (hardcoded) ======
OMDB_KEY     = "introducir tu api key"
MDBLIST_KEY  = "introducir tu api key"
SUBDL_KEY    = "introducir tu api key"
RPDB_KEY     = "introducir tu api key"
# ====================================

# Mapa de add-ons y posibles IDs de ajuste a probar
TARGETS = {
    # TMDb Helper → MDBlist
    "plugin.video.themoviedb.helper": {
        "MDBlist": {
            "value": MDBLIST_KEY,
            "ids": ["mdblist_apikey"]
        }
    },

    # Seren → OMDb
    "plugin.video.seren": {
        "OMDb": {
            "value": OMDB_KEY,
            "ids": ["omdb.apikey"]
        }
    },

    # Umbrella → MDBList 
    "plugin.video.umbrella": {
        "MDBList": {
            "value": MDBLIST_KEY,
            "ids": ["mdblist.api"]
        }
    },

    # a4kSubtitles → SubDL 
    "service.subtitles.a4ksubtitles": {
        "SubDL": {
            "value": SUBDL_KEY,
            "ids": ["subdl.apikey"]
        }
    },

    # POV → Rating Poster Database
    "plugin.video.pov": {
        "Rating Poster Database": {
            "value": RPDB_KEY,
            "ids": ["rpdb_api_key"]
        }
    }, 

}

def set_first_valid(addon_id, setting_ids, value):
    """
    Intenta escribir 'value' en el primer 'setting_id' que funcione.
    Devuelve (ok, setting_id_usado) .
    """
    try:
        ad = xbmcaddon.Addon(addon_id)
    except Exception:
        return False, "No instalado"

    for sid in setting_ids:
        try:
            ad.setSettingString(sid, value)
            if ad.getSettingString(sid) == value:
                return True, sid
        except Exception:
            # Continuar probando el siguiente ID candidato
            pass
    return False, "ID no encontrado"

def run():
    lines = []
    for addon_id, providers in TARGETS.items():
        for provider_name, cfg in providers.items():
            ok, used = set_first_valid(addon_id, cfg["ids"], cfg["value"])
            if ok:
                lines.append(f"✓ {addon_id} → {provider_name}: guardado en '{used}'")
            else:
                tried = ", ".join(cfg["ids"])
                lines.append(f"✗ {addon_id} → {provider_name}: no se encontró un ID válido (probados: {tried})")
    xbmcgui.Dialog().textviewer("setapikeys", "\n".join(lines))

if __name__ == "__main__":
    run()
