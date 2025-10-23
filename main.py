import asyncio
from src.connection.salesforce_connection import SalesforceConnection
from src.enums.auth_type import AuthType
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
#TODO: Remove load env in prod
import os
from dotenv import load_dotenv
load_dotenv()
async def main():
    try:
        auth_config = {
        "auth_type": "oauth",
        "domain":"test.salesforce.com",
        "api_version":"v59.0",
        "timeout":30,
        "max_retries":3,
        "username": os.getenv("SALESFORCE_USERNAME").strip(),
        "password": os.getenv("SALESFORCE_PASSWORD").strip(),
        "client_id": os.getenv("SALESFORCE_CLIENT_ID").strip(),
        "client_secret": os.getenv("SALESFORCE_CLIENT_SECRET").strip(),
        "security_token": os.getenv("SALESFORCE_SECURITY_TOKEN").strip()
    }
        logger.info("Authenticating to Salesforce...")
        logger.info("Auth type: {}".format(auth_config["auth_type"]))
        logger.info("Domain: {}".format(auth_config["domain"]))
        logger.info("API version: {}".format(auth_config["api_version"]))
        logger.info("Timeout: {}".format(auth_config["timeout"]))
        logger.info("Max retries: {}".format(auth_config["max_retries"]))
        logger.info("Username: {}".format(auth_config["username"]))
        logger.info("Password: {}".format(auth_config["password"]))
        logger.info("Client ID: {}".format(auth_config["client_id"]))
        logger.info("Client secret: {}".format(auth_config["client_secret"]))
        logger.info("Security token: {}".format(auth_config["security_token"]))
        salesforce_connection = SalesforceConnection(AuthType.OAUTH, auth_config)
        result = await salesforce_connection.authenticate()
        logger.info("Authentication result: {}".format(result))
        
    except Exception as e:
        logger.error("Authentication failed: {}".format(e))

if __name__ == "__main__":
    asyncio.run(main())
