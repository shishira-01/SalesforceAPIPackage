
from typing import Dict, Any
import httpx
from httpx import HTTPStatusError, AsyncClient
from datetime import datetime, timedelta
import logging
from ..enums.auth_type import AuthType
logger = logging.getLogger(__name__)

class SalesforceConnection:
    def __init__(self, auth_type: AuthType,  auth_config: Dict[str, Any]):
        self.auth_type = auth_type
        self.auth_config = auth_config
        self.domain = auth_config.get('domain', 'login.salesforce.com')
        self.api_version = auth_config.get('api_version', 'v59.0')
        self.timeout = auth_config.get('timeout', 30)
        self.max_retries = auth_config.get('max_retries', 3)
        self.session_id = None
        self.instance_url = None
        self.client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30
            ),
            timeout=httpx.Timeout(
                timeout=self.timeout,
                connect=5.0,
                read=10.0,
                write=10.0
            ),
            http2=True,  # Enable HTTP/2 for better performance
            follow_redirects=True
        )

    async def _ensure_client_connection(self):
        if self.client.is_closed() or self.client is None:
            self.client = httpx.AsyncClient(
                limits=httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=100,
                    keepalive_expiry=30
                ),
                timeout=httpx.Timeout(
                    timeout=self.timeout,
                    connect=5.0,
                    read=10.0,
                    write=10.0
                ),
                http2=True,  # Enable HTTP/2 for better performance
                follow_redirects=True
            )



    async def authenticate(self):
        logger.info("AuthType: {}".format(self.auth_type))
        if self.auth_type == AuthType.PASSWORD:
            logger.info("Authenticating with password...")
            await self.authenticate_with_password()
        elif self.auth_type == AuthType.JWT:
            logger.info("Authenticating with JWT...")
            await self.authenticate_with_jwt()
        elif self.auth_type == AuthType.OAUTH:
            logger.info("Authenticating with OAuth...")
            await self.authenticate_with_oauth()
        else:
            raise ValueError(f"Unsupported auth type: {self.auth_type}")

    async def authenticate_with_password(self):
        await self._ensure_client_connection()
        
        auth_type = AuthType(self.auth_config.get('auth_type', 'password'))
        
        if auth_type == AuthType.PASSWORD:
            return await self._authenticate_with_password()
        elif auth_type == AuthType.OAUTH:
            return await self._authenticate_with_oauth()
        elif auth_type == AuthType.JWT:
            return await self._authenticate_with_jwt()
        else:
            raise ValueError(f"Unsupported auth type: {auth_type}")
    
    async def _authenticate_with_password(self) -> Dict[str, Any]:
        """Async username-password authentication."""
        auth_url = f"https://{self.domain}/services/Soap/u/{self.api_version}"
        
        body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:partner.soap.sforce.com">
            <soapenv:Body>
                <urn:login>
                    <urn:username>{self.auth_config['username']}</urn:username>
                    <urn:password>{self.auth_config['password']}{self.auth_config.get('security_token', '')}</urn:password>
                </urn:login>
            </soapenv:Body>
        </soapenv:Envelope>"""
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'login'
        }
        
        try:
            response = await self.client.post(auth_url, content=body, headers=headers)
            response.raise_for_status()
            
            # Parse SOAP response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            
            session_id = root.find('.//{urn:partner.soap.sforce.com}sessionId')
            instance_url = root.find('.//{urn:partner.soap.sforce.com}serverUrl')
            
            if session_id is not None and instance_url is not None:
                self.session_id = session_id.text
                self.instance_url = instance_url.text.split('/services')[0]
                self.token_expires_at = datetime.now() + timedelta(hours=2)
                
                logger.info(f"Successfully authenticated to Salesforce: {self.instance_url}")
                return {
                    'session_id': self.session_id,
                    'instance_url': self.instance_url,
                    'success': True
                }
            else:
                raise Exception("Failed to extract session info")
                
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise Exception(f"Authentication failed: {str(e)}")

    async def authenticate_with_jwt(self):
        #later we will build this 
        pass

    async def authenticate_with_oauth(self):
        auth_url = f"https://{self.domain}/services/oauth2/token"
        logger.info("Authenticating with OAuth...")
        query_params = {
            "grant_type":"password",
            "client_id": self.auth_config["client_id"],
            "client_secret": self.auth_config["client_secret"],
            "username": self.auth_config["username"],
            "password": self.auth_config["password"]
        }
        
        try:
            response = await self.client.post(auth_url, params=query_params)
            response.raise_for_status()
            data = response.json()
            self.session_id = data["access_token"]
            self.instance_url = data["instance_url"]
            self.token_expires_at = datetime.now() + timedelta(hours=2)
            
            logger.info(f"Successfully authenticated to Salesforce: {self.instance_url}")
            return {
                'session_id': self.session_id,
                'instance_url': self.instance_url,
                'success': True
            }
        except HTTPStatusError as e:
            raise Exception(f"Failed to authenticate with OAuth: {e}")

    async def close(self):
        if not self.client.is_closed():
            await self.client.aclose()






