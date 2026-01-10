from __future__ import annotations
import logging
from typing import TYPE_CHECKING

from jinja2static.data import global_data, per_page_data
from jinja2static.data.helpers import get_creation_datetime, get_last_updated_datetime

from . import page_data

if TYPE_CHECKING:
    from pathlib import Path
    from jinja2static import Config

logger = logging.getLogger(__name__)



@global_data
def pages(data, config: Config):
    return {**data, "pages": {page: page_data(config, page) for page in config.pages}}

