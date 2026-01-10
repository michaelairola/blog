from __future__ import annotations
import logging
from typing import TYPE_CHECKING

from jinja2static.data import global_data, per_page_data
from jinja2static.data.helpers import get_creation_datetime, get_last_updated_datetime

if TYPE_CHECKING:
    from pathlib import Path
    from jinja2static import Config

logger = logging.getLogger(__name__)


def page_data(config, file_path):
    file_path = config.templates / file_path
    return {
        "file_creation_time": get_creation_datetime(file_path),
        "file_last_updated_time": get_last_updated_datetime(file_path),
    }

@per_page_data
def page(data, config: Config, file_path: Path):
    return {**data, "page": page_data(config, file_path)}
