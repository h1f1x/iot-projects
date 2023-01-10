import click

from sim2070iot import SIM2070


@click.command()
@click.option("--msg", prompt="Nachricht")
@click.option("--number", prompt="telefonnummer", help="SMS Ziel.")
def hello(msg, number):
    sim = SIM2070()
    sim.sendSMS(number=number, text=msg)


if __name__ == "__main__":
    hello()
