# -*- coding: utf-8 -*-
import sys
import urllib.parse
import xbmc
import xbmcgui
import xbmcaddon

# ====== TUS CLAVES (puedes editarlas en este archivo por ahora) ======
OMDB_KEY     = "3b6c28ce"
MDBLIST_KEY  = "xma2hxonarl718z4w7adchsef"
SUBDL_KEY    = "lj9neeNGx37abT59gZYQaF_8iDSwNrT_"
RPDB_KEY     = "t0-free-rpdb"
# =====================================================================

ADDON_ID = "plugin.program.setapikeys"
ADDON = xbmcaddon.Addon(id=ADDON_ID)

# Mapa de destinos → (tipo, id, posibles claves)
# tipo "addon" = setSetting, tipo "skinstring" = Skin.SetString
TARGETS = {
    "seren":         ("addon",      "plugin.video.seren",              ["omdb.apikey"]),
    "tmdb.helper":   ("addon",      "plugin.video.themoviedb.helper",  ["mdblist_apikey", "mdblist.api", "mdblist_api_key"]),
    "umbrella":      ("addon",      "plugin.video.umbrella",           ["mdblist.api", "mdblist_key"]),
    "a4ksubtitles":  ("addon",      "service.subtitles.a4ksubtitles",  ["subdl.apikey"]),
    "pov":           ("addon",      "plugin.video.pov",                ["rpdb_api_key"]),
    "skin_fentastic":("skinstring", None,                               ["mdblist_api_key"]),
}

PROVIDER_TO_KEY = {
    "omdb":    OMDB_KEY,
    "mdblist": MDBLIST_KEY,
    "subdl":   SUBDL_KEY,
    "rpdb":    RPDB_KEY,
}

def _notify(msg, icon=xbmcgui.NOTIFICATION_INFO, ms=3000):
    xbmcgui.Dialog().notification("setapikeys", msg, icon, ms)

def _save_to_addon(target_addon_id, keys, value):
    ok = False
    errors = []
    try:
        target = xbmcaddon.Addon(id=target_addon_id)
    except Exception as e:
        errors.append("No se pudo abrir el addon: %s" % e)
        return False, errors

    for k in keys:
        try:
            # usa setSettingString si existe (Kodi 20+), si no setSetting
            setter = getattr(target, "setSettingString", None) or target.setSetting
            setter(k, value)
            # comprobación
            getter = getattr(target, "getSettingString", None) or target.getSetting
            if getter(k) == value:
                ok = True
            else:
                errors.append("Escritura fallida en id '%s'" % k)
        except Exception as e:
            errors.append("Error en '%s': %s" % (k, e))
    return ok, errors

def _save_to_skinstring(keys, value):
    ok = False
    errors = []
    for name in keys:
        try:
            xbmc.executebuiltin(f"Skin.SetString({name},{value})")
            ok = True
        except Exception as e:
            errors.append("Error Skin.SetString '%s': %s" % (name, e))
    return ok, errors

def save(provider, target_key):
    if target_key not in TARGETS:
        _notify("Destino desconocido: %s" % target_key, xbmcgui.NOTIFICATION_ERROR)
        return
    if provider not in PROVIDER_TO_KEY:
        _notify("Proveedor desconocido: %s" % provider, xbmcgui.NOTIFICATION_ERROR)
        return

    value = PROVIDER_TO_KEY[provider]
    kind, addon_id, keys = TARGETS[target_key]

    if kind == "addon":
        ok, errors = _save_to_addon(addon_id, keys, value)
    else:
        ok, errors = _save_to_skinstring(keys, value)

    if ok:
        _notify("API guardada en %s" % target_key)
    else:
        _notify("No se pudo guardar en %s" % target_key, xbmcgui.NOTIFICATION_ERROR)
        if errors:
            xbmc.log("[setapikeys] " + "; ".join(errors), xbmc.LOGERROR)

def parse_params(arg):
    # Para scripts, sys.argv puede llegar como: ['default.py', 'action=save&target=seren&provider=omdb']
    if not arg:
        return {}
    if arg.startswith("?"):
        arg = arg[1:]
    parts = urllib.parse.parse_qs(arg, keep_blank_values=True)
    # a valores simples
    return {k: v[0] for k, v in parts.items()}

def main():
    # Si se ejecuta sin params, muestra un pequeño menú para comodidad
    params = parse_params(sys.argv[1] if len(sys.argv) > 1 else "")
    action = params.get("action")
    if action == "save":
        save(params.get("provider", ""), params.get("target", ""))
        return

    # Menú rápido alternativo
    choices = [
        ("Seren → Guardar OMDb", "save", {"provider":"omdb","target":"seren"}),
        ("TMDb Helper → Guardar MDBList", "save", {"provider":"mdblist","target":"tmdb.helper"}),
        ("Umbrella → Guardar MDBList", "save", {"provider":"mdblist","target":"umbrella"}),
        ("A4KSubtitles → Guardar SubDL", "save", {"provider":"subdl","target":"a4ksubtitles"}),
        ("POV → Guardar RPDB", "save", {"provider":"rpdb","target":"pov"}),
        ("Skin FENtastic → Guardar MDBList", "save", {"provider":"mdblist","target":"skin_fentastic"}),
    ]
    labels = [c[0] for c in choices] + ["Salir"]
    idx = xbmcgui.Dialog().select("setapikeys", labels)
    if idx == -1 or idx == len(labels)-1:
        return
    _, act, kw = choices[idx]
    if act == "save":
        save(kw["provider"], kw["target"])

if __name__ == "__main__":
    main()
