import requests
from telegram.ext import Updater, MessageHandler, Filters
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
MONDAY_TOKEN = os.environ.get("MONDAY_TOKEN")
BOARD_ID = int(os.environ.get("BOARD_ID"))

def get_task_info(task_name):
    url = "https://api.monday.com/v2"
    headers = {"Authorization": MONDAY_TOKEN}
    query = f"""
    query {{
      items_page_by_column_values(
        board_id: {BOARD_ID},
        columns: [{{column_id: "name", column_values: ["{task_name}"]}}],
        limit: 5
      ) {{
        items {{
          id
          name
          state
          column_values {{
            id
            text
            value
          }}
        }}
      }}
    }}
    """
    response = requests.post(url, json={"query": query}, headers=headers)
    return response.json()



def handle_message(update, context):
    task_name = update.message.text.strip()
    data = get_task_info(task_name)
    print(data)
    items = data.get("data", {}).get("items_page_by_column_values", {}).get("items", [])

    if not items:
        update.message.reply_text(f"❌ No task found with name: {task_name}")
        return

    task = items[0]
    reply = f"✅ Task found:\n\n*Name:* {task['name']}\n*State:* {task['state']}"

    for col in task["column_values"]:
        if col["text"]:
            reply += f"\n*{col['id']}:* {col['text']}"

    update.message.reply_text(reply, parse_mode="Markdown")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("🤖 Bot is running. Send a task name in Telegram to query Monday.")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()



