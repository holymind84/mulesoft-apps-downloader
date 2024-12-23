import requests
import json
import os
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

class MulesoftDownloader:
    def __init__(self):
        self._load_config()
        self._setup_base_urls()
        self.session = requests.Session()
        self.download_dir = "downloads"
        self._setup_session()
        self._setup_download_dir()

    def _load_config(self) -> None:
        """Load configurations from .env"""
        load_dotenv()
        
        required_vars = [
            'ANYPOINT_CLIENT_ID',
            'ANYPOINT_CLIENT_SECRET',
            'ANYPOINT_ORG_ID',
            'ANYPOINT_ENV_ID'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise KeyError(f"Missing environment variables: {', '.join(missing_vars)}")

        self.enable_endpoint_logging = os.getenv('ENABLE_ENDPOINT_LOGGING', 'True').lower() == 'true'
        self.control_plane = os.getenv('ANYPOINT_CONTROL_PLANE', 'us').lower()
        
        valid_control_planes = ['us', 'eu1', 'gov']
        if self.control_plane not in valid_control_planes:
            raise ValueError(f"ANYPOINT_CONTROL_PLANE must be one of: {', '.join(valid_control_planes)}")
            
        self.config = {
            'client_id': os.getenv('ANYPOINT_CLIENT_ID'),
            'client_secret': os.getenv('ANYPOINT_CLIENT_SECRET'),
            'organization_id': os.getenv('ANYPOINT_ORG_ID'),
            'environment_id': os.getenv('ANYPOINT_ENV_ID')
        }

    def _setup_base_urls(self) -> None:
        """Setup base URLs based on control plane"""
        # Map control planes to their domains
        control_plane_domains = {
            'us': 'anypoint.mulesoft.com',
            'eu1': 'eu1.anypoint.mulesoft.com',
            'gov': 'gov.anypoint.mulesoft.com'
        }
        
        base_domain = control_plane_domains[self.control_plane]
            
        self.auth_url = f"https://{base_domain}/accounts/api/v2/oauth2/token"
        self.base_url = f"https://{base_domain}/cloudhub/api"
        
        if self.enable_endpoint_logging:
            print(f"\nUsing control plane: {self.control_plane}")
            print(f"Base URL: {self.base_url}")

    def _log_endpoint(self, message: str) -> None:
        """Utility to log endpoints only if enabled"""
        if self.enable_endpoint_logging:
            print(message)

    def _setup_session(self) -> None:
        """Configure HTTP session with credentials and required headers"""
        self._log_endpoint(f"\nCalling authentication endpoint: {self.auth_url}")
        
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": self.config['client_id'],
            "client_secret": self.config['client_secret']
        }

        try:
            response = requests.post(self.auth_url, data=auth_data)
            response.raise_for_status()
            access_token = response.json()["access_token"]
            self.session.headers.update({
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "x-anypnt-env-id": self.config['environment_id'],
                "x-anypnt-org-id": self.config['organization_id']
            })
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error during authentication: {e}")

    def _setup_download_dir(self) -> None:
        """Create download directory if it doesn't exist"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.download_dir = f"downloads_{timestamp}"
        os.makedirs(self.download_dir, exist_ok=True)

    def get_applications(self) -> list:
        """Retrieve the list of applications"""
        url = f"{self.base_url}/applications"
        self._log_endpoint(f"\nCalling applications list endpoint: {url}")
        
        if self.enable_endpoint_logging:
            print("Headers used:")
            print(f"x-anypnt-env-id: {self.config['environment_id']}")
            print(f"x-anypnt-org-id: {self.config['organization_id']}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error retrieving applications: {e}")

    def get_application_info(self, app_name: str) -> Dict:
        """Retrieve detailed information for a single application"""
        url = f"{self.base_url}/organizations/{self.config['organization_id']}/environments/{self.config['environment_id']}/applications/{app_name}"
        self._log_endpoint(f"\nCalling application info endpoint: {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error retrieving information for {app_name}: {e}")

    def download_application(self, app_name: str, filename: str) -> Optional[str]:
        """Download the JAR file for the application"""
        url = f"{self.base_url}/organizations/{self.config['organization_id']}/environments/{self.config['environment_id']}/applications/{app_name}/download/{filename}"
        self._log_endpoint(f"\nCalling application download endpoint: {url}")
        
        # Create specific directory for the application
        app_dir = os.path.join(self.download_dir, app_name)
        os.makedirs(app_dir, exist_ok=True)
        
        output_path = os.path.join(app_dir, filename)

        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return output_path
        except requests.exceptions.RequestException as e:
            print(f"Error downloading application {app_name}: {e}")
            return None

    def process_all_applications(self) -> None:
        """Process all applications: retrieve info and download JARs"""
        print("Starting applications download process...")
        
        try:
            applications = self.get_applications()
            total_apps = len(applications)
            print(f"\nFound {total_apps} applications to process")
            
            # Save applications JSON to root
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"applications_list_{timestamp}.json"
            json_path = os.path.join(self.download_dir, json_filename)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(applications, f, indent=2)
            print(f"Saved applications JSON to: {json_path}")

            for index, app in enumerate(applications, 1):
                app_name = app.get('domain')
                if not app_name:
                    continue

                print(f"\nProcessing application {index} of {total_apps}: {app_name}")
                
                try:
                    app_info = self.get_application_info(app_name)
                    filename = app_info.get('filename')
                    
                    if not filename:
                        print(f"Filename not found for {app_name}, skipping")
                        print("Received JSON:", json.dumps(app_info, indent=2))
                        continue

                    print(f"Downloading file: {filename}")
                    output_path = self.download_application(app_name, filename)
                    
                    if output_path:
                        print(f"Download completed: {output_path}")
                    else:
                        print(f"Download failed for {app_name}")

                except Exception as e:
                    print(f"Error processing {app_name}: {e}")
                    continue

        except Exception as e:
            print(f"Error during process: {e}")

def main():
    try:
        downloader = MulesoftDownloader()
        downloader.process_all_applications()
        print("\nProcess completed successfully!")
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    main()