# FILE: sample_adk_agent/my_agent/agent.py

from google.adk.agents import Agent
from typing import List, Dict, Any

# These are the ADK-native tool definitions.
# Their signatures and docstrings are what the ADK agent's LLM will see.
# The code inside these functions will NEVER be executed by the harness.


def adk_find_flights(origin: str, destination: str, date: str) -> List[dict]:
    """
    Searches for available direct flights between an origin and a destination on a
    specific date. Args:
        origin: The three-letter IATA code for the origin airport (e.g., 'SFO').
        destination: The three-letter IATA code for the destination airport (e.g.,
        'JFK'). date: The desired flight date in 'YYYY-MM-DD' format.
    Returns:
        A list of available flights, each represented as a dictionary.
    """
    pass  # The harness executes the real tau2 tool.


def adk_get_booking_details(reservation_id: str) -> dict:
    """
    Retrieves the full details for a specific flight reservation using its ID.
    Args:
        reservation_id: The unique identifier for the reservation (e.g., '4WQ150').
    Returns:
        A dictionary containing the reservation details.
    """
    pass


def adk_cancel_reservation(reservation_id: str) -> dict:
    """
    Cancels an entire flight reservation using its unique ID.
    Args:
        reservation_id: The unique identifier for the reservation to be cancelled.
    Returns:
        A dictionary confirming the cancellation status.
    """
    pass


def adk_transfer_to_human(summary: str) -> dict:
    """
    Transfers the user to a human agent when a request cannot be handled by the
    available tools or policy. Args:
        summary: A brief summary of the user's issue for the human agent.
    Returns:
        A dictionary confirming the transfer.
    """
    pass


def adk_book_reservation(
    user_id: str,
    origin: str,
    destination: str,
    flight_type: str,
    cabin: str,
    flights: List[Dict[str, Any]],
    passengers: List[Dict[str, Any]],
    payment_methods: List[Dict[str, Any]],
    total_baggages: int,
    nonfree_baggages: int,
    insurance: str,
) -> dict:
    """
    Books a flight reservation with all necessary details.
    Args:
        user_id: The ID of the user.
        origin: The origin city IATA code.
        destination: The destination city IATA code.
        flight_type: Type of flight, e.g., 'one_way' or 'round_trip'.
        cabin: The cabin class, e.g., 'economy'.
        flights: List of flight details.
        passengers: List of passenger details.
        payment_methods: List of payment methods to use.
        total_baggages: Total number of bags.
        nonfree_baggages: Number of non-free bags.
        insurance: Whether to include insurance, 'yes' or 'no'.
    Returns:
        A dictionary confirming the new reservation.
    """
    pass


def adk_calculate(expression: str) -> str:
    """
    Calculates the result of a mathematical expression.
    Args:
        expression: The mathematical expression to calculate, e.g., '250 * 3 + 50'.
    Returns:
        The result of the calculation.
    """
    pass


def adk_get_user_details(user_id: str) -> dict:
    """
    Gets the details of a user, including their reservations.
    Args:
        user_id: The user ID.
    Returns:
        A dictionary with user details.
    """
    pass


def adk_list_all_airports() -> List[dict]:
    """
    Returns a list of all available airports.
    Returns:
        A list of airport dictionaries.
    """
    pass


def adk_search_onestop_flight(origin: str, destination: str, date: str) -> List[dict]:
    """
    Searches for one-stop flights between two cities on a specific date.
    Args:
        origin: The origin city airport IATA code.
        destination: The destination city airport IATA code.
        date: The date of the flight in 'YYYY-MM-DD' format.
    Returns:
        A list of flight options, where each option is a pair of flights.
    """
    pass


def adk_send_certificate(user_id: str, amount: int) -> str:
    """
    Sends a certificate of a specified amount to a user.
    Args:
        user_id: The user ID to send the certificate to.
        amount: The amount of the certificate.
    Returns:
        A string confirming the certificate was sent.
    """
    pass


def adk_update_reservation_baggages(
    reservation_id: str, total_baggages: int, nonfree_baggages: int, payment_id: str
) -> dict:
    """
    Updates the baggage information for a reservation.
    Args:
        reservation_id: The ID of the reservation to update.
        total_baggages: The new total number of bags.
        nonfree_baggages: The new number of non-free bags.
        payment_id: The ID of the payment method to use for any charges.
    Returns:
        The updated reservation details.
    """
    pass


def adk_update_reservation_flights(
    reservation_id: str, cabin: str, flights: List[Dict[str, Any]], payment_id: str
) -> dict:
    """
    Updates the flight information for a reservation.
    Args:
        reservation_id: The ID of the reservation to update.
        cabin: The new cabin class for the reservation.
        flights: The new list of flights for the entire reservation.
        payment_id: The ID of the payment method to use for any charges or refunds.
    Returns:
        The updated reservation details.
    """
    pass


def adk_update_reservation_passengers(
    reservation_id: str, passengers: List[Dict[str, Any]]
) -> dict:
    """
    Updates the passenger information for a reservation.
    Args:
        reservation_id: The ID of the reservation to update.
        passengers: The new list of passengers.
    Returns:
        The updated reservation details.
    """
    pass


def adk_get_flight_status(flight_number: str, date: str) -> str:
    """
    Gets the status of a specific flight on a specific date.
    Args:
        flight_number: The flight number.
        date: The date of the flight.
    Returns:
        The status of the flight (e.g., 'on time', 'delayed').
    """
    pass


# This is the agent we will evaluate.
root_agent = Agent(
    name="adk_airline_agent",
    model="gemini-2.5-flash",
    description="An ADK agent for booking, finding, and managing flight reservations.",
    instruction=(
        "You are a task-oriented airline assistant. Your ONLY goal is to use the "
        "provided tools to fulfill the user's request. "
        "You MUST call a tool in your first turn if the user's request contains enough "
        "information to do so. "
        "Analyze the user's request and immediately call the appropriate tool to find, "
        "get details for, or cancel a reservation. "
        "NOTE: If the user wants to cancel you must first check if all criteria for "
        "cancellation are met! "
        "In particular check whether the flight was made within 24 hours. This is "
        "important!"
    ),
    tools=[
        adk_find_flights,
        adk_get_booking_details,
        adk_cancel_reservation,
        adk_transfer_to_human,
        adk_book_reservation,
        adk_calculate,
        adk_get_user_details,
        adk_list_all_airports,
        adk_search_onestop_flight,
        adk_send_certificate,
        adk_update_reservation_baggages,
        adk_update_reservation_flights,
        adk_update_reservation_passengers,
        adk_get_flight_status,
    ],
)
