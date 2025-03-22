import asyncio

async def send_notification(message: str):
    """
    Simulates sending a notification asynchronously.

    Args:
        message (str): The notification message to send.
    """
    print(f"Notification sent: {message}")
    # Simulate an asynchronous operation (e.g., sending an email, push notification, etc.)
    await asyncio.sleep(1)  # Simulate a 1-second delay