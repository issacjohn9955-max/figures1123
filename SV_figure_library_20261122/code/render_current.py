"""Render Four Figures-style panels from project result tables."""
import argparse
import json
from pathlib import Path
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import LogNorm
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ENV = ['bio3', 'bio15', 'bio18', 'wind', 'srad']
DISPLAY = ['BIO3', 'BIO15', 'BIO18', 'Wind', 'Solar radiation']
NEW = [
    ('24_origin_world_asia', 'Representative origins across the main cohort', 'world_distribution_map'),
    ('25_partial_rda_ordination', 'Partial RDA ordination and axis tests', 'fig3_rda'),
    ('26_cross_method_summary', 'Cross-method evidence across analysis cohorts', 'fig4_evidence'),
    ('27_paired_statistics', 'Partial-rank and LFMM2 statistics on matched SVs', 'gea_marginal_scatter'),
]


def tsv(path):
    return pd.read_csv(path, sep='\t')


def normalize(run, earlier, geo, out):
    import shutil
    out.mkdir(parents=True, exist_ok=True)
    cohort = run/'results/evidence'
    rda = cohort/'rda'
    groups = tsv(cohort/'groups.tsv')
    groups[['sample', 'n_samples', 'lon', 'lat', *ENV]].to_csv(out/'groups.tsv', sep='\t', index=False)
    keys = ['rda_axis_tests.tsv', 'rda_sample_scores_vegan.csv', 'rda_environment_arrows_vegan.csv',
            'rda_metrics_vegan.tsv', 'rda_summary_vegan.txt']
    for name in keys:
        shutil.copyfile(rda/name, out/name)
    for name in ['evidence_counts.tsv', 'evidence_rows.tsv']:
        shutil.copyfile(earlier/name, out/name)
    partial = tsv(cohort/'association_summary.tsv').query('model == "sv_pc3_geo"')
    lfmm = tsv(cohort/'lfmm/K10/diagnostics.tsv')
    rates = partial[['variable', 'tested', 'significant']].merge(
        lfmm[['variable', 'finite_p', 'significant']], on='variable', validate='one_to_one',
        suffixes=('_rank', '_lfmm'))
    rates.to_csv(out/'environment_counts.tsv', sep='\t', index=False)
    fields = ['sv_id', 'variable', 'rho', 'q', 'lfmm_stat_K10', 'lfmm_q_K10']
    points = pd.read_csv(cohort/'integrated_evidence.tsv.gz', sep='\t', usecols=fields)
    if points.duplicated(['sv_id','variable']).any():
        raise ValueError('Integrated evidence must contain one row per allele and variable.')
    points = points.dropna(subset=['rho', 'q', 'lfmm_stat_K10', 'lfmm_q_K10'])
    points.to_csv(out/'paired_statistics.tsv.gz', sep='\t', index=False)
    shutil.copyfile(geo, out/'world_countries_110m.geojson')


def land(path):
    source = json.loads(path.read_text())
    polygons = []
    for feature in source['features']:
        geom = feature.get('geometry')
        if not geom:
            continue
        vertices = geom['coordinates']
        parts = [vertices] if geom['type'] == 'Polygon' else vertices if geom['type'] == 'MultiPolygon' else []
        polygons.extend(p[0] for p in parts if p)
    return polygons


def origin_map(root, colors):
    groups = tsv(root/'groups.tsv')
    if groups['sample'].duplicated().any() or groups.duplicated(['lon','lat']).any():
        raise ValueError('Each coordinate group must have a unique ID and location.')
    world = land(root/'world_countries_110m.geojson')
    region = (62, 146, -13, 57)
    inside = groups.lon.between(*region[:2]) & groups.lat.between(*region[2:])
    fig, ax = plt.subplots(1, 2, figsize=(9, 4.1), width_ratios=[1.55, 1], layout='constrained')
    for axis, shown, limits, title in zip(
        ax, [groups, groups.loc[inside]], [(-180, 180, -57, 83), region],
        ['A  Global distribution', f'B  Asia detail · {int(inside.sum())} groups'],
    ):
        axis.add_collection(PolyCollection(world, facecolor='#F1F4F6', edgecolor='#BAC5CC', linewidth=.38))
        scatter = axis.scatter(shown.lon, shown.lat, s=12+2.7*shown.n_samples,
                               c=shown.bio3, cmap='viridis', vmin=groups.bio3.min(), vmax=groups.bio3.max(),
                               edgecolor='white', linewidth=.6, zorder=3)
        axis.set(xlim=limits[:2], ylim=limits[2:], title=title, xlabel='Longitude (°)', ylabel='Latitude (°)')
        axis.set_aspect('equal')
    ax[0].add_patch(Rectangle((region[0],region[2]),region[1]-region[0],region[3]-region[2],
                              fill=False, ec=colors[0], lw=.8, zorder=2))
    for size in [5, 20, 50]:
        ax[0].scatter([], [], s=12+2.7*size, fc='none', ec=colors[0], label=str(size))
    ax[0].legend(loc='lower left', title='Individuals per group', ncol=3, frameon=False, fontsize=7)
    fig.colorbar(scatter, ax=ax, shrink=.72, label='BIO3 · isothermality')
    fig.suptitle(f'Representative origins of {groups.n_samples.sum()} individuals in {len(groups)} coordinate groups',
                 weight='bold')
    return fig


def rda_plot(root, colors):
    groups = tsv(root/'groups.tsv')
    axes = tsv(root/'rda_axis_tests.tsv')
    info = tsv(root/'rda_metrics_vegan.tsv').set_index('metric')['value']
    sites = pd.read_csv(root/'rda_sample_scores_vegan.csv').merge(groups, on='sample', validate='one_to_one')
    arrows = pd.read_csv(root/'rda_environment_arrows_vegan.csv').set_index('variable').loc[ENV]
    raw_summary = (root/'rda_summary_vegan.txt').read_text()
    inertia = dict((a,float(v)) for a,v in re.findall(r'^(RDA\d+)\s+\d+\s+([\d.]+)\s',raw_summary,re.M))
    variance = np.array([inertia[a] for a in axes.axis])
    if len(sites) != len(groups) or len(sites) != int(info.samples):
        raise ValueError('The partial RDA positions and cohort table differ.')
    if not np.isclose(variance.sum()/float(int(info.loci)), float(info.constrained_fraction), atol=5e-6):
        raise ValueError('Reported axis inertias do not match the constrained fraction.')
    # All response columns were scaled to unit variance. Validate the reported denominator.
    total = float(re.search(r'^total_inertia:\s+([\d.]+)',raw_summary,re.M)[1])
    if not np.isclose(total,int(info.loci)):
        raise ValueError('Response scaling differs from this partial RDA input contract.')
    percentages = 100*variance/total
    fig, ax = plt.subplots(1, 2, figsize=(8.9, 4.2), width_ratios=[1.4,1], layout='constrained')
    pos = sites[['RDA1','RDA2']].abs().max().to_numpy()
    vectors = arrows[['RDA1','RDA2']].to_numpy()
    endpoints = .73 * np.min(pos / np.abs(vectors).max(axis=0)) * vectors
    ax[0].axhline(0,c='#A9B2BB',lw=.55)
    ax[0].axvline(0,c='#A9B2BB',lw=.55)
    ax[0].scatter(sites.RDA1,sites.RDA2,s=15+2.15*sites.n_samples,c=colors[0],
                  alpha=.76,edgecolor='white',linewidth=.45,zorder=2)
    arrow_labels = [*DISPLAY[:4], 'Solar rad.']
    for label, (x,y) in zip(arrow_labels,endpoints):
        ax[0].annotate('', xy=(x,y), xytext=(0,0),
                       arrowprops={'arrowstyle':'->','color':'#A74431','lw':1.1})
        ax[0].annotate(label, (x,y), xytext=(3 if x>=0 else -3, 3 if y>=0 else -3),
                       textcoords='offset points', ha='left' if x>=0 else 'right',
                       va='bottom' if y>=0 else 'top',fontsize=7,color='#833D32')
    ax[0].set(xlabel=f'RDA1 ({percentages[0]:.2f}% of total inertia)',
              ylabel=f'RDA2 ({percentages[1]:.2f}% of total inertia)',
              title='A  Descriptive ordination · point size scales with group size')
    ax[0].margins(.19)
    ax[1].bar(axes.axis,percentages,color=colors[1],edgecolor=colors[0],linewidth=.5,width=.63)
    for i,(pct,q) in enumerate(zip(percentages,axes.BH_q)):
        ax[1].text(i,pct+.13,f'q={q:.3f}',ha='center',fontsize=7)
    passed=int(axes.eligible_for_screen.astype(str).str.lower().isin(['true','1']).sum())
    ax[1].set(ylim=(0,max(percentages)*1.26),ylabel='Total inertia (%)',title=f'B  Axis tests · {passed} eligible for screening')
    fig.suptitle(f'Partial RDA · {len(sites)} coordinate groups · overall permutation P = {float(info.global_p):.3f}',
                 weight='bold')
    return fig


def evidence_plot(root, colors):
    data=tsv(root/'environment_counts.tsv').set_index('variable').loc[ENV]
    summary=tsv(root/'evidence_counts.tsv')
    hits=tsv(root/'evidence_rows.tsv')
    if list(hits.groupby('cohort').size().reindex(summary.cohort,fill_value=0))!=summary.partial_hits.tolist():
        raise ValueError('Evidence totals and partial-rank hits differ.')
    fig,ax=plt.subplots(2,2,figsize=(9.1,5.45),layout='constrained')
    for a, suffix, color, title in [(ax[0,0],'rank',colors[0],'A  Partial rank · main cohort'),
                                     (ax[0,1],'lfmm',colors[1],'B  Joint LFMM2 K=10 · main cohort')]:
        vals=data[f'significant_{suffix}']
        bars=a.bar(DISPLAY,vals,color=color,width=.62)
        a.bar_label(bars,fontsize=7,padding=2)
        a.set(title=title,ylabel='SV–environment pairs at q < 0.05',ylim=(0,max(vals.max()*1.24,1.32)))
        den=data.tested if suffix=='rank' else data.finite_p
        detail=f'{den.iloc[0]:,} SV alleles tested per environment' if den.nunique()==1 else 'Tested SV alleles vary by environment'
        a.text(.97,.9,detail,ha='right',transform=a.transAxes,fontsize=7.1)
    rda=ax[1,0].bar(summary.cohort,summary.rda_hits,color=colors[2])
    ax[1,0].bar_label(rda,fontsize=7,padding=2)
    ax[1,0].set(title='C  Joint partial RDA',ylabel='SV alleles in eligible-axis tails',
                ylim=(0,max(1.32,summary.rda_hits.max()*1.22)))
    positions=np.arange(len(summary))
    for offset, field, name, c in [(-.16,'both_rda_lfmm','RDA and LFMM2 · at least one environment',colors[1]),
                                   (.16,'strict','Strict SV–environment pairs',colors[0])]:
        bars=ax[1,1].bar(positions+offset,summary[field],width=.32,label=name,color=c)
        ax[1,1].bar_label(bars,fontsize=7,padding=2)
    ax[1,1].set(xticks=positions,xticklabels=summary.cohort,title='D  Cross-method overlap',
               ylabel='SV alleles or SV–environment pairs',ylim=(0,max(summary.both_rda_lfmm.max()*1.43,1.32)))
    ax[1,1].legend(frameon=False,fontsize=6.7,loc='upper left')
    for a in ax.flat:
        a.tick_params(axis='x',labelrotation=15)
    fig.suptitle('Association evidence across methods and cohorts',weight='bold')
    return fig


def paired_plot(root, colors):
    pairs = tsv(root/'paired_statistics.tsv.gz')
    keys=['sv_id','variable']
    if pairs.duplicated(keys).any() or not np.isfinite(pairs[['rho','lfmm_stat_K10']]).all().all():
        raise ValueError('Paired plotting data require unique, finite statistics.')
    tail=float(pairs.lfmm_stat_K10.abs().max()) * 1.04
    fig, ax=plt.subplots(2,3,figsize=(9.2,5.45),sharex=True,sharey=True,layout='constrained')
    norm=LogNorm(vmin=1)
    layers=[]
    records=[]
    for a,env,label in zip(ax.flat,ENV,DISPLAY):
        block=pairs.loc[pairs.variable.eq(env)]
        h=a.hexbin(block.rho,block.lfmm_stat_K10,extent=(-1,1,-tail,tail),gridsize=35,mincnt=1,
                   cmap='Blues',linewidths=.06,norm=norm,rasterized=True)
        if h.get_array().sum()!=len(block):
            raise ValueError(f'Some statistics were lost from bins for {env}.')
        layers.append(h)
        for direction in [a.axhline,a.axvline]:
            direction(0,c='#8E9CA6',lw=.5,ls='--')
        focal=block.loc[block.q.lt(.05)]
        a.scatter(focal.rho,focal.lfmm_stat_K10,s=25,marker='D',edgecolor='white',linewidth=.6,
                  c='#BD503E',zorder=3)
        records.append({'variable':env,'paired_alleles':len(block),'partial_rank_hits':len(focal)})
        a.set(title=f'{label} · {len(block):,} SV alleles',xlim=(-1,1),ylim=(-tail,tail))
        a.label_outer()
    norm.vmax=max(max(layer.get_array()) for layer in layers)
    ax.flat[-1].axis('off')
    ax.flat[-1].text(.04,.87,'Same SV allele and environment\n\nDiamond: partial-rank q < 0.05\n\n'
                    'Each axis uses its own statistic.\nBinned densities describe overlap.',
                    fontsize=8,transform=ax.flat[-1].transAxes,va='top')
    fig.colorbar(layers[0],ax=list(ax.flat[:5]),shrink=.83,label='SV alleles per bin')
    fig.supxlabel('Partial rank correlation (rho)')
    fig.supylabel('Signed LFMM2 K=10 statistic')
    fig.suptitle('Paired association statistics in the main cohort',weight='bold')
    return fig,records


def render(inputs, out, style):
    out.mkdir(parents=True,exist_ok=True)
    theme=json.loads((style/'theme.json').read_text())
    palettes=json.loads((style/'palettes.json').read_text())
    colors=palettes['palettes'][palettes['default']]['categorical']
    ink=theme['colors']['ink']
    plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':theme['typography']['family'],
                         'font.size':8,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':False,
                         'text.color':ink,'axes.edgecolor':ink,'axes.labelcolor':ink,'axes.linewidth':.55,
                         'pdf.fonttype':42,'savefig.facecolor':'white'})
    for spec, plot in zip(NEW,[origin_map,rda_plot,evidence_plot,paired_plot]):
        fig=plot(inputs,colors)
        if isinstance(fig,tuple):
            fig,records=fig
            pd.DataFrame(records).to_csv(out/'matched_statistics_counts.tsv',sep='\t',index=False)
        fig.savefig(out/f'{spec[0]}.pdf',dpi=360)
        fig.savefig(out/f'{spec[0]}.png',dpi=600)
        plt.close(fig)
        print(f'Rendered {spec[0]}',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',type=Path,default=ROOT/'inputs')
    parser.add_argument('--output',type=Path,default=ROOT/'figures')
    parser.add_argument('--style',type=Path,default=ROOT/'style')
    parser.add_argument('--run',type=Path,help='Optional source integration for a completed cohort run.')
    parser.add_argument('--evidence-tables',type=Path)
    parser.add_argument('--basemap',type=Path)
    args=parser.parse_args()
    if args.run:
        if args.evidence_tables is None or args.basemap is None:
            parser.error('--run requires --evidence-tables and --basemap')
        normalize(args.run,args.evidence_tables,args.basemap,args.inputs)
    render(args.inputs,args.output,args.style)
