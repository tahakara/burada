from functools import wraps
from flask import request, Response, redirect, jsonify

from dotenv import load_dotenv
import os
import re

load_dotenv()

class OnBeforeRequestsMiddleware:
    def __init__(self):
        pass  # İstersen ileride config vs verebilirsin

    def handle(self):
        """Handle query parameter-based redirects."""
        redirect_target = request.args.get('redirect')

        if redirect_target and redirect_target.startswith('/'):
            return redirect(redirect_target)

        # İleride başka parametre kontrolleri de buraya eklenebilir
        return None
    
    def redirect(self):
        """
        Redirects the user to a specified target URL if it meets security and validation criteria.
        This method checks for a 'redirect' parameter in the query string and validates the target URL 
        to ensure it is safe and allowed. The validation includes:
        - Ensuring the URL uses HTTPS or upgrading it from HTTP.
        - Verifying the domain or subdomain matches the allowed domains specified in the environment.
        - Preventing path traversal attacks by removing malicious sequences.
        - Ensuring the redirect target is either a valid absolute URL or a relative path.
        Returns:
            A redirect response to the validated target URL if all checks pass, or None if the target 
            URL is invalid or unsafe.
        """
        redirect_target = request.args.get('redirect')
        domain = os.getenv('APP_DOMAIN', 'localhost:5000')

        # Allowed subdomains from environment variable
        allowed_subdomains = os.getenv('ALLOWED_SUBDOMAINS', '').split(',')

        if redirect_target:
            # Ensure the URL starts with http/https and upgrade to https if needed
            if re.match(r'^(http|https)://', redirect_target):
                redirect_target = re.sub(r'^http://', 'https://', redirect_target)
            elif re.match(r'^(www\.)', redirect_target):
                redirect_target = f"https://{redirect_target}"

            # Parse the domain and check for allowed subdomains
            parsed_domain = re.sub(r'^https?://', '', redirect_target).split('/')[0]

            # Check if domain starts with an allowed subdomain
            if any(parsed_domain.startswith(f"{subdomain}.") for subdomain in allowed_subdomains):
                parsed_domain = parsed_domain.split('.', 1)[1]  # Remove subdomain for comparison

            # Ensure the domain matches the environment domain
            if parsed_domain != domain:
                return None  # Not an allowed domain, return None (no redirect)

            # Remove path traversal sequences to prevent malicious redirects
            redirect_target = re.sub(r'(\.\./|/\.{2,}/)', '', redirect_target)

            # Ensure the redirect target is a valid relative path if it's not a full URL
            if not redirect_target.startswith('http') and not redirect_target.startswith('https'):
                if not redirect_target.startswith('/'):
                    redirect_target = f"/{redirect_target}"  # Add leading slash if missing

        # If redirect target is safe and relative (starts with '/'), perform the redirect
        if redirect_target and redirect_target.startswith('/'):
            return redirect(redirect_target)

        return None  # No valid redirect target found, return None