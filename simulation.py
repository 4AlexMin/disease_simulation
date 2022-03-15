import pandas as pd
import random
import wheels
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm

rec_rates = wheels.get_rec_rates()
pthp_prevs = wheels.get_prevalences('pathophysiological_prevalences.xlsx')
tret_prevs = wheels.get_prevalences('treatment_prevalences.xlsx')


#Generate patients' sample
__basepopul = 500
populs = dict()
for k, v in pthp_prevs.items():
    if v['max'] == v['min']:
        popul_rate = v['min']
    else:
        popul_rate = random.uniform(v['min'], v['max'])
    populs[k] = int(popul_rate*__basepopul)


# Generate treatment samples to randomly choose from
# For every patient, the treatment samples are `identical`
__basetret = 200
tret_samples = []
for k, v in tret_prevs.items():
    if v['max'] == v['min']:
        tret_rate = v['min']
    else:
        tret_rate = random.uniform(v['min'], v['max'])
    tret_samples.extend([k for _ in range(int(tret_rate*__basetret))])


def simulation(rec_rates, populs, tret_samples, tretnum=1):

    # patients finding cure
    recs = dict()
    for k, v in populs.items():
        recs[k] = []

        # single patient finding cure
        for _patient in range(v):
            rec = 0    # `rec` stands for whether this patient recovers.
            treatments = set()
            while len(treatments) < tretnum:
                treatments.add(random.choice(tret_samples))
            for tret in treatments:
                if random.random() <= rec_rates.loc[tret, k]:
                    rec = 1
                    break
                else:
                    continue
            recs[k].append(rec)

    popul_recs = dict()
    for k, v in recs.items():
        popul_recs[k] = v.count(1)/len(v)
    return popul_recs

# Run simulations
recs_df = pd.DataFrame(columns=['mechanism', 'treatment_number', 'recovery_rate'])

# Run same simulation `__simulation_rep` times for each `tretnum``
__simulation_rep = 50
print('Simulation Running:')
for tretnum in tqdm(range(1, len(tret_prevs)+1)):
    for rep in range(__simulation_rep):
        popul_recs = simulation(rec_rates, populs, tret_samples, tretnum)
        for pmechanism, rrate in popul_recs.items():
            rowname = str(tretnum)+'_'+str(rep)+'_'+pmechanism[:2]
            recs_df.loc[rowname] = [pmechanism, tretnum, rrate]
recs_df.to_csv('output/results.csv')

    
        


# Plotting figs

# This figure is based on one example of seaborn:
# https://seaborn.pydata.org/examples/horizontal_boxplot.html
sns.set_theme(style="ticks")
f, ax = plt.subplots()
sns.boxplot(x="recovery_rate", y="mechanism", data=recs_df,
            whis=[0, 100], width=.4, palette="vlag")    # Plot the orbital period with horizontal boxes
sns.stripplot(x="recovery_rate", y="mechanism", data=recs_df,
              size=2, color=".3", linewidth=0)    # Add in points to show each observation
ax.xaxis.grid(True)
ax.set(ylabel="pathophysiological mechanism")
sns.despine(trim=True, left=True)
plt.savefig('output/boxplot_formechanisms.svg', bbox_inches='tight')


# See trends under different treatment numbers
g = sns.FacetGrid(recs_df, col="mechanism", hue='treatment_number')
g.map(sns.histplot, "recovery_rate")
g.add_legend()
g.savefig('output/diff_treatnum_formechanisms.svg')
fig = plt.figure()
sns.kdeplot(data=recs_df, x='recovery_rate', hue='treatment_number')
fig.savefig('output/diff_treatnum_combined.svg')
