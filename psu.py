import pyvisa

# Constants
GPIB_ADDRESS = 'GPIB0::5::INSTR'
CHANNEL = 1  # Channel number to measure

def initialize_instrument(address):
    """Establishes a connection to the instrument."""
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource(address)
    instrument.timeout = 5000
    instrument.read_termination = '\n'
    print(f"Connected to: {instrument.query('*IDN?').strip()}")
    return instrument

def read_voltage(instrument, channel):
    """Reads and returns the voltage from the specified channel."""
    response = instrument.query(f"MEASure:VOLTage? (@{channel})")
    voltage = float(response.strip())
    return voltage

def read_current(instrument, channel):
    """Reads and returns the current from the specified channel."""
    response = instrument.query(f"MEASure:CURRent? (@{channel})")
    current = float(response.strip())
    return current

def close_instrument(instrument):
    """Closes the VISA connection."""
    instrument.close()
    print("Instrument connection closed.")

def set_voltage(instrument, channel, voltage):
    """Sets the voltage on the specified channel."""
    instrument.write(f"VOLT {voltage}, (@{channel})")
    print(f"Set voltage to {voltage} V on channel {channel}")

def set_current_limit(instrument, channel, current):
    """Sets the current limit on the specified channel."""
    instrument.write(f"CURR {current}, (@{channel})")
    print(f"Set current limit to {current} A on channel {channel}")

def read_current_limit(instrument, channel):
    """Reads and returns the programmed current limit for the specified channel."""
    response = instrument.query(f"CURR? (@{channel})")
    current_limit = float(response.strip())
    return current_limit

def main():
    """Main program logic."""
    try:
        # Connect to instrument
        inst = initialize_instrument(GPIB_ADDRESS)

        # Set voltage
        set_voltage(inst, CHANNEL, 6.0)  # Set to 5V as an example

        # Set current limit
        set_current_limit(inst, CHANNEL, 1.0)   # Set to 1A current limit

        # Read measurements
        voltage = read_voltage(inst, CHANNEL)
        current = read_current(inst, CHANNEL)

        # Read programmed current limit
        current_limit = read_current_limit(inst, CHANNEL)
        print(f"Channel {CHANNEL} Current Limit: {current_limit:.3f} A")

        # Display results
        print(f"Channel {CHANNEL} Voltage: {voltage:.3f} V")
        print(f"Channel {CHANNEL} Current: {current:.3f} A")

    except pyvisa.VisaIOError as e:
        print(f"VISA IO Error: {e}")
    except Exception as e:
        print(f"General error: {e}")
    finally:
        # Always try to close the connection
        try:
            close_instrument(inst)
        except:
            pass

# Run the program
if __name__ == "__main__":
    main()
