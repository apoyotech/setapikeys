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
SUBSOURCE_KEY = "sk_e231cadbaa9900ae2225bf7cdb8805fa11a74423d5c7cfa4eab58402123ff810"
RPDB_KEY     = "t0-free-rpdb"
# =====================================================================

ADDON_ID = "plugin.program.setapikeys"
ADDON = xbmcaddon.Addon(id=ADDON_ID)

# Mapa de destinos → (tipo, id, posibles claves)
# tipo "addon" = setSetting, tipo "skinstring" = Skin.SetString
TARGETS = {
    "seren": ("addon", "plugin.video.seren", ["omdb.apikey"]),
    "themoviedb.helper": ("addon", "plugin.video.themoviedb.helper", ["mdblist_apikey", "mdblist.api", "mdblist_api_key"]),
    "umbrella": ("addon", "plugin.video.umbrella", ["mdblist.api", "mdblist_key"]),
    "a4ksubtitles": ("addon", "service.subtitles.a4ksubtitles", ["subdl.apikey"]),
    "a4ksubtitles.subsource": ("addon", "service.subtitles.a4ksubtitles", ["subsource.apikey"]),
    "pov": ("addon", "plugin.video.pov", ["rpdb_api_key"]),
    "skin_fentastic": ("skinstring", None, ["mdblist_api_key"]),
    "skin_nimbus": ("skinstring", None, ["mdblist_api_key"]),
}

PROVIDER_TO_KEY = {
    "subsource": SUBSOURCE_KEY,
    "omdb":  OMDB_KEY,
    "mdblist": MDBLIST_KEY,
    "subdl": SUBDL_KEY,
    "rpdb": RPDB_KEY,
}

# ====== SKIN INFO (detecta instalación y skin activo) ======
SKIN_INFO = {
    "skin_fentastic": {"addon_id": "skin.fentastic", "label": "Skin FENtastic"},
    "skin_nimbus": {"addon_id": "skin.nimbus",    "label": "Skin Nimbus"},
}

def _skin_is_installed(target_key):
    info = SKIN_INFO.get(target_key)
    if not info:
        return True  # No es un skin target
    try:
        return xbmc.getCondVisibility(f"System.HasAddon({info['addon_id']})") == 1
    except Exception:
        return False

def _skin_is_current(target_key):
    info = SKIN_INFO.get(target_key)
    if not info:
        return False
    try:
        return xbmc.getSkinDir() == info['addon_id']
    except Exception:
        return False
# ===========================================================

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
            setter = getattr(target, "setSettingString", None) or target.setSetting
            setter(k, value)
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
            errors.append("Error en skinstring '%s': %s" % (name, e))
    return ok, errors

def _is_active(target_key, provider=None):
    """Devuelve True si el destino ya tiene algún valor para sus claves (o Skin String)."""
    kind, addon_id, keys = TARGETS[target_key]
    try:
        if kind == "addon":
            try:
                target = xbmcaddon.Addon(id=addon_id)
            except Exception:
                return False
            getter = getattr(target, "getSettingString", None) or target.getSetting
            for k in keys:
                try:
                    if getter(k):
                        return True
                except Exception:
                    continue
            return False
        else:  # skinstring
            try:
                val = xbmc.getInfoLabel("Skin.String(mdblist_api_key)")
                return bool(val)
            except Exception:
                return False
    except Exception:
        return False

def parse_params(arg):
    if not arg:
        return {}
    if arg.startswith("?"):
        arg = arg[1:]
    parts = urllib.parse.parse_qs(arg, keep_blank_values=True)
    return {k: v[0] for k, v in parts.items()}

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
    elif kind == "skinstring":
        if not _skin_is_installed(target_key):
            _notify("Destino no instalado: %s" % target_key, xbmcgui.NOTIFICATION_ERROR)
            return
        ok, errors = _save_to_skinstring(keys, value)
    else:
        ok, errors = False, ["Tipo desconocido"]

    if ok:
        _notify("API guardada en %s" % target_key)
    else:
        _notify("No se pudo guardar en %s" % target_key, xbmcgui.NOTIFICATION_ERROR)
        if errors:
            xbmc.log("[setapikeys] " + "; ".join(errors), xbmc.LOGERROR)

def main():
    params = parse_params(sys.argv[1] if len(sys.argv) > 1 else "")
    action = params.get("action")
    if action == "save":
        save(params.get("provider", ""), params.get("target", ""))
        return

    items = [
        ("Seren → Guardar OMDb",             "omdb",    "seren"),
        ("TheMovieDB-Helper → Guardar MDBList", "mdblist", "themoviedb.helper"),
        ("Umbrella → Guardar MDBList",       "mdblist", "umbrella"),
        ("A4KSubtitles → Guardar SubDL",     "subdl",   "a4ksubtitles"),
        ("A4KSubtitles → Guardar SubSource",  "subsource", "a4ksubtitles.subsource"),
        ("POV → Guardar RPDB",               "rpdb",    "pov"),
        ("Skin FENtastic → Guardar MDBList", "mdblist", "skin_fentastic"),
        ("Skin Nimbus → Guardar MDBList",    "mdblist", "skin_nimbus"),
    ]

    choices = []
    for base_label, provider, target in items:
        no_instalado = (target in SKIN_INFO and not _skin_is_installed(target))
        actual = " [COLOR deepskyblue](actual)[/COLOR]" if _skin_is_current(target) else ""
        if _is_active(target, provider):
            estado = " [COLOR mediumspringgreen]activo[/COLOR]"
        else:
            estado = " [COLOR red]inactivo[/COLOR]"
        if no_instalado:
            estado += " [COLOR dimgray](no instalado)[/COLOR]"
        choices.append((base_label + actual + estado, "save", {"provider": provider, "target": target}))

    labels = [c[0] for c in choices] + ["Salir"]
    idx = xbmcgui.Dialog().select("setapikeys", labels)
    if idx == -1 or idx == len(labels)-1:
        return
    _, act, kw = choices[idx]
    if act == "save":
        save(kw["provider"], kw["target"])

if __name__ == "__main__":
    main()
