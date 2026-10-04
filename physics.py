"""Original calibrated synaptic programmer, task4.2-pilot, MIT code.

The clocked neuron and immediate plasticity law is unchanged from law1.0.
New task: infer per-cell kinetics from the complete disclosed port-scan raster,
then supply any valid20command programme for the requested persistent bitmap.
This is a specified digital surrogate, not measured hardware.
"""
import numpy as np

TASK_VERSION = '4.2-pilot'
LAW_VERSION = '1.0'
CELLS = 24
COMMANDS = 20
GAIN_VALUES = tuple(range(96,145))


def drive_lookup():
    xy=np.array([(i,j) for i in range(6) for j in range(4)])
    centres=np.array([(x,y) for x in np.linspace(0,5,4) for y in (0,3)])
    profile=np.exp(-np.sum((xy[None]-centres[:,None])**2,axis=2)/(2*1.5**2))
    return np.rint(profile[:,:,None]*np.array(GAIN_VALUES)).astype(np.int64).tolist()


DRIVE_LOOKUP = drive_lookup()


def reconstruct(known_chip,parameters):
    gain=parameters['gain']
    drive=[[DRIVE_LOOKUP[p][j][gain[j]-96] for j in range(24)] for p in range(8)]
    return dict(drive=drive,leak=parameters['leak'][:],threshold=parameters['threshold'][:],
                bias=parameters['bias'][:],sign=known_chip['sign'][:],
                mask=[r[:] for r in known_chip['mask']],bits=[r[:] for r in known_chip['bits']])


def make_chip(seed):
    rng=np.random.default_rng(seed)
    parameters=dict(gain=rng.integers(96,145,24).tolist(),leak=rng.integers(230,247,24).tolist(),
                    threshold=rng.integers(210,281,24).tolist(),bias=rng.integers(4,13,24).tolist())
    sign=np.where(rng.random(24)<.2,-1,1)
    mask=rng.random((24,24))<.25;np.fill_diagonal(mask,False)
    bits=mask&(rng.random((24,24))<.5);bits[mask&(sign[:,None]<0)]=True
    known={k:v.astype(int).tolist() for k,v in dict(sign=sign,mask=mask,bits=bits).items()}
    return known,parameters,reconstruct(known,parameters)


def simulate(chip,commands,return_state=False):
    """Independent scalar, exact original law; record every tick's synchronous spikes."""
    v=[0]*24;adapt=[0]*24;old=[0]*24;bits=[row[:] for row in chip['bits']];raster=[]
    for command in commands:
        if type(command) is not int or not 0<=command<8:
            raise ValueError('ordinary integer command0..7 required')
        for _ in range(2):
            nxt=[];sp=[]
            for j in range(24):
                current=16*sum(old[i]*chip['sign'][i]*bits[i][j] for i in range(24))
                value=v[j]*chip['leak'][j]//256+chip['bias'][j]+chip['drive'][command][j]+current-adapt[j]
                if old[j]:value=0
                fire=int(value>=chip['threshold'][j]);sp.append(fire);nxt.append(0 if fire else value)
            updated=[row[:] for row in bits]
            for i in range(24):
                if chip['sign'][i]<0:continue
                for j in range(24):
                    if chip['mask'][i][j]:
                        if old[i] and sp[j]:updated[i][j]=1
                        elif sp[i] and old[j]:updated[i][j]=0
            adapt=[adapt[j]*240//256+18*sp[j] for j in range(24)]
            v,old,bits=nxt,sp,updated;raster.append(sp[:])
    if return_state:return dict(bits=bits,v=v,adapt=adapt,old=old,spikes=raster)
    return bits


def sample(chip_seed,teacher_seed):
    known,parameters,chip=make_chip(chip_seed)
    word=np.random.default_rng(teacher_seed).integers(0,8,20).tolist()
    # Each complete probe starts from the same initial state, not a preceding probe.
    observed=[simulate(chip,[port]*20,True) for port in range(8)]
    probes=[state['spikes'] for state in observed]
    voltages=[state['v'] for state in observed]
    return known,probes,voltages,simulate(chip,word),word,parameters,chip
