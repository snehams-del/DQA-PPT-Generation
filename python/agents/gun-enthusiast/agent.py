import datetime
import requests
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from .prompt import agent_instruction

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}

def get_gun_catalog():
    """
    指定されたURLにHTTP GETリクエストを送信し、
    200 OKが返ってきた場合にレスポンスボディを文字列で返します。

    Args:
        url (str): 取得したいURL。

    Returns:
        str: レスポンスボディの文字列。
        None: リクエストが成功しなかった場合（200 OK以外、またはエラー）。
    """
    try:
        response = requests.get("https://storage.googleapis.com/gun-enthusiast-assets/GUN_CATALOG.md")

        # ステータスコードが200 OKであることを確認
        if response.status_code == 200:
            return response.text  # レスポンスボディを文字列で返す
        else:
            print(f"エラー: ステータスコード {response.status_code} が返されました。")
            return None
    except requests.exceptions.RequestException as e:
        print(f"リクエスト中にエラーが発生しました: {e}")
        return None

root_agent = Agent(
    model="gemini-2.0-flash",
    name="gun_enthusiast",
    instruction=agent_instruction,
    tools=[get_current_time,get_gun_catalog],
)
