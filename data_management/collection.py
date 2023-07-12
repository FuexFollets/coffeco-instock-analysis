from __future__ import annotations

from sp_api.api import Inventories

from data_management.constants import CREDENTIALS


res = Inventories(credentials=CREDENTIALS).get_inventory_summary_marketplace()
