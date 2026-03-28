# -*- coding: utf-8 -*-
import sys
import urllib.parse
import xbmc
import xbmcgui
import xbmcaddon

# ====== TUS CLAVES PERSONALES (hardcoded – uso personal) =============
OMDB_KEY      = "3b6c28ce"
MDBLIST_KEY   = "xma2hxonarl718z4w7adchsef"
SUBDL_KEY     = "lj9neeNGx37abT59gZYQaF_8iDSwNrT_"
SUBSOURCE_KEY = "sk_e231cadbaa9900ae2225bf7cdb8805fa11a74423d5c7cfa4eab58402123ff810"
RPDB_KEY      = "t0-free-rpdb"
SUBSRO_KEY    = "fb3f06ba411d25cf04e3fbb0e2cd9884ae0c215cbc2886d236d8495f5f6e85ad"
# =====================================================================

ADDON_ID = "plugin.program.setapikeys"
ADDON = xbmcaddon.Addon(id=ADDON_ID)

# Mapa de destinos → (tipo, addon_id, [posibles setting ids])
# tipo "addon"      → xbmcaddon.Addon.setSetting estándar
# tipo "fenlight"   → cache interna de Fen Light (sqlite + Window property)
# tipo "luc_mdb"    → addon estándar + activa mdblist.enable automáticamente
# tipo "skinstring" → Skin.SetString
TARGETS = {
    "seren":                  ("addon",      "plugin.video.seren",             ["omdb.apikey"]),
    "fenlight":               ("fenlight",   "plugin.video.fenlight",          ["omdb_api"]),
    "luc_kodi_omdb":          ("addon",      "plugin.video.luc_kodi",          ["omdb.apikey"]),
    "luc_kodi_mdblist":       ("luc_mdb",    "plugin.video.luc_kodi",          ["mdblist.apikey"]),
    "themoviedb.helper":      ("addon",      "plugin.video.themoviedb.helper", ["mdblist_apikey", "mdblist.api", "mdblist_api_key"]),
    "umbrella":               ("addon",      "plugin.video.umbrella",          ["mdblist.api", "mdblist_key"]),
    "a4ksubtitles":           ("addon",      "service.subtitles.a4ksubtitles", ["subdl.apikey"]),
    "a4ksubtitles.subsource": ("addon",      "service.subtitles.a4ksubtitles", ["subsource.apikey"]),
    "pov":                    ("addon",      "plugin.video.pov",               ["rpdb_api_key"]),
    "subsro":                 ("addon",      "service.subtitles.subsro",       ["api_key"]),
    "skin_fentastic":         ("skinstring", None,                             ["mdblist_api_key"]),
    "skin_nimbus":            ("skinstring", None,                             ["mdblist_api_key"]),
}

PROVIDER_TO_KEY = {
    "omdb":      OMDB_KEY,
    "mdblist":   MDBLIST_KEY,
    "subdl":     SUBDL_KEY,
    "subsource": SUBSOURCE_KEY,
    "rpdb":      RPDB_KEY,
    "subsro":    SUBSRO_KEY,
}

# ====== SKIN INFO ======================================================
SKIN_INFO = {
    "skin_fentastic": {"addon_id": "skin.fentastic", "label": "Skin FENtastic"},
    "skin_nimbus":    {"addon_id": "skin.nimbus",    "label": "Skin Nimbus"},
}

def _skin_is_installed(target_key):
    info = SKIN_INFO.get(target_key)
    if not info:
        return True
    try:
        return xbmc.getCondVisibility(f"System.HasAddon({info['addon_id']})") == 1
    except Exception:
        return False

def _skin_is_current(target_key):
    info = SKIN_INFO.get(target_key)
    if not info:
        return False
    try:
        return xbmc.getSkinDir() == info["addon_id"]
    except Exception:
        return False


# ====== SYNC: vuelca las keys hardcoded al settings.xml del propio addon =
# Así se ven enmascaradas (hidden) cuando el usuario abre los ajustes.
def _sync_keys_to_settings():
    pairs = [
        ("key_omdb",      OMDB_KEY),
        ("key_mdblist",   MDBLIST_KEY),
        ("key_subdl",     SUBDL_KEY),
        ("key_subsource", SUBSOURCE_KEY),
        ("key_rpdb",      RPDB_KEY),
        ("key_subsro",    SUBSRO_KEY),
    ]
    for sid, val in pairs:
        try:
            ADDON.setSetting(sid, val)
        except Exception:
            pass
# =======================================================================


def _notify(msg, icon=xbmcgui.NOTIFICATION_INFO, ms=3000):
    xbmcgui.Dialog().notification("setapikeys", msg, icon, ms)


# ====== FUNCIONES DE ESCRITURA ==========================================
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


def _save_to_luc_mdblist(target_addon_id, keys, value):
    """
    luc_kodi cachea todos sus settings en Window(10000)['luc_kodi_settings']
    al arrancar el servicio. onSettingsChanged() solo limpia esa caché cuando
    el usuario cambia algo desde el diálogo propio de luc_kodi — NO se dispara
    con setSetting() externo (el que usamos nosotros desde setapikeys).

    Consecuencia: aunque escribamos mdblist.enable='true' en disco, luc_kodi
    sigue leyendo 'false' desde la caché en memoria → scrobbling nunca arranca.

    FIX: después de escribir los settings, limpiamos la caché manualmente.
    La próxima vez que luc_kodi llame a control.setting() reconstruye el dict
    desde el settings.xml del userdata, donde ya están los valores correctos.
    """
    ok, errors = _save_to_addon(target_addon_id, keys, value)
    if ok:
        try:
            target = xbmcaddon.Addon(id=target_addon_id)
            setter = getattr(target, "setSettingString", None) or target.setSetting
            setter("mdblist.enable", "true")
        except Exception as e:
            errors.append("No se pudo activar mdblist.enable: %s" % e)
        try:
            # Limpia la caché de Window para que luc_kodi re-lea del disco
            xbmcgui.Window(10000).clearProperty("luc_kodi_settings")
        except Exception as e:
            errors.append("No se pudo limpiar caché de luc_kodi: %s" % e)
    return ok, errors


def _save_to_fenlight(target_addon_id, setting_id, value):
    """Fen Light NO usa settings.xml estándar: guarda en su settings_cache (sqlite + Window(10000))."""
    ok = False
    errors = []
    try:
        import os
        fen = xbmcaddon.Addon(id=target_addon_id)
        fen_path = fen.getAddonInfo("path")
        lib_path = os.path.join(fen_path, "resources", "lib")
        if lib_path not in sys.path:
            sys.path.insert(0, lib_path)
        from caches.settings_cache import set_setting, get_setting
        set_setting(setting_id, value)
        if get_setting("fenlight.%s" % setting_id, "") == value:
            ok = True
        else:
            try:
                prop = xbmcgui.Window(10000).getProperty("fenlight.%s" % setting_id)
                if prop == value:
                    ok = True
                else:
                    errors.append("Escritura fallida en fenlight.%s" % setting_id)
            except Exception as e:
                errors.append("No se pudo verificar property: %s" % e)
    except Exception as e:
        errors.append("Error Fen Light cache: %s" % e)
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
# =======================================================================


def _is_active(target_key, provider=None):
    """Devuelve True si el destino ya tiene algún valor para sus claves."""
    kind, addon_id, keys = TARGETS[target_key]
    try:
        if kind == "fenlight":
            val = xbmcgui.Window(10000).getProperty("fenlight.%s" % keys[0])
            return bool(val and val not in ("empty_setting",))
        if kind in ("addon", "luc_mdb"):
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
            val = xbmc.getInfoLabel("Skin.String(mdblist_api_key)")
            return bool(val)
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

    if kind == "fenlight":
        ok, errors = _save_to_fenlight(addon_id, keys[0], value)
    elif kind == "luc_mdb":
        ok, errors = _save_to_luc_mdblist(addon_id, keys, value)
    elif kind == "addon":
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
    # Sincroniza las keys hardcoded al settings.xml para visualización hidden
    _sync_keys_to_settings()

    params = parse_params(sys.argv[1] if len(sys.argv) > 1 else "")
    action = params.get("action")
    if action == "save":
        save(params.get("provider", ""), params.get("target", ""))
        return

    items = [
        ("Seren → Guardar OMDb",                    "omdb",      "seren"),
        ("Fen Light → Guardar OMDb",                "omdb",      "fenlight"),
        ("luc_kodi → Guardar OMDb",                 "omdb",      "luc_kodi_omdb"),
        ("luc_kodi → Guardar MDBList",              "mdblist",   "luc_kodi_mdblist"),
        ("TheMovieDB-Helper → Guardar MDBList",     "mdblist",   "themoviedb.helper"),
        ("Umbrella → Guardar MDBList",              "mdblist",   "umbrella"),
        ("A4KSubtitles → Guardar SubDL",            "subdl",     "a4ksubtitles"),
        ("A4KSubtitles → Guardar SubSource",        "subsource", "a4ksubtitles.subsource"),
        ("POV → Guardar RPDB",                      "rpdb",      "pov"),
        ("Subs.ro → Guardar API key",               "subsro",    "subsro"),
        ("Skin FENtastic → Guardar MDBList",        "mdblist",   "skin_fentastic"),
        ("Skin Nimbus → Guardar MDBList",           "mdblist",   "skin_nimbus"),
    ]

    choices = []
    for base_label, provider, target in items:
        no_instalado = False
        if target in SKIN_INFO and not _skin_is_installed(target):
            no_instalado = True
        elif TARGETS[target][0] in ("addon", "luc_mdb", "fenlight"):
            _aid = TARGETS[target][1]
            try:
                xbmcaddon.Addon(id=_aid)
            except Exception:
                no_instalado = True

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
    if idx == -1 or idx == len(labels) - 1:
        return
    _, act, kw = choices[idx]
    if act == "save":
        save(kw["provider"], kw["target"])


if __name__ == "__main__":
    main()
