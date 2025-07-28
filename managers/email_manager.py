import os
import httpx
import logging

logger = logging.getLogger(__name__)

class EmailManager:
    @staticmethod
    async def send_motivational_email(user_id: int, to_email: str, message: str, greeting: str = "Hey,", salutation: str = "Good morning!"):
        full_message = f"{greeting}\n\n{message}\n\n{salutation}"
        try:
            logger.info(f"Attempting to send email for user {user_id} to {to_email}")
            mailgun_api_key = os.getenv("MAILGUN_API_KEY")
            mailgun_domain = os.getenv("MAILGUN_DOMAIN")

            if not mailgun_api_key or not mailgun_domain:
                raise Exception("Mailgun API key or domain not configured.")

            # For testing purposes, print the full message instead of sending it
            logger.info(f"--- Simulating Email Send for user {user_id} ---")
            logger.info(f"To: {to_email}")
            logger.info(f"Subject: Your daily motivational message")
            logger.info(f"Body:\n{full_message}")
            logger.info(f"-----------------------------")

            # Uncomment the following lines to send the actual email
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
                    auth=("api", mailgun_api_key),
                    data={
                        "from": f"Jurn AI <help@{mailgun_domain}>",
                        "to": [to_email],
                        "subject": "Your daily motivational message",
                        "text": full_message
                    }
                )

            if response.status_code == 200:
                logger.info(f"Email sent to {to_email} for user {user_id}")
            else:
                logger.error(f"Failed to send email to {to_email} for user {user_id}: {response.text}")

        except Exception as e:
            logger.error(f"Error sending email to {to_email} for user {user_id}: {e}")