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
WYZIE_KEY     = "pon tu api aqui"
ORION_KEY     = "pon tu api aqui"

# Sootio – token completo (URL desde sooti.info/configure)
# El scraper acepta URL completa, JSON crudo, base64 o JSON url-encoded.
SOOTIO_TOKEN  = "pon tu sootio token aqui"

# OpenSubtitles.com
OPENSUBS_USER = "pon tu user aqui"
OPENSUBS_PASS = "pon tu password aqui"

# Gemini (Google AI Studio) — 3 claves rotatorias
GEMINI_KEY_1  = "pon tu api aqui"
GEMINI_KEY_2  = "pon tu api aqui"
GEMINI_KEY_3  = "pon tu api aqui"

# AIOStreams – instancia midnightignite (index '0' en luc_kodi v0.0.86+)
AIOSTREAMS_MIDNIGHT_UUID    = "pon tu UUID aqui"
# AIOStreams – instancia stremio.ru (index '1')
AIOSTREAMS_STREMIO_UUID     = "pon tu UUID aqui"
# AIOStreams – password compartida entre instancias
AIOSTREAMS_PASSWORD         = "pon tu password aqui"

# MediaFusion – instancia midnightignite (index '0')
MEDIAFUSION_MIDNIGHT_SECRET = "pon tu secret aqui"
# =====================================================================

ADDON_ID = "plugin.program.setapikeys"
ADDON = xbmcaddon.Addon(id=ADDON_ID)

# ====== TARGETS ======================================================
TARGETS = {
    "seren":                  ("addon",        "plugin.video.seren",               ["omdb.apikey"]),
    "fenlight":               ("fenlight",     "plugin.video.fenlight",             ["omdb_api"]),
    "luc_kodi_omdb":          ("addon",        "plugin.video.luc_kodi",             ["omdb.apikey"]),
    "luc_kodi_mdblist":       ("luc_mdb",      "plugin.video.luc_kodi",             ["mdblist.apikey"]),
    "luc_kodi_opensubs":      ("luc_provider", "plugin.video.luc_kodi",             {
        "opensubsusername": OPENSUBS_USER,
        "opensubspassword": OPENSUBS_PASS,
    }),
    "umbrella_opensubs":      ("addon",        "plugin.video.umbrella",             ["opensubsusername", "opensubspassword"]),
    # Orion scraper — activa provider + escribe API key + limpia caché luc_kodi
    "luc_kodi_orion":         ("luc_provider", "plugin.video.luc_kodi",             {
        "orion.api_key":    ORION_KEY,
        "provider.orion":  "true",
    }),
    # Sootio scraper — instancia oficial (índice 0) + token completo + limpia caché
    "luc_kodi_sootio":        ("luc_provider", "plugin.video.luc_kodi",             {
        "sootio.url":      "0",
        "sootio.config":   SOOTIO_TOKEN,
        "provider.sootio": "true",
    }),
    # AIOStreams midnightignite — índice 0 desde luc_kodi v0.0.86
    "luc_kodi_aio_midnight":  ("luc_provider", "plugin.video.luc_kodi",             {
        "aiostreams.url":      "0",
        "aiostreams.uuid":     AIOSTREAMS_MIDNIGHT_UUID,
        "aiostreams.password": AIOSTREAMS_PASSWORD,
        "provider.aiostreams": "true",
    }),
    "luc_kodi_aio_stremio":   ("luc_provider", "plugin.video.luc_kodi",             {
        "aiostreams.url":      "1",
        "aiostreams.uuid":     AIOSTREAMS_STREMIO_UUID,
        "aiostreams.password": AIOSTREAMS_PASSWORD,
        "provider.aiostreams": "true",
    }),
    "luc_kodi_mediafusion":   ("luc_provider", "plugin.video.luc_kodi",             {
        "mediafusion.url":      "0",
        "mediafusion.secret":   MEDIAFUSION_MIDNIGHT_SECRET,
        "provider.mediafusion": "true",
    }),
    "themoviedb.helper":      ("addon",        "plugin.video.themoviedb.helper",    ["mdblist_apikey", "mdblist.api", "mdblist_api_key"]),
    "umbrella":               ("addon",        "plugin.video.umbrella",             ["mdblist.api", "mdblist_key"]),
    "a4ksubtitles":           ("addon",        "service.subtitles.a4ksubtitles",    ["subdl.apikey"]),
    "a4ksubtitles.subsource": ("addon",        "service.subtitles.a4ksubtitles",    ["subsource.apikey"]),
    "pov_rpdb":               ("addon",        "plugin.video.pov",                  ["rpdb_api_key"]),
    "pov_wyzie":              ("addon",        "plugin.video.pov",                  ["subtitles.apikey"]),
    "wyzie_service":          ("addon",        "service.subtitles.wyzie",           ["wyzie_api_key"]),
    "substudio_wyzie":        ("addon",        "service.subtitles.substudio",       ["wyzie_api_key"]),
    "wyzie_gemini":           ("gemini",       "service.subtitles.wyzie",           {
        "api_key_r3_1": GEMINI_KEY_1,
        "api_key_r3_2": GEMINI_KEY_2,
        "api_key_r3_3": GEMINI_KEY_3,
    }),
    "substudio_gemini":       ("gemini",       "service.subtitles.substudio",       {
        "api_key_1": GEMINI_KEY_1,
        "api_key_2": GEMINI_KEY_2,
        "api_key_3": GEMINI_KEY_3,
    }),
    "skin_fentastic":         ("skinstring",   None,                                ["mdblist_api_key"]),
    "skin_nimbus":            ("skinstring",   None,                                ["mdblist_api_key"]),
}

PROVIDER_TO_KEY = {
    "omdb":      OMDB_KEY,
    "mdblist":   MDBLIST_KEY,
    "subdl":     SUBDL_KEY,
    "subsource": SUBSOURCE_KEY,
    "rpdb":      RPDB_KEY,
    "wyzie":     WYZIE_KEY,
    "orion":     ORION_KEY,
}

# ====== MENÚ EN DOS NIVELES ==========================================
MENU = [
    ("[COLOR gold]● OMDb[/COLOR]", [
        ("Seren",                    "omdb",         "seren"),
        ("Fen Light",                "omdb",         "fenlight"),
        ("luc_kodi",                 "omdb",         "luc_kodi_omdb"),
    ]),
    ("[COLOR deepskyblue]● MDBList[/COLOR]", [
        ("luc_kodi",                 "mdblist",      "luc_kodi_mdblist"),
        ("TheMovieDB Helper",        "mdblist",      "themoviedb.helper"),
        ("Umbrella",                 "mdblist",      "umbrella"),
        ("Skin FENtastic",           "mdblist",      "skin_fentastic"),
        ("Skin Nimbus",              "mdblist",      "skin_nimbus"),
    ]),
    ("[COLOR mediumspringgreen]● OpenSubtitles.com[/COLOR]", [
        ("luc_kodi",                 "luc_provider", "luc_kodi_opensubs"),
        ("Umbrella",                 "opensubs",     "umbrella_opensubs"),
    ]),
    ("[COLOR orange]● Providers  [COLOR dimgray](luc_kodi custom scrapers)[/COLOR][/COLOR]", [
        ("Orion",                    "luc_provider", "luc_kodi_orion"),
        ("Sootio",                   "luc_provider", "luc_kodi_sootio"),
        ("AIOStreams midnight",       "luc_provider", "luc_kodi_aio_midnight"),
        ("AIOStreams stremio.ru",     "luc_provider", "luc_kodi_aio_stremio"),
        ("MediaFusion midnight",     "luc_provider", "luc_kodi_mediafusion"),
    ]),
    ("[COLOR mediumpurple]● Subtítulos[/COLOR]", [
        ("A4KSubtitles SubDL",       "subdl",        "a4ksubtitles"),
        ("A4KSubtitles SubSource",   "subsource",    "a4ksubtitles.subsource"),
        ("POV Wyzie",                "wyzie",        "pov_wyzie"),
        ("Wyzie Service",            "wyzie",        "wyzie_service"),
        ("SubStudio Wyzie",          "wyzie",        "substudio_wyzie"),
    ]),
    ("[COLOR cyan]● Gemini AI[/COLOR]", [
        ("Wyzie Service",            "gemini",       "wyzie_gemini"),
        ("SubStudio",                "gemini",       "substudio_gemini"),
    ]),
    ("[COLOR tomato]● RPDB[/COLOR]", [
        ("POV",                      "rpdb",         "pov_rpdb"),
    ]),
]
# =====================================================================

# ====== SKIN INFO ====================================================
SKIN_INFO = {
    "skin_fentastic": {"addon_id": "skin.fentastic"},
    "skin_nimbus":    {"addon_id": "skin.nimbus"},
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


# ====== SYNC HIDDEN ==================================================
def _sync_keys_to_settings():
    pairs = [
        ("key_omdb",               OMDB_KEY),
        ("key_mdblist",            MDBLIST_KEY),
        ("key_subdl",              SUBDL_KEY),
        ("key_subsource",          SUBSOURCE_KEY),
        ("key_rpdb",               RPDB_KEY),
        ("key_wyzie",              WYZIE_KEY),
        ("key_orion",              ORION_KEY),
        ("key_sootio",             SOOTIO_TOKEN),
        ("key_opensubs_user",      OPENSUBS_USER),
        ("key_opensubs_pass",      OPENSUBS_PASS),
        ("key_gemini_1",           GEMINI_KEY_1),
        ("key_gemini_2",           GEMINI_KEY_2),
        ("key_gemini_3",           GEMINI_KEY_3),
        ("key_aio_midnight_uuid",  AIOSTREAMS_MIDNIGHT_UUID),
        ("key_aio_stremio_uuid",   AIOSTREAMS_STREMIO_UUID),
        ("key_aio_password",       AIOSTREAMS_PASSWORD),
        ("key_mediafusion_secret", MEDIAFUSION_MIDNIGHT_SECRET),
    ]
    for sid, val in pairs:
        try:
            ADDON.setSetting(sid, val)
        except Exception:
            pass


def _notify(msg, icon=xbmcgui.NOTIFICATION_INFO, ms=3000):
    xbmcgui.Dialog().notification("setapikeys", msg, icon, ms)


def _clear_luc_cache():
    try:
        xbmcgui.Window(10000).clearProperty("luc_kodi_settings")
    except Exception as e:
        xbmc.log("[setapikeys] No se pudo limpiar caché luc_kodi: %s" % e, xbmc.LOGWARNING)


# ====== ESCRITURA ====================================================
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
                errors.append("Escritura fallida en '%s'" % k)
        except Exception as e:
            errors.append("Error en '%s': %s" % (k, e))
    return ok, errors


def _save_to_addon_multi(target_addon_id, kv_dict):
    ok = False
    errors = []
    try:
        target = xbmcaddon.Addon(id=target_addon_id)
    except Exception as e:
        errors.append("No se pudo abrir el addon: %s" % e)
        return False, errors
    setter = getattr(target, "setSettingString", None) or target.setSetting
    getter = getattr(target, "getSettingString", None) or target.getSetting
    for k, v in kv_dict.items():
        try:
            setter(k, v)
            if getter(k) == v:
                ok = True
            else:
                errors.append("Escritura fallida en '%s'" % k)
        except Exception as e:
            errors.append("Error en '%s': %s" % (k, e))
    return ok, errors


def _save_to_luc_mdblist(target_addon_id, keys, value):
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
                errors.append("Escritura fallida en '%s'" % setting_id)
        except Exception as e:
            errors.append("Error en '%s': %s" % (setting_id, e))
    if ok:
        _clear_luc_cache()
    return ok, errors


def _save_to_fenlight(target_addon_id, setting_id, value):
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
            prop = xbmcgui.Window(10000).getProperty("fenlight.%s" % setting_id)
            if prop == value:
                ok = True
            else:
                errors.append("Escritura fallida en fenlight.%s" % setting_id)
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


# ====== ESTADO =======================================================
def _is_active(target_key):
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
            for k, expected_v in payload.items():
                if k.startswith("provider."):
                    continue
                if len(expected_v) <= 1:
                    continue
                try:
                    if getter(k) != expected_v:
                        return False
                except Exception:
                    return False
            return True

        if kind == "gemini":
            try:
                target = xbmcaddon.Addon(id=addon_id)
            except Exception:
                return False
            getter = getattr(target, "getSettingString", None) or target.getSetting
            first_slot = next(iter(payload))
            try:
                return bool(getter(first_slot))
            except Exception:
                return False

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


# ====== GUARDAR ======================================================
def save(provider, target_key):
    if target_key not in TARGETS:
        _notify("Destino desconocido: %s" % target_key, xbmcgui.NOTIFICATION_ERROR)
        return

    kind, addon_id, payload = TARGETS[target_key]

    if kind == "luc_provider":
        ok, errors = _save_to_luc_provider(addon_id, payload)

    elif kind == "gemini":
        ok, errors = _save_to_addon_multi(addon_id, payload)

    elif target_key == "umbrella_opensubs":
        ok, errors = _save_to_addon_multi(addon_id, {
            "opensubsusername": OPENSUBS_USER,
            "opensubspassword": OPENSUBS_PASS,
        })

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


# ====== MENÚ =========================================================
def _build_item_label(label, provider, target_key):
    installed     = _addon_is_installed(target_key)
    active        = _is_active(target_key)
    current       = _skin_is_current(target_key)
    badge_current = " [COLOR deepskyblue](actual)[/COLOR]" if current else ""
    if not installed:
        badge_state = " [COLOR dimgray]no instalado[/COLOR]"
    elif active:
        badge_state = " [COLOR mediumspringgreen]● activo[/COLOR]"
    else:
        badge_state = " [COLOR red]● inactivo[/COLOR]"
    return "%s%s%s" % (label, badge_current, badge_state)


def _show_category(cat_label, items):
    while True:
        sub_labels = []
        sub_data   = []
        for label, provider, target_key in items:
            sub_labels.append(_build_item_label(label, provider, target_key))
            sub_data.append((provider, target_key))
        sub_labels.append("[COLOR dimgray]← Volver[/COLOR]")
        idx = xbmcgui.Dialog().select(cat_label, sub_labels)
        if idx == -1 or idx == len(sub_data):
            return
        provider, target_key = sub_data[idx]
        save(provider, target_key)


def _show_main_menu():
    while True:
        cat_labels = []
        for cat_label, items in MENU:
            installed = sum(1 for _, _, tk in items if _addon_is_installed(tk))
            activos   = sum(1 for _, _, tk in items if _is_active(tk))
            cat_labels.append("%s  [COLOR dimgray]%d/%d activos[/COLOR]" % (cat_label, activos, installed))
        cat_labels.append("[COLOR dimgray]Salir[/COLOR]")
        idx = xbmcgui.Dialog().select("setapikeys", cat_labels)
        if idx == -1 or idx == len(MENU):
            return
        cat_label, items = MENU[idx]
        _show_category(cat_label, items)


# ====== ENTRADA ======================================================
def parse_params(arg):
    if not arg:
        return {}
    if arg.startswith("?"):
        arg = arg[1:]
    parts = urllib.parse.parse_qs(arg, keep_blank_values=True)
    return {k: v[0] for k, v in parts.items()}


def main():
    _sync_keys_to_settings()
    params = parse_params(sys.argv[1] if len(sys.argv) > 1 else "")
    action = params.get("action")
    if action == "save":
        save(params.get("provider", ""), params.get("target", ""))
        return
    _show_main_menu()


if __name__ == "__main__":
    main()
