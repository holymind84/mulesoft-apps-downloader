# mulesoft-apps-downloader

A Python script to download all applications from Mulesoft Anypoint Platform.

## Features

- Downloads all applications from a specified environment
- Supports both US and EU1 control planes
- Organizes downloads in timestamped directories
- Saves applications list as JSON
- Progress tracking during downloads

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/holymind84/mulesoft-apps-downloader.git
cd mulesoft-apps-downloader
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and set your Anypoint Platform credentials:
```properties
ANYPOINT_CLIENT_ID=your_client_id
ANYPOINT_CLIENT_SECRET=your_client_secret
ANYPOINT_ORG_ID=your_organization_id
ANYPOINT_ENV_ID=your_environment_id

# Optional configurations
ANYPOINT_CONTROL_PLANE=us  # Available options: us, eu1, gov
ENABLE_ENDPOINT_LOGGING=True  # Set to False to disable endpoint logging
```

## Usage

Run the script:
```bash
python mulesoft_downloader.py
```

The script will:
1. Create a timestamped directory for downloads
2. Save the full applications list as JSON
3. Create a subdirectory for each application
4. Download each application's JAR file
5. Show progress during the download process

## Output Structure

```
downloads_YYYYMMDD_HHMMSS/
├── applications_list_YYYYMMDD_HHMMSS.json
├── app1_name/
│   └── app1.jar
├── app2_name/
│   └── app2.jar
└── ...
```

## Error Handling

The script includes error handling for:
- Missing environment variables
- Invalid control plane settings
- API connection issues
- Download failures

Each error is logged with appropriate context for debugging.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Donations

If you find this project helpful and want to support its continued development:

[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/SBernardini84)

Your support helps:
- 🚀 Maintain and improve the project
- 💡 Develop new features
- 🐛 Provide faster bug fixes
- 📚 Improve documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.