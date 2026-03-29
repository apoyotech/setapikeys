# -*- coding: utf-8 -*-
import sys
import urllib.parse
import xbmc
import xbmcgui
import xbmcaddon

# ====== TUS CLAVES PERSONALES (hardcoded – uso personal) =============
OMDB_KEY      = "pon tu api aqui"
MDBLIST_KEY   = "pon tu api aqui"
SUBDL_KEY     = "pon tu api aqui"
SUBSOURCE_KEY = "pon tu api aqui"
RPDB_KEY      = "pon tu api aqui"
SUBSRO_KEY    = "pon tu api aqui"

# AIOStreams – instancia nhyira (index '3')
AIOSTREAMS_NHYIRA_UUID      = "pon tu nhyira UUID aqui"
# AIOStreams – instancia stremio.ru (index '1')
AIOSTREAMS_STREMIO_UUID     = "pon tu stremio.ru UUID aqui"
# AIOStreams – password compartida entre instancias
AIOSTREAMS_PASSWORD         = "pon tu instance password aqui"

# MediaFusion – instancia midnightignite (index '0')
MEDIAFUSION_MIDNIGHT_SECRET = "pon tu midnightignite secret aqui"
# =====================================================================

ADDON_ID = "plugin.program.setapikeys"
ADDON = xbmcaddon.Addon(id=ADDON_ID)

# Mapa de destinos → (tipo, addon_id, payload)
#
# tipo "addon"        → payload = [setting_id, ...]    escribe un único valor
# tipo "fenlight"     → payload = [setting_id]         cache interna de Fen Light
# tipo "luc_mdb"      → payload = [setting_id]         addon + activa mdblist.enable + limpia caché
# tipo "luc_provider" → payload = {setting_id: value}  escribe múltiples campos fijos
#                                                       + activa el provider + limpia caché
# tipo "skinstring"   → payload = [skin_string_name]   Skin.SetString
TARGETS = {
    "seren":                  ("addon",         "plugin.video.seren",             ["omdb.apikey"]),
    "fenlight":               ("fenlight",      "plugin.video.fenlight",          ["omdb_api"]),
    "luc_kodi_omdb":          ("addon",         "plugin.video.luc_kodi",          ["omdb.apikey"]),
    "luc_kodi_mdblist":       ("luc_mdb",       "plugin.video.luc_kodi",          ["mdblist.apikey"]),
    "luc_kodi_aio_nhyira":    ("luc_provider",  "plugin.video.luc_kodi",          {
        "aiostreams.url":      "3",
        "aiostreams.uuid":     AIOSTREAMS_NHYIRA_UUID,
        "aiostreams.password": AIOSTREAMS_PASSWORD,
        "provider.aiostreams": "true",
    }),
    "luc_kodi_aio_stremio":   ("luc_provider",  "plugin.video.luc_kodi",          {
        "aiostreams.url":      "1",
        "aiostreams.uuid":     AIOSTREAMS_STREMIO_UUID,
        "aiostreams.password": AIOSTREAMS_PASSWORD,
        "provider.aiostreams": "true",
    }),
    "luc_kodi_mediafusion":   ("luc_provider",  "plugin.video.luc_kodi",          {
        "mediafusion.url":      "0",
        "mediafusion.secret":   MEDIAFUSION_MIDNIGHT_SECRET,
        "provider.mediafusion": "true",
    }),
    "themoviedb.helper":      ("addon",         "plugin.video.themoviedb.helper", ["mdblist_apikey", "mdblist.api", "mdblist_api_key"]),
    "umbrella":               ("addon",         "plugin.video.umbrella",          ["mdblist.api", "mdblist_key"]),
    "a4ksubtitles":           ("addon",         "service.subtitles.a4ksubtitles", ["subdl.apikey"]),
    "a4ksubtitles.subsource": ("addon",         "service.subtitles.a4ksubtitles", ["subsource.apikey"]),
    "pov":                    ("addon",         "plugin.video.pov",               ["rpdb_api_key"]),
    "subsro":                 ("addon",         "service.subtitles.subsro",       ["api_key"]),
    "skin_fentastic":         ("skinstring",    None,                             ["mdblist_api_key"]),
    "skin_nimbus":            ("skinstring",    None,                             ["mdblist_api_key"]),
}

PROVIDER_TO_KEY = {
    "omdb":      OMDB_KEY,
    "mdblist":   MDBLIST_KEY,
    "subdl":     SUBDL_KEY,
    "subsource": SUBSOURCE_KEY,
    "rpdb":      RPDB_KEY,
    "subsro":    SUBSRO_KEY,
    # luc_provider no usa PROVIDER_TO_KEY — sus valores están en TARGETS
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


# ====== SYNC: vuelca las keys hardcoded al settings.xml para visualización hidden =
def _sync_keys_to_settings():
    pairs = [
        ("key_omdb",               OMDB_KEY),
        ("key_mdblist",            MDBLIST_KEY),
        ("key_subdl",              SUBDL_KEY),
        ("key_subsource",          SUBSOURCE_KEY),
        ("key_rpdb",               RPDB_KEY),
        ("key_subsro",             SUBSRO_KEY),
        ("key_aio_nhyira_uuid",    AIOSTREAMS_NHYIRA_UUID),
        ("key_aio_stremio_uuid",   AIOSTREAMS_STREMIO_UUID),
        ("key_aio_password",       AIOSTREAMS_PASSWORD),
        ("key_mediafusion_secret", MEDIAFUSION_MIDNIGHT_SECRET),
    ]
    for sid, val in pairs:
        try:
            ADDON.setSetting(sid, val)
        except Exception:
            pass
# =========================================================================


def _notify(msg, icon=xbmcgui.NOTIFICATION_INFO, ms=3000):
    xbmcgui.Dialog().notification("setapikeys", msg, icon, ms)


def _clear_luc_cache():
    """Limpia la caché de settings de luc_kodi en Window(10000)."""
    try:
        xbmcgui.Window(10000).clearProperty("luc_kodi_settings")
    except Exception as e:
        xbmc.log("[setapikeys] No se pudo limpiar caché luc_kodi: %s" % e, xbmc.LOGWARNING)


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
    Escribe mdblist.apikey, activa mdblist.enable y limpia la caché de
    luc_kodi en Window(10000) para que los nuevos valores sean efectivos
    inmediatamente sin reinicio de Kodi.
    """
    ok, errors = _save_to_addon(target_addon_id, keys, value)
    if ok:
        try:
            target = xbmcaddon.Addon(id=target_addon_id)
            setter = getattr(target, "setSettingString", None) or target.setSetting
            setter("mdblist.enable", "true")
        except Exception as e:
            errors.append("No se pudo activar mdblist.enable: %s" % e)
        _clear_luc_cache()
    return ok, errors


def _save_to_luc_provider(target_addon_id, settings_dict):
    """
    Escribe múltiples setting_id → value de una vez en luc_kodi.
    Usado para proveedores custom (AIOStreams, MediaFusion) que necesitan
    varios campos simultáneamente: instance, uuid/secret y enable flag.
    Limpia la caché de luc_kodi al terminar.
    """
    ok = False
    errors = []
    try:
        target = xbmcaddon.Addon(id=target_addon_id)
    except Exception as e:
        errors.append("No se pudo abrir el addon: %s" % e)
        return False, errors
    setter = getattr(target, "setSettingString", None) or target.setSetting
    getter = getattr(target, "getSettingString", None) or target.getSetting
    for setting_id, value in settings_dict.items():
        try:
            setter(setting_id, value)
            if getter(setting_id) == value:
                ok = True
            else:
                errors.append("Escritura fallida en id '%s'" % setting_id)
        except Exception as e:
            errors.append("Error en '%s': %s" % (setting_id, e))
    if ok:
        _clear_luc_cache()
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
# =========================================================================


def _is_active(target_key):
    """Devuelve True si el destino ya tiene algún valor guardado."""
    kind, addon_id, payload = TARGETS[target_key]
    try:
        if kind == "fenlight":
            val = xbmcgui.Window(10000).getProperty("fenlight.%s" % payload[0])
            return bool(val and val not in ("empty_setting",))

        if kind in ("addon", "luc_mdb"):
            try:
                target = xbmcaddon.Addon(id=addon_id)
            except Exception:
                return False
            getter = getattr(target, "getSettingString", None) or target.getSetting
            for k in payload:
                try:
                    if getter(k):
                        return True
                except Exception:
                    continue
            return False

        if kind == "luc_provider":
            try:
                target = xbmcaddon.Addon(id=addon_id)
            except Exception:
                return False
            getter = getattr(target, "getSettingString", None) or target.getSetting
            # Comprueba el primer setting no-booleano del dict (uuid o secret)
            for k in payload:
                if k.startswith("provider."):
                    continue
                try:
                    return bool(getter(k))
                except Exception:
                    continue
            return False

        # skinstring
        val = xbmc.getInfoLabel("Skin.String(%s)" % payload[0])
        return bool(val)
    except Exception:
        return False


def _addon_is_installed(target_key):
    kind, addon_id, _ = TARGETS[target_key]
    if kind == "skinstring":
        return _skin_is_installed(target_key)
    if addon_id:
        try:
            xbmcaddon.Addon(id=addon_id)
            return True
        except Exception:
            return False
    return True


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

    kind, addon_id, payload = TARGETS[target_key]

    # luc_provider: los valores están embebidos en el propio payload de TARGETS
    if kind == "luc_provider":
        ok, errors = _save_to_luc_provider(addon_id, payload)

    else:
        if provider not in PROVIDER_TO_KEY:
            _notify("Proveedor desconocido: %s" % provider, xbmcgui.NOTIFICATION_ERROR)
            return
        value = PROVIDER_TO_KEY[provider]

        if kind == "fenlight":
            ok, errors = _save_to_fenlight(addon_id, payload[0], value)
        elif kind == "luc_mdb":
            ok, errors = _save_to_luc_mdblist(addon_id, payload, value)
        elif kind == "addon":
            ok, errors = _save_to_addon(addon_id, payload, value)
        elif kind == "skinstring":
            if not _skin_is_installed(target_key):
                _notify("Destino no instalado: %s" % target_key, xbmcgui.NOTIFICATION_ERROR)
                return
            ok, errors = _save_to_skinstring(payload, value)
        else:
            ok, errors = False, ["Tipo desconocido: %s" % kind]

    if ok:
        _notify("Guardado en %s" % target_key)
    else:
        _notify("No se pudo guardar en %s" % target_key, xbmcgui.NOTIFICATION_ERROR)
        if errors:
            xbmc.log("[setapikeys] " + "; ".join(errors), xbmc.LOGERROR)


def main():
    _sync_keys_to_settings()

    params = parse_params(sys.argv[1] if len(sys.argv) > 1 else "")
    action = params.get("action")
    if action == "save":
        save(params.get("provider", ""), params.get("target", ""))
        return

    items = [
        # label,                                          provider,       target
        ("Seren → Guardar OMDb",                          "omdb",         "seren"),
        ("Fen Light → Guardar OMDb",                      "omdb",         "fenlight"),
        ("luc_kodi → Guardar OMDb",                       "omdb",         "luc_kodi_omdb"),
        ("luc_kodi → Guardar MDBList",                    "mdblist",      "luc_kodi_mdblist"),
        ("luc_kodi → AIOStreams nhyira",                   "luc_provider", "luc_kodi_aio_nhyira"),
        ("luc_kodi → AIOStreams stremio.ru",               "luc_provider", "luc_kodi_aio_stremio"),
        ("luc_kodi → MediaFusion midnightignite",         "luc_provider", "luc_kodi_mediafusion"),
        ("TheMovieDB-Helper → Guardar MDBList",           "mdblist",      "themoviedb.helper"),
        ("Umbrella → Guardar MDBList",                    "mdblist",      "umbrella"),
        ("A4KSubtitles → Guardar SubDL",                  "subdl",        "a4ksubtitles"),
        ("A4KSubtitles → Guardar SubSource",              "subsource",    "a4ksubtitles.subsource"),
        ("POV → Guardar RPDB",                            "rpdb",         "pov"),
        ("Subs.ro → Guardar API key",                     "subsro",       "subsro"),
        ("Skin FENtastic → Guardar MDBList",              "mdblist",      "skin_fentastic"),
        ("Skin Nimbus → Guardar MDBList",                 "mdblist",      "skin_nimbus"),
    ]

    choices = []
    for base_label, provider, target in items:
        no_instalado = not _addon_is_installed(target)
        actual = " [COLOR deepskyblue](actual)[/COLOR]" if _skin_is_current(target) else ""
        estado = (" [COLOR mediumspringgreen]activo[/COLOR]"
                  if _is_active(target)
                  else " [COLOR red]inactivo[/COLOR]")
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
