'''
    rethink
    october 2024

    This file contains the configration for Danger Mode and Docker Mode. 
    It also contains the global variables and broker configurations.
    
'''



DANGER_MODE = False

# Required for the app to run, DO NOT CHANGE
DOCKER_MODE = False

# Global variables
SUPPORTED_BROKERS = [
    "bbae",
    "chase",
    "dspac",
    "fennel",
    "fidelity",
    "firstrade",
    "public",
    "robinhood",
    "schwab",
    "tastytrade",
    "tornado",
    "tradier",
    "vanguard",
    "webull",
    "wellsfargo",
]
DAY1_BROKERS = [
    "bbae",
    "chase",
    "dspac",
    "fennel",
    "firstrade",
    "public",
    "schwab",
    "tastytrade",
    "tradier",
    "webull",
]

# Define broker configurations
BROKER_CONFIG = {
    "BBAE": {
        "fields": [
            {"label": "Username (Email or Phone)", "key": "BBAE_USERNAME", "type": "entry"},
            {"label": "Password", "key": "BBAE_PASSWORD", "type": "entry"},
        ],
        "env_format": "BBAE={BBAE_USERNAME}:{BBAE_PASSWORD}",
        "multiple_accounts": False,
        "notes": "BBAE_USERNAME can either be email or phone number."
    },
    "Chase": {
        "fields": [
            {"label": "Username", "key": "CHASE_USERNAME", "type": "entry"},
            {"label": "Password", "key": "CHASE_PASSWORD", "type": "entry"},
            {"label": "Cell Phone Last Four", "key": "CELL_PHONE_LAST_FOUR", "type": "entry", "optional": True},
            {"label": "Debug Mode", "key": "DEBUG", "type": "combobox", "options": ["True", "False"], "default": "False"}
        ],
        "env_format": "CHASE={CHASE_USERNAME}:{CHASE_PASSWORD}:{CELL_PHONE_LAST_FOUR}:{DEBUG}",
        "multiple_accounts": False,
        "notes": "Optional fields: CELL_PHONE_LAST_FOUR, DEBUG."
    },
    "DSPAC": {
        "fields": [
            {"label": "Username (Email or Phone)", "key": "DSPAC_USERNAME", "type": "entry"},
            {"label": "Password", "key": "DSPAC_PASSWORD", "type": "entry"},
        ],
        "env_format": "DSPAC={DSPAC_USERNAME}:{DSPAC_PASSWORD}",
        "multiple_accounts": False,
        "notes": "DSPAC_USERNAME can either be email or phone number."
    },
    "Fennel": {
        "fields": [
            {"label": "Email", "key": "FENNEL_EMAIL", "type": "entry"},
        ],
        "env_format": "FENNEL={FENNEL_EMAIL}",
        "multiple_accounts": False,
        "notes": "Fennel accounts don't have passwords."
    },
    "Fidelity": {
        "fields": [
            {"label": "Username", "key": "FIDELITY_USERNAME", "type": "entry"},
            {"label": "Password", "key": "FIDELITY_PASSWORD", "type": "entry"},
        ],
        "env_format": "FIDELITY={FIDELITY_USERNAME}:{FIDELITY_PASSWORD}",
        "multiple_accounts": False,
        "notes": "Uses Selenium for web scraping."
    },
    "Firstrade": {
        "fields": [
            {"label": "Username", "key": "FIRSTRADE_USERNAME", "type": "entry"},
            {"label": "Password", "key": "FIRSTRADE_PASSWORD", "type": "entry"},
            {"label": "OTP (One-Time Password)", "key": "FIRSTRADE_OTP", "type": "entry"},
        ],
        "env_format": "FIRSTRADE={FIRSTRADE_USERNAME}:{FIRSTRADE_PASSWORD}:{FIRSTRADE_OTP}",
        "multiple_accounts": False,
        "notes": "Supports multiple 2FA methods."
    },
    "Public": {
        "fields": [
            {"label": "Username", "key": "PUBLIC_USERNAME", "type": "entry"},
            {"label": "Password", "key": "PUBLIC_PASSWORD", "type": "entry"},
        ],
        "env_format": "PUBLIC_BROKER={PUBLIC_USERNAME}:{PUBLIC_PASSWORD}",
        "multiple_accounts": False,
        "notes": "Use PUBLIC_BROKER due to Windows environment variable conflict."
    },
    "Robinhood": {
        "fields": [
            {"label": "Username", "key": "ROBINHOOD_USERNAME", "type": "entry"},
            {"label": "Password", "key": "ROBINHOOD_PASSWORD", "type": "entry"},
            {"label": "TOTP (Two-Factor Authentication)", "key": "ROBINHOOD_TOTP", "type": "entry", "optional": True},
        ],
        "env_format": "ROBINHOOD={ROBINHOOD_USERNAME}:{ROBINHOOD_PASSWORD}:{ROBINHOOD_TOTP}",
        "multiple_accounts": False,
        "notes": "Use 'NA' if 2FA is not enabled."
    },
    "Schwab": {
        "fields": [
            {"label": "Username", "key": "SCHWAB_USERNAME", "type": "entry"},
            {"label": "Password", "key": "SCHWAB_PASSWORD", "type": "entry"},
            {"label": "TOTP Secret", "key": "SCHWAB_TOTP_SECRET", "type": "entry", "optional": True},
        ],
        "env_format": "SCHWAB={SCHWAB_USERNAME}:{SCHWAB_PASSWORD}:{SCHWAB_TOTP_SECRET}",
        "multiple_accounts": False,
        "notes": "Use 'NA' if 2FA is not enabled."
    },
    "Tornado": {
        "fields": [
            {"label": "Email", "key": "TORNADO_EMAIL", "type": "entry"},
            {"label": "Password", "key": "TORNADO_PASSWORD", "type": "entry"},
        ],
        "env_format": "TORNADO={TORNADO_EMAIL}:{TORNADO_PASSWORD}",
        "multiple_accounts": False,
        "notes": ""
    },
    "Tradier": {
        "fields": [
            {"label": "Access Token", "key": "TRADIER_ACCESS_TOKEN", "type": "entry"},
        ],
        "env_format": "TRADIER={TRADIER_ACCESS_TOKEN}",
        "multiple_accounts": False,
        "notes": "Obtain access token from Tradier API settings."
    },
    "Tastytrade": {
        "fields": [
            {"label": "Username", "key": "TASTYTRADE_USERNAME", "type": "entry"},
            {"label": "Password", "key": "TASTYTRADE_PASSWORD", "type": "entry"},
        ],
        "env_format": "TASTYTRADE={TASTYTRADE_USERNAME}:{TASTYTRADE_PASSWORD}",
        "multiple_accounts": False,
        "notes": ""
    },
    "Webull": {
        "fields": [
            {"label": "Username (Email or Phone)", "key": "WEBULL_USERNAME", "type": "entry"},
            {"label": "Password", "key": "WEBULL_PASSWORD", "type": "entry"},
            {"label": "DID", "key": "WEBULL_DID", "type": "entry"},
            {"label": "Trading PIN", "key": "WEBULL_TRADING_PIN", "type": "entry"},
        ],
        "env_format": "WEBULL={WEBULL_USERNAME}:{WEBULL_PASSWORD}:{WEBULL_DID}:{WEBULL_TRADING_PIN}",
        "multiple_accounts": False,
        "notes": "Username can be email or phone number formatted as +1-XXXXXXXXXX or +86-XXXXXXXXXXX."
    },
    "Vanguard": {
        "fields": [
            {"label": "Username", "key": "VANGUARD_USERNAME", "type": "entry"},
            {"label": "Password", "key": "VANGUARD_PASSWORD", "type": "entry"},
            {"label": "Phone Last Four", "key": "PHONE_LAST_FOUR", "type": "entry"},
            {"label": "Debug Mode", "key": "DEBUG", "type": "combobox", "options": ["True", "False"], "default": "False"},
        ],
        "env_format": "VANGUARD={VANGUARD_USERNAME}:{VANGUARD_PASSWORD}:{PHONE_LAST_FOUR}:{DEBUG}",
        "multiple_accounts": False,
        "notes": "Optional field: DEBUG."
    },
    "Wells Fargo": {
        "fields": [
            {"label": "Username", "key": "WELLSFARGO_USERNAME", "type": "entry"},
            {"label": "Password", "key": "WELLSFARGO_PASSWORD", "type": "entry"},
            {"label": "Phone Last Four", "key": "WELLSFARGO_PHONE_LAST_FOUR", "type": "entry"},
        ],
        "env_format": "WELLSFARGO={WELLSFARGO_USERNAME}:{WELLSFARGO_PASSWORD}:{WELLSFARGO_PHONE_LAST_FOUR}",
        "multiple_accounts": False,
        "notes": ""
    }
}