from sim2070iot.sim2070iot import SIM2070


def test_something():
    pass


def test_close_pdp_context():
    """
    You can check with your provide if the PDP context ist closed.
    """
    sim = SIM2070()
    sim.deactivateContext()
