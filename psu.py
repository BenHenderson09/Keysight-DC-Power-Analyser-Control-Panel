import pyvisa

# Constants
GPIB_ADDRESS = 'GPIB0::5::INSTR'

def initialize_instrument(address):
    """Establishes a connection to the instrument."""
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource(address)
    instrument.timeout = 5000
    instrument.read_termination = '\n'
    print(f"Connected to: {instrument.query('*IDN?').strip()}")
    return instrument

def set_voltage(instrument, channel, voltage):
    """Sets the voltage on the specified channel."""
    instrument.write(f"VOLT {voltage}, (@{channel})")

def set_current(instrument, channel, current):
    """Sets the current limit on the specified channel."""
    instrument.write(f"CURR {current}, (@{channel})")

def read_voltage(instrument, channel):
    """Reads and returns the actual output voltage from the specified channel."""
    response = instrument.query(f"MEASure:VOLTage? (@{channel})")
    return float(response.strip())

def read_current(instrument, channel):
    """Reads and returns the actual output current from the specified channel."""
    response = instrument.query(f"MEASure:CURRent? (@{channel})")
    return float(response.strip())

def read_current_limit(instrument, channel):
    """Reads and returns the programmed current limit for the specified channel."""
    response = instrument.query(f"CURR? (@{channel})")
    return float(response.strip())

def prompt_and_set_channel(instrument):
    """Continuously prompts the user to set voltage/current."""
    while True:
        try:
            channel = int(input("Enter channel number: "))
            voltage = float(input("Enter desired voltage (V): "))
            current = float(input("Enter current limit (A): "))

            set_voltage(instrument, channel, voltage)
            set_current(instrument, channel, current)

            measured_v = read_voltage(instrument, channel)
            limit_c = read_current_limit(instrument, channel)

            print(f"\n*** Settings applied to channel {channel}:")
            print(f"  Measured Voltage: {measured_v:.3f} V")
            print(f"  Measured Current Limit: {limit_c:.3f} A\n")

        except ValueError:
            print("Invalid input. Please enter numeric values.\n")
        except pyvisa.VisaIOError as e:
            print(f"VISA IO Error: {e}\n")
        except Exception as e:
            print(f"Unexpected error: {e}\n")

def close_instrument(instrument):
    """Closes the VISA connection."""
    instrument.close()
    print("Instrument connection closed.")

def main():
    """Main program logic."""

    print("--- Ben's CLI for PSU ---")

    try:
        inst = initialize_instrument(GPIB_ADDRESS)
        prompt_and_set_channel(inst)
    except KeyboardInterrupt:
        print("\nExiting on user interrupt.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            close_instrument(inst)
        except:
            pass

if __name__ == "__main__":
    main()
