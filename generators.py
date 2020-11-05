from random import SystemRandom

from generator import generalised_feedback_shift_registers as gfsr
from generator import linear_congruential_generators as lcg
from generator import linear_feedback_shift_registers as lfsr
from generator.generator import StaticFileGenerator, StaticSequenceGenerator

available_generators = (
    # Generalised feedback shift registers
    'mt32', 'lcg_randu', 'lfsr_131',
)


def create(generator_id, seed=None):
    if not generator_id:
        raise ValueError("No generator selected")

    if generator_id.startswith('file:'):
        print(generator_id[5:], seed)
        return StaticFileGenerator(generator_id[5:])

    if not seed:
        seed = SystemRandom().getrandbits(128)

    # Generalised feedback shift registers
    if generator_id == 'mt32':
        return gfsr.MersenneTwister32(seed=seed)

    # Linear congruential generators
    elif generator_id == 'lcg_randu':
        return lcg.RanduLinearCongruentialGenerator(seed=seed % (2 ** 31))

    # Linear feedback shift registers
    elif generator_id == 'lfsr_131':
        return lfsr.LinearFeedbackShiftRegister(131, taps=(131, 130, 84, 83),
                                                seed=seed % (2 ** 131))

    else:
        raise ValueError("Invalid generator")


def reseed(generator):
    if not generator:
        raise ValueError("No generator given")

    generator_type = type(generator)

    if generator_type in (StaticFileGenerator, StaticSequenceGenerator):
        return

    seed = SystemRandom().getrandbits(128)

    # Generalised feedback shift registers
    if generator_type is gfsr.MersenneTwister32:
        seed = seed % (2 ** 32)

    # Linear congruential generators
    elif isinstance(generator, lcg.LinearCongruentialGenerator):
        seed = seed % generator.m

    # Linear feedback shift registers
    elif generator_type is lfsr.LinearFeedbackShiftRegister:
        seed = seed % (2 ** generator.length)

    else:
        raise ValueError("Invalid generator")

    generator.seed(seed)

    return seed
