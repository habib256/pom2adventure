"""Report explicit contract registration, never infer complete narrative coverage."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('audit',type=Path)
p.add_argument('output',type=Path)
a=p.parse_args();audit=json.loads(a.audit.read_text())
reviewed={int(x) for x in audit['required']}
groups={
 'conditions':set('V VR AC CI CN CV CX CG CB CT CA GU CU CP'.split()),
 'effects':set('G GX GA E E0 EH P PC PD PO PS PX TR'.split()),
 'random_tests':set('CL CE CS ED DV'.split()),
 'combat':set('M MM MF MR MD MS MI MV MB CF'.split()),
}
rows={}
for label,ops in groups.items():
 pages={int(n) for n,row in audit['corpus']['FR'].items() if any(line.split()[0] in ops for line in row['mechanics'])}
 rows[label]={'pages':len(pages),'registered':sorted(pages & reviewed),'unregistered':sorted(pages-reviewed)}
result={'scope':'Explicit required contracts only. Registration does not certify the entire page; categories overlap. Unregistered is not proof that no test exists.', 'corpus_pages':len(audit['corpus']['FR']),'registered_pages':len(reviewed),'audit_errors':audit['errors'],'categories':rows}
a.output.write_text(json.dumps(result,indent=2)+'\n')
for label,row in rows.items():print(label,':',len(row['registered']),'registered /',row['pages'],'pages;',len(row['unregistered']),'without explicit registered contract')
