"""Import English reference figures and extend the numbered project figure library."""
import argparse
from collections import Counter
import csv
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from zipfile import ZipFile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from render_current import NEW

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
COMMIT = '2128a965825251e39fedf6599ab2efd182c89d1a'
UPSTREAM = f'https://github.com/issacjohn9955-max/Figures/tree/{COMMIT}'


def load(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def write(path, rows):
    with path.open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def page_count(pdf):
    info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
    return int(re.search(r'^Pages:\s+(\d+)$', info, re.M)[1])


def english_and_single(pdf):
    assert page_count(pdf) == 1, pdf
    content = subprocess.check_output(['pdftotext', str(pdf), '-'], text=True)
    if re.search(r'[\u3400-\u9fff]', content):
        raise ValueError(f'Select an English reference for {pdf.name}.')


def reference_specs(source, revision):
    specs=load(ROOT/'figure_sources.tsv')
    rows=[]
    for index, item in enumerate(specs, 1):
        module=item['module']
        folder=source/module
        stems=folder/item['stem']
        name=f'F{index:02d}_{module}_{Path(item["stem"]).name}'
        target=ROOT/'references'/f'{name}.pdf'
        ref_pdf=(revision/item['revision']).with_suffix('.pdf') if item['revision'] else stems.with_suffix('.pdf')
        english_and_single(ref_pdf)
        shutil.copyfile(ref_pdf,target)
        code_dir=ROOT/'references'/'source'/module
        code_dir.mkdir(parents=True,exist_ok=True)
        paths=[*folder.glob('README.md'), *folder.glob('CAPTIONS.md'), *folder.glob('plot*.py'), *folder.glob('plot*.R')]
        if module == 'fig1_chicken_GRCg7b_circos':
            paths.extend((folder/'06_scripts').glob('plot*.R'))
        for path in paths:
            shutil.copyfile(path,code_dir/path.name)
        rows.append(dict(number=f'F{index:02d}',gallery_page=30+index,title=item['title'],
                         provenance=item['provenance'],file=target.relative_to(ROOT).as_posix(),
                         module=module,condition=item['condition'],source=f'{UPSTREAM}/{module}',
                         sha256=sha256(target.read_bytes()).hexdigest()))
    if len({r['module'] for r in rows})!=17:
        raise ValueError('Expected one or more English examples from each of the 17 source modules.')
    return rows


def project_specs():
    rows=[]
    original=load(PROJECT/'tables/figure_catalog.tsv')
    prior=PROJECT/'deliverables/Chicken_SV_environment_complete_delivery_20261121.zip'
    individual=ROOT/'baseline'
    individual.mkdir(exist_ok=True)
    with ZipFile(prior) as archive:
        names=sorted(n for n in archive.namelist() if re.fullmatch(r'figure_files/\d\d_.*\.pdf',n))
        if len(names)!=len(original):
            raise ValueError('Existing gallery and individual figure count disagree.')
        for index, (item, name) in enumerate(zip(original,names),1):
            asset=individual/Path(name).name
            asset.write_bytes(archive.read(name))
            rows.append(dict(number=f'{index:02d}',gallery_page=index+2,title=item['title'],
                             provenance=item['kind'],file=asset.relative_to(ROOT).as_posix(),
                             module=item['id'],condition='',source=item['reference'],
                             sha256=sha256(asset.read_bytes()).hexdigest()))
    for stem,title,module in NEW:
        index=int(stem[:2])
        asset=ROOT/'figures'/f'{stem}.pdf'
        english_and_single(asset)
        rows.append(dict(number=f'{index:02d}',gallery_page=index+2,title=title,provenance='observed',
                         file=asset.relative_to(ROOT).as_posix(),module=module,condition='Completed SV cohort tables',
                         source=f'{UPSTREAM}/{module}',sha256=sha256(asset.read_bytes()).hexdigest()))
    return rows


def index_page(path,title,subtitle,rows):
    fig=plt.figure(figsize=(8.27,11.69),facecolor='white')
    fig.text(.07,.93,title,fontsize=19,weight='bold',color='#273746')
    fig.text(.07,.892,subtitle,fontsize=9,color='#386C8C')
    for x,name in [(.07,'ID'),(.15,'Page'),(.235,'Figure'),(.76,'Provenance')]:
        fig.text(x,.847,name,fontsize=9,weight='bold',color='#273746')
    y=.819
    for row in rows:
        for x, value in [(.07,row['number']),(.15,str(row['gallery_page'])),(.235,row['title']),(.76,row['provenance'])]:
            fig.text(x,y,value,fontsize=8,color='#273746')
        if row['source'].startswith('https://'):
            fig.text(.93,y,'↗',fontsize=8,color='#386C8C',url=row['source'])
        y-=.026
    fig.savefig(path)
    plt.close(fig)


def build(source, revision):
    project=project_specs()
    references=reference_specs(source,revision)
    write(ROOT/'figure_library_catalog.tsv',project+references)
    output=ROOT/'deliverables'
    output.mkdir(exist_ok=True)
    project_index=output/'project_index.pdf'
    reference_index=output/'reference_index.pdf'
    index_page(project_index,'Chicken SV–environment figure library',
               'Project figures · the existing gallery begins on page 2',project)
    index_page(reference_index,'Figures repository reference plates',
               'Historical and synthetic examples · reuse requires the input listed in the catalogue',references)
    base=PROJECT/'deliverables/SV_complete_figure_gallery.pdf'
    target=output/'SV_figure_library.pdf'
    pending=target.with_suffix('.building.pdf')
    paths=[project_index,base,*(ROOT/r['file'] for r in project[23:]),reference_index,
           *(ROOT/r['file'] for r in references)]
    subprocess.run(['pdfunite',*(str(p) for p in paths),str(pending)],check=True)
    expected=1+page_count(base)+len(project[23:])+1+len(references)
    assert page_count(pending)==expected==references[-1]['gallery_page']
    pending.replace(target)
    print(f'{len(project)} project figures and {len(references)} reference figures, {expected} PDF pages.',flush=True)
    (output/'validation.json').write_text(json.dumps({
        'status':'PASS','project_figures':dict(Counter(r['provenance'] for r in project)),
        'reference_figures':len(references),'reference_modules':len({r['module'] for r in references}),
        'gallery_pages':expected,'gallery_sha256':sha256(target.read_bytes()).hexdigest(),
        'upstream_commit':COMMIT,
    },ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    repo=PROJECT.parent/'21_figure_reproduction_20261113'
    parser.add_argument('--source',type=Path,default=repo/'source')
    parser.add_argument('--revision',type=Path,default=repo/'revision_content_20261114/figures')
    args=parser.parse_args()
    build(args.source,args.revision)
