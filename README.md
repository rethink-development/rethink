# Rethink

**Rethink** is a comprehensive stock trading application that integrates with multiple brokerage APIs, allowing users to execute trades, check holdings, and manage credentials securely through a user-friendly graphical interface built with Tkinter.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
- [Configuration](#configuration)
- [Guides](#guides)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Multi-Broker Integration**: Supports brokers like Fidelity, Robinhood, Schwab, Vanguard, Webull, Wells Fargo, and more.
- **Secure Credential Management**: Encrypts and securely stores brokerage credentials.
- **Graphical User Interface**: Intuitive GUI for executing trades and checking holdings.
- **Command Builder**: Easily create and execute complex trading commands.
- **Holdings Checker**: View your current holdings across all connected brokers.
- **Logging**: Detailed logs for actions and errors, with optional Discord notifications.

## Prerequisites

- **Python 3.8+**: Ensure you have Python installed. You can download it from [python.org](https://www.python.org/downloads/).
- **Virtual Environment**: Recommended to use a virtual environment to manage dependencies.

## Installation

1. **Clone the Repository**

   ```bash
   git clone git@github.com:rethink-development/rethink.git
   cd rethink
   ```

## Setup

1. **Run the Setup Script**

   The setup script installs necessary environment configurations and dependencies.

   ```bash
   python3 setup.py
   ```

2. **Activate the Virtual Environment**

   After running `setup.py`, activate the virtual environment as instructed. For example:

   ```bash
   source autorsa-venv/bin/activate
   ```

   *Example Output:*

   ```
   To activate the virtual environment, run:
   source autorsa-venv/bin/activate
   ```

3. **Run the Application**

   ```bash
   python3 main.py
   ```

## Usage

Launch the application using the following command:

```bash
python3 main.py
```

Once the GUI is up, you can:

- **Command Builder Tab**: Create and execute buy/sell orders across selected brokers.
- **Holdings Checker Tab**: View your current holdings from all connected brokerage accounts.
- **Settings Tab**: Manage your brokerage credentials securely.

## Configuration

## Guides
   The directory contains the following guides:

   - `guides/RobinhoodSetup.md`
   - `guides/SchwabSetup.md`


### Managing Credentials

1. **Navigate to the Settings Tab** in the application.
2. **Select Brokerage**: Choose the brokerage you want to add credentials for.
3. **Enter Credentials**: Input your brokerage-specific credentials. Password fields are masked for security.
4. **Add Credential**: Click the "Add Credential" button to save. Credentials are encrypted and stored in `credentials.json`.
5. **View Credentials**: Saved credentials are listed with masked sensitive information.
6. **Delete Credential**: Select a credential from the list and click "Delete Selected" to remove it.

### Supported Brokers

The application supports multiple brokers. Ensure your brokerage is listed in the `BROKER_CONFIG` within the configuration files.

## Security

- **Encryption**: Credentials are encrypted using Fernet symmetric encryption. The encryption key is stored in `secret.key`.
  
  - **Important**: Keep `secret.key` secure. Without it, encrypted credentials cannot be decrypted.
  
- **Credentials Storage**: Encrypted credentials are stored in `credentials.json`.
  
- **Best Practices**:
  
  - Do not share `secret.key` or `credentials.json` with unauthorized individuals.
  - (roadmap item) Consider using environment variables or secure storage solutions for enhanced security.
  
## Troubleshooting

- **Missing `secret.key`**: If the application fails to find `secret.key`, it will generate one. Ensure you keep this file secure.
  
- **Decryption Errors**: If credentials fail to decrypt, ensure `secret.key` is present and correct. Any corruption or loss of this key will prevent access to stored credentials.
  
- **Dependency Issues**: Ensure all dependencies are installed correctly within the virtual environment. Re-run `pip install -r requirements.txt` if necessary.
  
- **GUI Not Launching**: Check for any errors in the terminal output. Ensure that Tkinter is properly installed and compatible with your Python version.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**
2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add some feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

Please ensure that your code adheres to the project's coding standards and includes relevant tests.

## Acknowledgements

Special thanks to the following resources and libraries that made this project possible:

- [Tkinter](https://docs.python.org/3/library/tkinter.html) - For the graphical user interface.
- [Fernet](https://cryptography.io/en/latest/fernet/) - For encryption and secure credential management.
- [auto-rsa](https://github.com/NelsonDane/auto-rsa)

## References

- [Official Python Documentation](https://docs.python.org/3/)
- [Cryptography Documentation](https://cryptography.io/en/latest/)
- [Requests Documentation](https://docs.python-requests.org/en/latest/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [Auto-RSA GitHub Repository](https://github.com/NelsonDane/auto-rsa)

## License

This project is licensed under the [MIT License](LICENSE).

---

*For any issues or feature requests, please open an [issue](https://github.com/rethink-development/rethink/issues) on GitHub.*
