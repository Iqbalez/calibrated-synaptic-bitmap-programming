# Calibrated Synaptic Bitmap Programming

Original source for a synthetic circuit-calibration and program-synthesis benchmark. These are specified digital circuits, not measured hardware or biological records.

A solver receives the initial topology and synaptic bitmap of a 24-cell circuit, complete spike observations from eight reset calibration probes, the stored membrane voltages at the end of those probes, and a requested final bitmap. Four integer coefficients per cell remain fixed but latent. The solver emits any 20 commands from ports 0 through 7 that reach the requested bitmap. Each command lasts two synchronous ticks. Programs are judged by their result, not equality to a teaching word.

This repository currently contains the development specification and 32 labelled training examples. It is not the final challenge release, a claim of platform acceptance, or a measured-device validation. The circuit law and measurement convention are fixed; final qualification and the larger training release are separate work.

## Files

| Path | Content |
| --- | --- |
| `physics.py` | Exact integer dynamics and original circuit sampler |
| `drive_lookup.json` | Authoritative drives indexed by port, cell, and gain minus 96 |
| `generate_examples.py` | Independent reproducible training-example generator |
| `examples/train.csv` | 32 labelled development feature rows |
| `examples/train_labels.csv` | Auxiliary coefficients and one valid program per training row |
| `LICENSE_CODE.txt` | MIT license for original code |
| `LICENSE_DATA.md` | CC0 1.0 dedication for original generated data |
| `requirements.txt` | NumPy dependency |
| `SOURCE_MANIFEST.json` | SHA-256 and byte inventory of the source files |

Feature columns are `case_id`, `known_chip`, `calibration_spikes`, `calibration_voltage`, and `goal`. Training labels join by `case_id` and contain `parameters` and `program`. Matrix entry `[i][j]` means presynaptic cell i to postsynaptic cell j. `known_chip` contains `sign`, `mask`, and initial `bits`. Goal dimensions are 24 by 24.

Coefficients are independently uniform integers: gain 96 through 144, leak 230 through 246, bias 4 through 12, and threshold 210 through 280, with inclusive bounds. Their realized values stay fixed across calibration and programming. The sampler draws signs and connection masks independently of these coefficients. Allowed excitatory bits start with independent probability one half; allowed inhibitory bits start at one and absent bits at zero. Teaching words use an independent draw.

`calibration_spikes` has dimensions 8 by 40 by 24. Probe p applies 20 copies of command p. `[p][t][j]` is the synchronous spike after tick t+1. Each probe and the requested program start from the original bitmap, zero membrane, zero adaptation and zero previous spikes. Plasticity is enabled during calibration.

`calibration_voltage` has dimensions 8 by 24. It records the stored membrane voltage after tick 40 of each probe, including spike reset and refractory overwrite. Values may be negative. A tick-40 spike, or a spike on tick 39 followed by refractory tick 40, leaves stored voltage zero. No extra observation tick or noise is added. The full spike raster remains available.

Voltage uses mathematical floor division, including for negative values. Current uses previous spikes and the previous bitmap. All cells update synchronously, with new plastic bits affecting the following tick. Absent and inhibitory connections retain their initial bits. The executable law in `physics.py` is authoritative. `drive_lookup.json` supplies exact integer drive values, so the example generator binds it before creating circuits.

## Generate independent training examples

```bash
python -m pip install -r requirements.txt
python generate_examples.py --count 32 --seed 202610041 --output generated_examples
```

The example seed generates new examples; it does not reproduce any assessment devices. Generated features and labels use the same schema as the supplied examples. Each target comes from an independent uniform word of 20 commands, which supplies a valid witness. Other valid words are equally acceptable. Circuit identifiers use a separate random stream and convey no teaching-word information.

## Scientific context and scope

[Pfeil et al. (2013)](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2013.00011/full) describes calibration and membrane observations on neuromorphic hardware. [Kaiser, Müller and Schemmel (2026)](https://arxiv.org/html/2602.10763v1) studies amortized neuron-parameter inference from hardware observations. These motivate response-based calibration; they do not validate this exact integer surrogate, noiseless endpoint readout or benchmark timing. Calibration and spike-timing plasticity are established mechanisms. The capability evaluated here is calibration-conditioned finite-word programming of a persistent recurrent bitmap.

No article text, figures, measured traces, third-party datasets or third-party source code are redistributed. Code and generated examples are original benchmark artifacts; dependency packages are installed separately under their own licenses.
