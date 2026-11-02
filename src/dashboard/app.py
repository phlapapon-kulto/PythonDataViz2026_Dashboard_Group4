"""Build the Dash application."""
from __future__ import annotations

from pathlib import Path

from dash import Dash

from src.dashboard import theme as t
from src.dashboard.callbacks import register_callbacks
from src.dashboard.data_store import DataNotReady, DataStore, load_store
from src.dashboard.layout import build_layout, error_layout
from src.dashboard.state import default_state

ASSETS = Path(__file__).parent / "assets"
TITLE = "ภัยดิจิทัลยุค AI | Digital Threat Dashboard"


def defaults_for(store: DataStore) -> dict:
    window = store.panel[store.panel["in_acsc_window"]]
    return default_state(
        store.news["date"].min().date().isoformat(), store.news["date"].max().date().isoformat(),
        window["week_start"].min().date().isoformat(), window["week_end"].max().date().isoformat(),
    )


def create_app() -> Dash:
    app = Dash(
        __name__, title=TITLE, update_title=None, assets_folder=str(ASSETS), external_stylesheets=[t.FONT_URL],
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )
    app.index_string = app.index_string.replace("<html>", '<html lang="th">')
    try:
        store = load_store()
    except DataNotReady as error:
        app.layout = error_layout(str(error))
        return app
    defaults = defaults_for(store)
    app.layout = build_layout(store, defaults)
    register_callbacks(app, store, defaults)
    return app
