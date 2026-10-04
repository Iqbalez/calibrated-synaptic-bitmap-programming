"""Generate independent labelled examples of the specified digital circuit."""
import argparse, csv, hashlib, json
from pathlib import Path
import numpy as np
import physics

def dump(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=32)
    parser.add_argument('--seed', type=int, default=202610041)
    parser.add_argument('--output', type=Path, default=Path('generated_examples'))
    args=parser.parse_args()
    if not 1<=args.count<=100000 or args.seed<0:
        raise ValueError('positive bounded count and nonnegative example seed required')
    if args.output.exists():
        raise ValueError('use a new output directory')
    # Stored integer drives are authoritative, avoiding float recomputation.
    physics.DRIVE_LOOKUP=json.loads((Path(__file__).parent/'drive_lookup.json').read_bytes())
    rng=np.random.default_rng(args.seed)
    def fresh_entropy():
        return int.from_bytes(rng.bytes(16), 'big')
    features=[]; labels=[]
    for _ in range(args.count):
        chip_seed, teacher_seed, key=fresh_entropy(), fresh_entropy(), fresh_entropy()
        known, raster, voltage, goal, word, params, _chip=physics.sample(chip_seed, teacher_seed)
        ident='example_'+hashlib.blake2b(key.to_bytes(16,'big'),digest_size=12).hexdigest()
        features.append(dict(case_id=ident,known_chip=dump(known),calibration_spikes=dump(raster),
                             calibration_voltage=dump(voltage),goal=dump(goal)))
        labels.append(dict(case_id=ident,parameters=dump(params),program=dump(dict(commands=word))))
    if len({r['case_id'] for r in features})!=args.count:
        raise RuntimeError('example ID collision')
    args.output.mkdir(parents=True)
    for name, rows in [('train.csv',features),('train_labels.csv',labels)]:
        with (args.output/name).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps(dict(examples=args.count,output=str(args.output))))

if __name__=='__main__':
    main()
