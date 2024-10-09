'''
    rethink
    October 2024

    This is a GUI wrapper, which allows users to 
    execute stock orders and check holdings across multiple brokerages.

'''

import math
import tkinter as tk
from setup import *
# Brokerage configuration
from config import *
import traceback
import threading
from helperAPI import (
    ThreadHandler,
    check_package_versions,
    printAndDiscord,
    stockOrder,
    updater,
)
# Custom API libraries
from retailers.bbaeAPI import *
from retailers.chaseAPI import *
from retailers.dspacAPI import *
from retailers.fennelAPI import *
from retailers.fidelityAPI import *
from retailers.firstradeAPI import *
from helperAPI import (
    ThreadHandler,
    check_package_versions,
    printAndDiscord,
    stockOrder,
    updater,
)
from retailers.publicAPI import *
from retailers.robinhoodAPI import *
from retailers.schwabAPI import *
from retailers.tastyAPI import *
from retailers.tornadoAPI import *
from retailers.tradierAPI import *
from retailers.vanguardAPI import *
from retailers.webullAPI import *
from retailers.wellsfargoAPI import *
from cryptography.fernet import Fernet
from tkinter import ttk, messagebox, scrolledtext
import json
import os


# Account nicknames
def nicknames(broker):
    if broker == "bb":
        return "bbae"
    if broker == "ds":
        return "dspac"
    if broker in ["fid", "fido"]:
        return "fidelity"
    if broker == "ft":
        return "firstrade"
    if broker == "rh":
        return "robinhood"
    if broker == "tasty":
        return "tastytrade"
    if broker == "vg":
        return "vanguard"
    if broker == "wb":
        return "webull"
    if broker == "wf":
        return "wellsfargo"
    return broker

# Load the encryption key
def load_key():
    """
    Loads the Fernet encryption key from the secret.key file.
    """
    key_path = "secret.key"
    if not os.path.exists(key_path):
        raise FileNotFoundError("Encryption key not found. Please generate it first.")
    return open(key_path, "rb").read()

if not os.path.exists("secret.key"):
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    print("Encryption key generated and saved as 'secret.key'. Please keep this file secure.")

cipher_suite = Fernet(load_key())

# Runs the specified function for each broker in the list
# broker name + type of function
def fun_run(orderObj: stockOrder, command, botObj=None, loop=None):
    if command in [("_init", "_holdings"), ("_init", "_transaction")]:
        for broker in orderObj.get_brokers():
            if broker in orderObj.get_notbrokers():
                continue
            broker = nicknames(broker)
            first_command, second_command = command
            try:
                # Initialize broker
                fun_name = broker + first_command
                if broker.lower() == "wellsfargo":
                    # Fidelity requires docker mode argument
                    orderObj.set_logged_in(
                        globals()[fun_name](
                            DOCKER=DOCKER_MODE, botObj=botObj, loop=loop
                        ),
                        broker,
                    )
                elif broker.lower() == "tornado":
                    # Requires docker mode argument and loop
                    orderObj.set_logged_in(
                        globals()[fun_name](DOCKER=DOCKER_MODE, loop=loop),
                        broker,
                    )

                elif broker.lower() in [
                    "bbae",
                    "dspac",
                    "fennel",
                    "firstrade",
                    "public",
                ]:
                    # Requires bot object and loop
                    orderObj.set_logged_in(
                        globals()[fun_name](botObj=botObj, loop=loop), broker
                    )
                elif broker.lower() in ["chase", "fidelity", "vanguard"]:
                    fun_name = broker + "_run"
                    # PLAYWRIGHT_BROKERS have to run all transactions with one function
                    th = ThreadHandler(
                        globals()[fun_name],
                        orderObj=orderObj,
                        command=command,
                        botObj=botObj,
                        loop=loop,
                    )
                    th.start()
                    th.join()
                    _, err = th.get_result()
                    if err is not None:
                        raise Exception(
                            "Error in "
                            + fun_name
                            + ": Function did not complete successfully."
                        )
                else:
                    orderObj.set_logged_in(globals()[fun_name](), broker)

                print()
                if broker.lower() not in ["chase", "fidelity", "vanguard"]:
                    # Verify broker is logged in
                    orderObj.order_validate(preLogin=False)
                    logged_in_broker = orderObj.get_logged_in(broker)
                    if logged_in_broker is None:
                        print(f"Error: {broker} not logged in, skipping...")
                        continue
                    # Get holdings or complete transaction
                    if second_command == "_holdings":
                        fun_name = broker + second_command
                        globals()[fun_name](logged_in_broker, loop)
                    elif second_command == "_transaction":
                        fun_name = broker + second_command
                        globals()[fun_name](
                            logged_in_broker,
                            orderObj,
                            loop,
                        )
                        printAndDiscord(
                            f"All {broker.capitalize()} transactions complete",
                            loop,
                        )
            except Exception as ex:
                print(traceback.format_exc())
                print(f"Error in {fun_name} with {broker}: {ex}")
                print(orderObj)
            print()
        printAndDiscord("All commands complete in all brokers", loop)
    else:
        print(f"Error: {command} is not a valid command")


# Parse input arguments and update the order object
def argParser(args: list) -> stockOrder:
    args = [x.lower() for x in args]
    # Initialize order object
    orderObj = stockOrder()
    # If first argument is holdings, set holdings to true
    if args[0] == "holdings":
        orderObj.set_holdings(True)
        # Next argument is brokers
        if args[1] == "all":
            orderObj.set_brokers(SUPPORTED_BROKERS)
        elif args[1] == "day1":
            orderObj.set_brokers(DAY1_BROKERS)
        elif args[1] == "most":
            orderObj.set_brokers(
                list(filter(lambda x: x != "vanguard", SUPPORTED_BROKERS))
            )
        elif args[1] == "fast":
            orderObj.set_brokers(DAY1_BROKERS + ["robinhood"])
        else:
            for broker in args[1].split(","):
                orderObj.set_brokers(nicknames(broker))
        # If next argument is not, set not broker
        if len(args) > 3 and args[2] == "not":
            for broker in args[3].split(","):
                if nicknames(broker) in SUPPORTED_BROKERS:
                    orderObj.set_notbrokers(nicknames(broker))
        return orderObj
    # Otherwise: action, amount, stock, broker, (optional) not broker, (optional) dry
    orderObj.set_action(args[0])
    orderObj.set_amount(args[1])
    for stock in args[2].split(","):
        orderObj.set_stock(stock)
    # Next argument is a broker, set broker
    if args[3] == "all":
        orderObj.set_brokers(SUPPORTED_BROKERS)
    elif args[3] == "day1":
        orderObj.set_brokers(DAY1_BROKERS)
    elif args[3] == "most":
        orderObj.set_brokers(list(filter(lambda x: x != "vanguard", SUPPORTED_BROKERS)))
    elif args[3] == "fast":
        orderObj.set_brokers(DAY1_BROKERS + ["robinhood"])
    else:
        for broker in args[3].split(","):
            if nicknames(broker) in SUPPORTED_BROKERS:
                orderObj.set_brokers(nicknames(broker))
    # If next argument is not, set not broker
    if len(args) > 4 and args[4] == "not":
        for broker in args[5].split(","):
            if nicknames(broker) in SUPPORTED_BROKERS:
                orderObj.set_notbrokers(nicknames(broker))
    # If next argument is false, set dry to false
    if args[-1] == "false":
        orderObj.set_dry(False)
    # Validate order object
    orderObj.order_validate(preLogin=True)
    return orderObj


# Account nicknames
def nicknames(broker):
    broker = broker.lower()
    nickname_map = {
        "bb": "bbae",
        "ds": "dspac",
        "fid": "fidelity",
        "fido": "fidelity",
        "ft": "firstrade",
        "rh": "robinhood",
        "tasty": "tastytrade",
        "vg": "vanguard",
        "wb": "webull",
        "wf": "wellsfargo",
    }
    return nickname_map.get(broker, broker)

# Function to handle executing stock orders
def execute_stock_order(order_obj, bot_obj=None, loop=None, log_callback=None):
    try:
        fun_run(order_obj, ("_init", "_transaction"), botObj=bot_obj, loop=loop)
        if log_callback:
            log_callback("All stock transactions executed successfully.")
    except Exception as e:
        error_message = f"Error executing stock orders: {e}"
        if log_callback:
            log_callback(error_message)
        print(traceback.format_exc())

# Function to handle checking holdings
def execute_holdings_check(order_obj, bot_obj=None, loop=None, log_callback=None):
    try:
        fun_run(order_obj, ("_init", "_holdings"), botObj=bot_obj, loop=loop)
        if log_callback:
            log_callback("Holdings check executed successfully.")
    except Exception as e:
        error_message = f"Error checking holdings: {e}"
        if log_callback:
            log_callback(error_message)
        print(traceback.format_exc())

class StockTradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("rethink")
        self.root.geometry("1200x700")  # Adjust size as needed

        # Initialize encryption
        self.initialize_encryption()

        # Create a notebook (tabbed interface)
        self.tab_control = ttk.Notebook(root)

        # Create tabs
        self.create_command_builder_tab()
        self.create_holdings_checker_tab()
        self.create_settings_tab()

        self.tab_control.pack(expand=1, fill='both')

    def initialize_encryption(self):
        """
        Initializes the encryption mechanism by loading the key.
        If the key does not exist, generates it and notifies the user.
        """
        key_path = "secret.key"
        if not os.path.exists(key_path):
            try:
                key = Fernet.generate_key()
                with open(key_path, "wb") as key_file:
                    key_file.write(key)
                messagebox.showinfo(
                    "Encryption Key Generated",
                    "An encryption key has been generated and saved as 'secret.key'.\n"
                    "Please keep this file secure. Without it, encrypted credentials cannot be decrypted."
                )
            except Exception as e:
                messagebox.showerror("Key Generation Error", f"Failed to generate encryption key: {e}")
                self.root.destroy()
                return
        try:
            with open(key_path, "rb") as key_file:
                self.cipher_suite = Fernet(key_file.read())
        except Exception as e:
            messagebox.showerror("Key Loading Error", f"Failed to load encryption key: {e}")
            self.root.destroy()

        # Initialize credentials
        self.credentials_file = "credentials.json"
        self.credentials = self.load_credentials()

    def encrypt_credentials(self, creds_str):
        """
        Encrypts a credentials string.
        """
        return self.cipher_suite.encrypt(creds_str.encode()).decode()

    def decrypt_credentials(self, encrypted_creds_str):
        """
        Decrypts an encrypted credentials string.
        """
        try:
            return self.cipher_suite.decrypt(encrypted_creds_str.encode()).decode()
        except Exception as e:
            self.log_settings(f"Decryption failed: {e}")
            return "DecryptionError"

    def load_credentials(self):
        """
        Loads and decrypts credentials from the credentials.json file.
        """
        credentials = {}
        if os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, 'r') as file:
                    data = json.load(file)
                    for broker, encrypted_creds in data.items():
                        decrypted_creds = self.decrypt_credentials(encrypted_creds)
                        if decrypted_creds != "DecryptionError":
                            credentials[broker] = decrypted_creds
            except json.JSONDecodeError as e:
                self.log_settings(f"JSON Decode Error: {e}")
            except Exception as e:
                self.log_settings(f"Error loading credentials: {e}")
        return credentials

    def save_credentials(self):
        """
        Encrypts and saves credentials to the credentials.json file.
        """
        data = {}
        for broker, creds in self.credentials.items():
            encrypted_creds = self.encrypt_credentials(creds)
            data[broker] = encrypted_creds
        try:
            with open(self.credentials_file, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            self.log_settings(f"Error saving credentials: {e}")

    def parse_creds(self, creds_str, broker):
        """
        Parses the credentials string into a dictionary and masks password fields.
        """
        creds = {}
        config = BROKER_CONFIG.get(broker, {})
      
        # Split the creds string based on the delimiter
        for pair in creds_str.split(':'):
            if '@' in pair and '.' in pair:
                creds['email'] = pair.strip()
            
            else:
                creds['password'] = '****'  # Mask the password
        return creds

    def populate_credentials(self):
        """
        Populates the Listbox with existing credentials, masking sensitive fields.
        """
        self.credentials_list.delete(0, tk.END)
        for broker, creds in self.credentials.items():
            masked_creds = self.parse_creds(creds, broker)
            # Reconstruct the masked creds string
            masked_creds_str = ", ".join(f"{k}={v}" for k, v in masked_creds.items())
            display_text = f"{broker.capitalize()}: {masked_creds_str}"
            self.credentials_list.insert(tk.END, display_text)

    def create_command_builder_tab(self):
        """
        Creates the Command Builder tab in the GUI.
        """
        command_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(command_tab, text='Command Builder')

        # Create a frame for inputs with labels on top
        inputs_frame = ttk.Frame(command_tab, padding=10)
        inputs_frame.pack(fill='x', expand=True)

        # Define the structure: list of tuples (Label Text, Widget)
        fields = [
            ("Action", "combobox", ["buy", "sell"], "buy"),
            ("Amount", "entry", None, ""),
            ("Tickers", "entry", None, ""),
            ("Accounts", "combobox", ["all", "fidelity", "robinhood", "schwab", "vanguard", "day1", "most", "fast"], "all"),
            ("Dry Run", "combobox", ["True", "False"], "True")
        ]

        self.command_vars = {}
        for idx, (label_text, widget_type, options, default) in enumerate(fields):
            # Create Label
            label = ttk.Label(inputs_frame, text=label_text)
            label.grid(row=0, column=idx, padx=10, pady=5, sticky='N')

            # Create Widget
            if widget_type == "combobox":
                var = tk.StringVar()
                combobox = ttk.Combobox(inputs_frame, textvariable=var, state="readonly", values=options)
                combobox.current(options.index(default))
                combobox.grid(row=1, column=idx, padx=10, pady=5, sticky='EW')
                self.command_vars[label_text.lower().replace(" ", "_")] = var
            elif widget_type == "entry":
                entry = ttk.Entry(inputs_frame)
                entry.grid(row=1, column=idx, padx=10, pady=5, sticky='EW')
                self.command_vars[label_text.lower().replace(" ", "_")] = entry

        # Configure grid weights for responsiveness
        for idx in range(len(fields)):
            inputs_frame.columnconfigure(idx, weight=1)

        # Execute Button
        execute_button = ttk.Button(command_tab, text="Execute Command", command=self.execute_command)
        execute_button.pack(pady=10)

        # Log Area
        log_label = ttk.Label(command_tab, text="Log:")
        log_label.pack(anchor='w', padx=10)

        self.log_area = scrolledtext.ScrolledText(command_tab, height=15, state='disabled', wrap='word')
        self.log_area.pack(fill='both', expand=True, padx=10, pady=5)

    def execute_command(self):
        """
        Handles the execution of stock orders based on user input.
        """
        action = self.command_vars['action'].get()
        amount = self.command_vars['amount'].get()
        tickers = self.command_vars['tickers'].get()
        accounts = self.command_vars['accounts'].get()
        dry = self.command_vars['dry_run'].get()

        # Validate inputs
        if not amount.isdigit():
            self.log("Error: Amount must be an integer.")
            messagebox.showerror("Input Error", "Amount must be an integer.")
            return
        if not tickers:
            self.log("Error: At least one ticker is required.")
            messagebox.showerror("Input Error", "At least one ticker is required.")
            return
        if not accounts:
            self.log("Error: At least one account must be specified.")
            messagebox.showerror("Input Error", "At least one account must be specified.")
            return

        # Create a stockOrder object
        order_obj = stockOrder()
        order_obj.set_action(action)
        order_obj.set_amount(amount)
        for stock in tickers.split(","):
            order_obj.set_stock(stock.strip())

        # Set brokers based on accounts selection
        if accounts == "all":
            order_obj.set_brokers(SUPPORTED_BROKERS)
        elif accounts == "day1":
            order_obj.set_brokers(DAY1_BROKERS)
        elif accounts == "most":
            order_obj.set_brokers([broker for broker in SUPPORTED_BROKERS if broker != "vanguard"])
        elif accounts == "fast":
            order_obj.set_brokers(DAY1_BROKERS + ["robinhood"])
        else:
            selected_brokers = [nicknames(broker) for broker in accounts.split(",") if nicknames(broker) in SUPPORTED_BROKERS]
            order_obj.set_brokers(selected_brokers)

        # Handle 'not' exclusion if applicable (You can add an input for exclusions if needed)
        # For simplicity, assuming no exclusions from GUI. If needed, add another input field.

        # Set dry run
        order_obj.set_dry(dry.lower() == "true")

        # Validate order object
        order_obj.order_validate(preLogin=True)

        # Start the execution in a separate thread to prevent GUI freezing
        threading.Thread(target=self.run_order, args=(order_obj,)).start()

    def run_order(self, order_obj):
        """
        Executes the stock order and logs the outcome.
        """
        self.log("Starting stock order execution...")
        try:
            fun_run(order_obj, ("_init", "_transaction"), botObj=None, loop=None)
            self.log("Stock order execution completed successfully.")
        except Exception as e:
            error_message = f"Error executing stock orders: {e}"
            self.log(error_message)
            print(traceback.format_exc())

    def log(self, message):
        """
        Logs messages to the Command Builder tab.
        """
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.configure(state='disabled')
        self.log_area.see(tk.END)  # Auto-scroll to the bottom

    def create_holdings_checker_tab(self):
        """
        Creates the Holdings Checker tab in the GUI.
        """
        holdings_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(holdings_tab, text='Holdings Checker')

        # Create a frame for inputs with labels on top
        inputs_frame = ttk.Frame(holdings_tab, padding=10)
        inputs_frame.pack(fill='x', expand=True)

        # Define the structure: list of tuples (Label Text, Widget)
        fields = [
            ("Accounts", "combobox", ["all", "fidelity", "robinhood", "schwab", "vanguard", "day1", "most", "fast"], "all")
        ]

        self.holdings_vars = {}
        for idx, (label_text, widget_type, options, default) in enumerate(fields):
            # Create Label
            label = ttk.Label(inputs_frame, text=label_text)
            label.grid(row=0, column=idx, padx=10, pady=5, sticky='N')

            # Create Widget
            if widget_type == "combobox":
                var = tk.StringVar()
                combobox = ttk.Combobox(inputs_frame, textvariable=var, state="readonly", values=options)
                combobox.current(options.index(default))
                combobox.grid(row=1, column=idx, padx=10, pady=5, sticky='EW')
                self.holdings_vars[label_text.lower().replace(" ", "_")] = var

        # Configure grid weights for responsiveness
        for idx in range(len(fields)):
            inputs_frame.columnconfigure(idx, weight=1)

        # Check Holdings Button
        check_button = ttk.Button(holdings_tab, text="Check Holdings", command=self.check_holdings)
        check_button.pack(pady=10)

        # Log Area
        log_label = ttk.Label(holdings_tab, text="Log:")
        log_label.pack(anchor='w', padx=10)

        self.holdings_log_area = scrolledtext.ScrolledText(holdings_tab, height=15, state='disabled', wrap='word')
        self.holdings_log_area.pack(fill='both', expand=True, padx=10, pady=5)

    def check_holdings(self):
        """
        Handles the holdings check based on user input.
        """
        accounts = self.holdings_vars['accounts'].get()
        if not accounts:
            self.log_holdings("Error: At least one account must be specified.")
            messagebox.showerror("Input Error", "At least one account must be specified.")
            return

        # Create a stockOrder object
        order_obj = stockOrder()
        order_obj.set_holdings(True)

        # Set brokers based on accounts selection
        if accounts == "all":
            order_obj.set_brokers(SUPPORTED_BROKERS)
        elif accounts == "day1":
            order_obj.set_brokers(DAY1_BROKERS)
        elif accounts == "most":
            order_obj.set_brokers([broker for broker in SUPPORTED_BROKERS if broker != "vanguard"])
        elif accounts == "fast":
            order_obj.set_brokers(DAY1_BROKERS + ["robinhood"])
        else:
            selected_brokers = [nicknames(broker) for broker in accounts.split(",") if nicknames(broker) in SUPPORTED_BROKERS]
            order_obj.set_brokers(selected_brokers)

        # Handle 'not' exclusion if applicable (You can add an input for exclusions if needed)
        # For simplicity, assuming no exclusions from GUI. If needed, add another input field.

        # Validate order object
        order_obj.order_validate(preLogin=True)

        # Start the holdings check in a separate thread to prevent GUI freezing
        threading.Thread(target=self.run_holdings_check, args=(order_obj,)).start()

    def run_holdings_check(self, order_obj):
        """
        Executes the holdings check and logs the outcome.
        """
        self.log_holdings("Starting holdings check...")
        try:
            fun_run(order_obj, ("_init", "_holdings"), botObj=None, loop=None)
            self.log_holdings("Holdings check completed successfully.")
        except Exception as e:
            error_message = f"Error checking holdings: {e}"
            self.log_holdings(error_message)
            print(traceback.format_exc())

    def log_holdings(self, message):
        """
        Logs messages to the Holdings Checker tab.
        """
        self.holdings_log_area.configure(state='normal')
        self.holdings_log_area.insert(tk.END, message + "\n")
        self.holdings_log_area.configure(state='disabled')
        self.holdings_log_area.see(tk.END)  # Auto-scroll to the bottom

    def create_settings_tab(self):
        """
        Creates the Settings tab in the GUI.
        """
        settings_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(settings_tab, text='Settings')

        frame = ttk.Frame(settings_tab, padding=20)
        frame.pack(fill='both', expand=True)

        # Broker Selection
        broker_selection_frame = ttk.Frame(frame)
        broker_selection_frame.pack(fill='x', pady=5)

        broker_label = ttk.Label(broker_selection_frame, text="Select Brokerage:")
        broker_label.pack(side='left', padx=5, pady=5)

        self.selected_broker = tk.StringVar()
        broker_dropdown = ttk.Combobox(broker_selection_frame, textvariable=self.selected_broker, state="readonly")
        broker_dropdown['values'] = list(BROKER_CONFIG.keys())
        broker_dropdown.pack(side='left', padx=5, pady=5)
        broker_dropdown.bind("<<ComboboxSelected>>", self.render_broker_fields)

        # Frame to hold dynamic broker fields
        self.broker_fields_frame = ttk.Frame(frame)
        self.broker_fields_frame.pack(fill='both', expand=True, pady=10)

        # Add Credential Button
        add_button = ttk.Button(frame, text="Add Credential", command=self.add_credential)
        add_button.pack(pady=5)

        # Saved Credentials List
        credentials_label = ttk.Label(frame, text="Saved Credentials:")
        credentials_label.pack(anchor='w', padx=5, pady=5)

        self.credentials_list = tk.Listbox(frame, height=10)
        self.credentials_list.pack(fill='both', expand=True, padx=5, pady=5)
        self.credentials_list.bind('<<ListboxSelect>>', self.on_credentials_select)

        # Delete Credential Button
        delete_button = ttk.Button(frame, text="Delete Selected", command=self.delete_credential)
        delete_button.pack(pady=5)

        # Log Area for Settings
        settings_log_label = ttk.Label(frame, text="Log:")
        settings_log_label.pack(anchor='w', padx=5, pady=5)

        self.settings_log_area = scrolledtext.ScrolledText(frame, height=8, state='disabled', wrap='word')
        self.settings_log_area.pack(fill='both', expand=True, padx=5, pady=5)

        # Load existing credentials
        self.populate_credentials()

    def render_broker_fields(self, event=None):
        """
        Dynamically renders input fields based on the selected brokerage.
        Masks password fields.
        """
        # Clear previous fields
        for widget in self.broker_fields_frame.winfo_children():
            widget.destroy()

        broker = self.selected_broker.get()
        if not broker:
            return

        config = BROKER_CONFIG.get(broker, {})
        fields = config.get("fields", [])

        self.current_broker_fields = {}  # To store references to input widgets

        for idx, field in enumerate(fields):
            label = ttk.Label(self.broker_fields_frame, text=field["label"] + ":")
            label.grid(row=idx, column=0, padx=5, pady=5, sticky='W')

            if field["type"] == "combobox":
                var = tk.StringVar()
                combobox = ttk.Combobox(
                    self.broker_fields_frame,
                    textvariable=var,
                    state="readonly",
                    values=field.get("options", [])
                )
                if "default" in field:
                    try:
                        combobox.current(field["options"].index(field["default"]))
                    except ValueError:
                        pass  # Default value not in options
                combobox.grid(row=idx, column=1, padx=5, pady=5, sticky='EW')
                self.current_broker_fields[field["key"]] = combobox
            elif field["type"] == "entry":
                # Mask the input if the field is a password
                show_char = "*" if "password" in field["key"].lower() else None
                entry = ttk.Entry(self.broker_fields_frame, show=show_char)
                entry.grid(row=idx, column=1, padx=5, pady=5, sticky='EW')
                self.current_broker_fields[field["key"]] = entry

        # Configure grid weights
        self.broker_fields_frame.columnconfigure(1, weight=1)

    def add_credential(self):
        """
        Adds a new credential for the selected brokerage.
        Encrypts and saves the credential.
        """
        broker = self.selected_broker.get()
        if not broker:
            self.log_settings("Error: No brokerage selected.")
            messagebox.showerror("Input Error", "Please select a brokerage.")
            return

        config = BROKER_CONFIG.get(broker, {})
        fields = config.get("fields", [])
        env_format = config.get("env_format", "")
        multiple_accounts = config.get("multiple_accounts", False)

        credentials_data = {}
        for field in fields:
            key = field["key"]
            widget = self.current_broker_fields.get(key)
            if not widget:
                continue
            if field["type"] == "combobox":
                value = widget.get()
            else:
                value = widget.get().strip()
            if not value and not field.get("optional", False):
                self.log_settings(f"Error: {field['label']} is required.")
                messagebox.showerror("Input Error", f"{field['label']} is required.")
                return
            credentials_data[key] = value if value else "NA"

        # Format the env string
        try:
            env_entry = env_format.format(**credentials_data)
        except KeyError as e:
            self.log_settings(f"Error formatting credentials: Missing {e}")
            messagebox.showerror("Formatting Error", f"Missing value for {e}")
            return

        if multiple_accounts:
            # Allow multiple entries separated by commas
            existing_entry = self.credentials.get(broker, "")
            if existing_entry:
                new_entry = existing_entry + "," + env_entry
            else:
                new_entry = env_entry
            self.credentials[broker] = new_entry
        else:
            # Single entry per broker
            self.credentials[broker] = env_entry

        self.save_credentials()
        self.populate_credentials()
        self.log_settings(f"Success: Credentials for {broker} added.")
        messagebox.showinfo("Success", f"Credentials for {broker} added.")

        # Clear input fields
        for widget in self.current_broker_fields.values():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Combobox):
                # Reset to default if needed
                if widget['values']:
                    widget.current(0)

    def populate_credentials(self):
        """
        Populates the Listbox with existing credentials, masking sensitive fields.
        """
        self.credentials_list.delete(0, tk.END)
        for broker, creds in self.credentials.items():
            masked_creds = self.parse_creds(creds, broker)
            # Reconstruct the masked creds string
            masked_creds_str = ", ".join(f"{k}={v}" for k, v in masked_creds.items())
            display_text = f"{broker}: {masked_creds_str}"
            self.credentials_list.insert(tk.END, display_text)

    def delete_credential(self):
        """
        Deletes the selected credential from the storage.
        """
        selected = self.credentials_list.curselection()
        if not selected:
            self.log_settings("Error: No credential selected.")
            messagebox.showerror("Selection Error", "No credential selected.")
            return
        index = selected[0]
        selected_text = self.credentials_list.get(index)
        broker = selected_text.split(":")[0]

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete credentials for {broker}?")
        if confirm:
            if broker in self.credentials:
                del self.credentials[broker]
                self.save_credentials()
                self.populate_credentials()
                self.log_settings(f"Deleted: Credentials for {broker} deleted.")
                messagebox.showinfo("Deleted", f"Credentials for {broker} deleted.")
            else:
                self.log_settings(f"Error: No credentials found for {broker}.")
                messagebox.showerror("Error", f"No credentials found for {broker}.")

    def on_credentials_select(self, event):
        """
        Optional: Implement if you want to show details when a credential is selected.
        Currently does nothing.
        """
        pass

    def log_settings(self, message):
        """
        Logs messages to the Settings tab.
        """
        self.settings_log_area.configure(state='normal')
        self.settings_log_area.insert(tk.END, message + "\n")
        self.settings_log_area.configure(state='disabled')
        self.settings_log_area.see(tk.END)  # Auto-scroll to the bottom

def fun_run(orderObj: stockOrder, command, botObj=None, loop=None):
    """
    Executes the specified function for each broker in the list based on the command.
    """
    if command in [("_init", "_holdings"), ("_init", "_transaction")]:
        for broker in orderObj.get_brokers():
            if broker in orderObj.get_notbrokers():
                continue
            broker = nicknames(broker)
            first_command, second_command = command
            try:
                # Initialize broker
                fun_name = broker + first_command
                if broker.lower() == "wellsfargo":
                    # Wells Fargo requires docker mode argument
                    orderObj.set_logged_in(
                        globals()[fun_name](
                            DOCKER=DOCKER_MODE, botObj=botObj, loop=loop
                        ),
                        broker,
                    )
                elif broker.lower() == "tornado":
                    # Tornado requires docker mode argument and loop
                    orderObj.set_logged_in(
                        globals()[fun_name](DOCKER=DOCKER_MODE, loop=loop),
                        broker,
                    )

                elif broker.lower() in [
                    "bbae",
                    "dspac",
                    "fennel",
                    "firstrade",
                    "public",
                ]:
                    # Brokers requiring bot object and loop
                    orderObj.set_logged_in(
                        globals()[fun_name](botObj=botObj, loop=loop), broker
                    )
                elif broker.lower() in ["chase", "fidelity", "vanguard"]:
                    fun_name = broker + "_run"
                    # PLAYWRIGHT_BROKERS have to run all transactions with one function
                    th = ThreadHandler(
                        globals()[fun_name],
                        orderObj=orderObj,
                        command=command,
                        botObj=botObj,
                        loop=loop,
                    )
                    th.start()
                    th.join()
                    _, err = th.get_result()
                    if err is not None:
                        raise Exception(
                            "Error in "
                            + fun_name
                            + ": Function did not complete successfully."
                        )
                else:
                    orderObj.set_logged_in(globals()[fun_name](), broker)

                print()
                if broker.lower() not in ["chase", "fidelity", "vanguard"]:
                    # Verify broker is logged in
                    orderObj.order_validate(preLogin=False)
                    logged_in_broker = orderObj.get_logged_in(broker)
                    if logged_in_broker is None:
                        print(f"Error: {broker} not logged in, skipping...")
                        continue
                    # Get holdings or complete transaction
                    if second_command == "_holdings":
                        fun_name = broker + second_command
                        globals()[fun_name](logged_in_broker, loop)
                    elif second_command == "_transaction":
                        fun_name = broker + second_command
                        globals()[fun_name](
                            logged_in_broker,
                            orderObj,
                            loop,
                        )
                        printAndDiscord(
                            f"All {broker.capitalize()} transactions complete",
                            loop,
                        )
            except Exception as ex:
                print(traceback.format_exc())
                print(f"Error in {fun_name} with {broker}: {ex}")
                print(orderObj)
            print()
        printAndDiscord("All commands complete in all brokers", loop)
    else:
        print(f"Error: {command} is not a valid command")

# Parse input arguments and update the order object
def argParser(args: list) -> stockOrder:
    args = [x.lower() for x in args]
    # Initialize order object
    orderObj = stockOrder()
    # If first argument is holdings, set holdings to true
    if args[0] == "holdings":
        orderObj.set_holdings(True)
        # Next argument is brokers
        if args[1] == "all":
            orderObj.set_brokers(SUPPORTED_BROKERS)
        elif args[1] == "day1":
            orderObj.set_brokers(DAY1_BROKERS)
        elif args[1] == "most":
            orderObj.set_brokers(
                list(filter(lambda x: x != "vanguard", SUPPORTED_BROKERS))
            )
        elif args[1] == "fast":
            orderObj.set_brokers(DAY1_BROKERS + ["robinhood"])
        else:
            for broker in args[1].split(","):
                orderObj.set_brokers(nicknames(broker))
        # If next argument is not, set not broker
        if len(args) > 3 and args[2] == "not":
            for broker in args[3].split(","):
                if nicknames(broker) in SUPPORTED_BROKERS:
                    orderObj.set_notbrokers(nicknames(broker))
        return orderObj
    # Otherwise: action, amount, stock, broker, (optional) not broker, (optional) dry
    orderObj.set_action(args[0])
    orderObj.set_amount(args[1])
    for stock in args[2].split(","):
        orderObj.set_stock(stock)
    # Next argument is a broker, set broker
    if args[3] == "all":
        orderObj.set_brokers(SUPPORTED_BROKERS)
    elif args[3] == "day1":
        orderObj.set_brokers(DAY1_BROKERS)
    elif args[3] == "most":
        orderObj.set_brokers(list(filter(lambda x: x != "vanguard", SUPPORTED_BROKERS)))
    elif args[3] == "fast":
        orderObj.set_brokers(DAY1_BROKERS + ["robinhood"])
    else:
        for broker in args[3].split(","):
            if nicknames(broker) in SUPPORTED_BROKERS:
                orderObj.set_brokers(nicknames(broker))
    # If next argument is not, set not broker
    if len(args) > 4 and args[4] == "not":
        for broker in args[5].split(","):
            if nicknames(broker) in SUPPORTED_BROKERS:
                orderObj.set_notbrokers(nicknames(broker))
    # If next argument is false, set dry to false
    if args[-1] == "false":
        orderObj.set_dry(False)
    # Validate order object
    orderObj.order_validate(preLogin=True)
    return orderObj

'''
    Loading screen for the app

'''
class LoadingScreen:
    def __init__(self, parent, message="Setting up the application..."):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Rethink")
        self.window.geometry("300x200")
        self.window.resizable(False, False)
        self.window.grab_set()  # Make the loading window modal

        # Set the window's background color to match the lambda symbol
        self.window.configure(bg="black")

        # Center the loading window
        self.center_window(self.window, 300, 200)

        # Create a canvas to draw the lambda symbol with a transparent background
        self.canvas = tk.Canvas(self.window, width=100, height=100, bg="black", highlightthickness=0)
        self.canvas.pack(pady=20)

        # Draw the lambda symbol (λ) using text
        self.lambda_text = self.canvas.create_text(50, 50, text="λ", font=("Helvetica", 48), fill="white")

        # Initialize rotation angle
        self.angle = 0

        # Message Label
        self.message_label = ttk.Label(self.window, text=message, background="orange", foreground="white")
        self.message_label.pack(pady=10)

        # Start the animation
        self.animate()

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def animate(self):
        # Simple rotation animation by rotating the canvas
        # Note: Tkinter doesn't support direct rotation of text, so we'll simulate it by rotating the canvas
        self.angle = (self.angle + 10) % 360
        self.canvas.delete("all")
        # Calculate new position with rotation
        radians = math.radians(self.angle)
        x = 50 + 30 * math.cos(radians)
        y = 50 + 30 * math.sin(radians)
        # Redraw lambda symbol
        self.canvas.create_text(x, y, text="λ", font=("Helvetica", 48), fill="orange")
        # Schedule the next frame
        self.window.after(100, self.animate)

    def close(self):
        self.window.destroy()

'''
    End of loading screen for the app
'''
def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window during setup

    # Optional: Apply a modern theme if available
    try:
        import ctypes
        if os.name == "nt":
            # For Windows: Use 'vista' theme
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    # Create and show the loading screen
    loading = LoadingScreen(root)

    # Run the setup in a separate thread
    def run_setup():
        try:
            setup_environment()
            # Once setup is complete, close the loading screen and show the main window
            root.after(0, loading.close)
            root.after(0, root.deiconify)  # Show the main window
          
        except subprocess.CalledProcessError as e:
            root.after(0, loading.close)
            messagebox.showerror("Setup Error", f"An error occurred during setup:\n{e}")
            root.after(0, root.destroy)  # Close the application
        except Exception as e:
            root.after(0, loading.close)
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred:\n{e}")
            root.after(0, root.destroy)  # Close the application

    setup_thread = threading.Thread(target=run_setup)
    setup_thread.start()

    # Initialize the main application (but it's hidden until setup is complete)
    app = StockTradingApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()