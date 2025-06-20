from typing import List, Dict, Union, Optional, Any
import re
import json
import os
import base64
from pathlib import Path
from urllib.parse import urlparse
import requests

from sendlayer.base import BaseClient
from sendlayer.exceptions import SendLayerError, SendLayerAPIError, SendLayerAuthenticationError, SendLayerValidationError

class Emails:
    """Client for sending emails through SendLayer."""

    def __init__(self, client: BaseClient):
        self.client = client
    
    def _validate_email(self, email: str) -> bool:
        """Validate email address format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _read_attachment(self, file_path: str) -> str:
        """Read a file and encode it in base64."""

        path_obj = Path(file_path)
        
        # Check if file exists and is readable
        if not path_obj.exists():
            raise SendLayerError(f"Attachment file does not exist: {file_path}")
        
        if not path_obj.is_file():
            raise SendLayerError(f"Path is not a file: {file_path}")
            
        if not os.access(path_obj, os.R_OK):
            raise SendLayerError(f"File is not readable: {file_path}")

        # Check if the path is a URL
        parsed = urlparse(file_path)
        is_url = bool(parsed.scheme and parsed.netloc)

        # Get Absolute path
        absolute_path = os.path.abspath(file_path)

        relative_path = os.path.join(os.getcwd(), file_path)  # Relative to current working directory
 


        try:
            if is_url:
                # Handle remote file
                response = requests.get(file_path, timeout=30)
                response.raise_for_status()
                file_content = response.content

           # Try the original path first
            elif os.path.exists(file_path):
                with open(file_path, "rb") as file:
                    file_content = file.read()
            
            
            elif os.path.exists(absolute_path):
                with open(absolute_path, "rb") as file:
                    file_content = file.read()

            elif os.path.exists(relative_path):
                with open(relative_path, "rb") as file:
                    file_content = file.read()
                
            # encoded content to base64
            encoded_content = base64.b64encode(file_content).decode("utf-8")
            return encoded_content
                
        except FileNotFoundError:
            raise SendLayerError(f"Attachment file not found: {file_path}")
        except requests.exceptions.RequestException as e:
            raise SendLayerError('Error fetching remote file: ', str(e))
        except Exception as e:
            raise SendLayerValidationError(f"Error reading attachment: {str(e)}")
        
    
    def _validate_attachment(self, attachment: Dict[str, str]) -> None:
        """Validate attachment format."""
        if not attachment.get("path"):
            raise SendLayerValidationError("Attachment path is required")
        if not attachment.get("type"):
            raise SendLayerValidationError("Attachment type is required")
    
    def send(
        self,
        to: Union[str, Dict[str, Optional[str]], List[Union[str, Dict[str, Optional[str]]]]],
        from_email: str,
        subject: str,
        text: str,
        from_name: Optional[str] = None,
        html: Optional[str] = None,
        cc: Optional[List[Union[str, Dict[str, Optional[str]]]]] = None,
        bcc: Optional[List[Union[str, Dict[str, Optional[str]]]]] = None,
        reply_to: Optional[Union[str, Dict[str, Optional[str]]]] = None,
        attachments: Optional[List[Dict[str, str]]] = None,
        headers: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Send an email through SendLayer."""
        # Validate email addresses
        if not self._validate_email(from_email):
            raise SendLayerValidationError(f"Invalid sender email address: {from_email}")
            
        def validate_recipient(recipient: Union[str, Dict[str, Optional[str]]], recipient_type: str = "recipient") -> Dict[str, Optional[str]]:
            if isinstance(recipient, str):
                if not self._validate_email(recipient):
                    raise SendLayerValidationError(f"Invalid {recipient_type} email address: {recipient}")
                return {"email": recipient}
            if not self._validate_email(recipient['email']):
                raise SendLayerValidationError(f"Invalid {recipient_type} email address: {recipient['email']}")
            return recipient
            
        to_list = [validate_recipient(r, "recipient") for r in (to if isinstance(to, list) else [to])]
                
        if cc:
            cc = [validate_recipient(r, "cc") for r in cc]
                    
        if bcc:
            bcc = [validate_recipient(r, "bcc") for r in bcc]
                    
        if reply_to:
            reply_to = validate_recipient(reply_to, "reply_to")
        
        payload = {
            "From": {"email": from_email, "name": from_name},
            "To": to_list,
            "Subject": subject,
            "ContentType": "HTML" if html else "Text",
            "HTMLContent" if html else "PlainContent": html or text
        }
        
        if cc:
            payload["CC"] = cc
        if bcc:
            payload["BCC"] = bcc
        if reply_to:
            payload["ReplyTo"] = [reply_to]
        if attachments:
            # Validate and transform attachments
            payload["Attachments"] = []
            for attachment in attachments:
                self._validate_attachment(attachment)
                encoded_content = self._read_attachment(attachment["path"])
                
                payload["Attachments"].append({
                    "Content": encoded_content,
                    "Type": attachment["type"],
                    "Filename": os.path.basename(attachment["path"]),
                    "Disposition": "attachment",
                    "ContentId": int(hash(attachment["path"]))  # Using a unique identifier
                })
        if headers:
            payload["Headers"] = headers
        if tags:
            if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
                raise SendLayerValidationError("Tags must be a list of strings.")
            payload["Tags"] = tags
            
        return self.client._make_request("POST", "email", json=payload) 