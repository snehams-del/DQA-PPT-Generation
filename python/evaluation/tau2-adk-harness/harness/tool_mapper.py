# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def map_airline_arguments(adk_tool_name: str, adk_args: dict) -> dict:
    """
    Translates arguments from ADK tool format to Tau2 tool format for the airline
    domain. For our current example, the argument names match, so we can just return
    them. If they were different, you would add mapping logic here. e.g., if adk_args
    had 'from_city', you'd map it to 'origin'.
    """
    return adk_args


# --- The Central Mapping Configuration ---
# To support a new domain, add a new entry here.
DOMAIN_CONFIGS = {
    "airline": {
        "tool_map": {
            # ADK Tool Name : Tau2 Tool Name
            "adk_find_flights": "search_direct_flight",
            "adk_get_booking_details": "get_reservation_details",
            "adk_cancel_reservation": "cancel_reservation",
            "adk_transfer_to_human": "transfer_to_human_agents",
            "adk_book_reservation": "book_reservation",
            "adk_calculate": "calculate",
            "adk_get_user_details": "get_user_details",
            "adk_list_all_airports": "list_all_airports",
            "adk_search_onestop_flight": "search_onestop_flight",
            "adk_send_certificate": "send_certificate",
            "adk_update_reservation_baggages": "update_reservation_baggages",
            "adk_update_reservation_flights": "update_reservation_flights",
            "adk_update_reservation_passengers": "update_reservation_passengers",
            "adk_get_flight_status": "get_flight_status",
        },
        "arg_mapper": map_airline_arguments,
    },
    # "telecom": { ... mappings for telecom would go here ... }
}


def get_tool_mapping(domain: str) -> dict:
    """
    Returns the tool and argument mapping configuration for a given domain.
    """
    if domain in DOMAIN_CONFIGS:
        return DOMAIN_CONFIGS[domain]
    else:
        raise ValueError(
            f"No tool mapping is configured for domain: '{domain}'. Please add it"
            f"to harness/tool_mapper.py."
        )
