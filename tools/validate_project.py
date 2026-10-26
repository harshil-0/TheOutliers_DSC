"""Independent checks of the saved data, statistics and notebook.

Run after analysis.py: python tools/validate_project.py [--pdf]
The optional PDF checks require pymupdf (requirements-notebook.txt).
No inferential method, threshold or dataset is selected by these checks.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import platform
import re

import numpy as np
import pandas as pd
from scipy import sparse, stats

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', action='store_true')
    args = parser.parse_args()
    checks = []
    def passed(name):
        checks.append(name)
    r = json.loads((ROOT/'results/results.json').read_text())
    raw_hash = hashlib.sha256((ROOT/'data/raw/Online_Retail.xlsx').read_bytes()).hexdigest()
    assert raw_hash == r['sha256'] == '43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d'
    passed('Original workbook SHA-256 matches source baseline')
    x = pd.read_csv(ROOT/'data/processed/clean_transactions.csv.gz',
                    dtype={'CustomerID':str,'StockCode':str,'InvoiceNo':str},
                    parse_dates=['Day','InvoiceDate'])
    c = pd.read_csv(ROOT/'data/processed/customer_cohort.csv',dtype={'CustomerID':str},
                    parse_dates=['index_day','second_day'])
    days = pd.read_csv(ROOT/'data/processed/uk_shopping_days.csv',dtype={'CustomerID':str},parse_dates=['Day'])
    assert len(x)==391150 and not x.duplicated().any()
    assert x.CustomerID.notna().all() and x.Quantity.gt(0).all() and x.UnitPrice.gt(0).all()
    assert not x.InvoiceNo.str.upper().str.startswith('C').any()
    assert x.StockCode.str.fullmatch(r'\d{5}[A-Za-z]{0,2}').all()
    np.testing.assert_allclose(x.LineValue,x.Quantity*x.UnitPrice)
    assert x.Day.equals(x.InvoiceDate.dt.normalize())
    flow = pd.read_csv(ROOT/'results/cleaning_flow.csv')
    assert flow.rows.tolist()==[541909,536641,524878,392692,391150]
    assert flow.removed_at_step.sum()+len(x)==541909
    passed('Cleaning rules, row reconciliation and monetary/date derivations')
    daily = x.loc[x.Country.eq('United Kingdom')].groupby(['CustomerID','Day']).agg(
        breadth=('StockCode','nunique'),spend=('LineValue','sum'),
        units=('Quantity','sum'),invoices=('InvoiceNo','nunique')).reset_index()
    pd.testing.assert_frame_equal(daily,days,check_dtype=False,rtol=1e-12,atol=1e-9)
    first = daily.sort_values('Day').groupby('CustomerID').head(1)
    first = first.loc[first.Day.between('2011-01-01','2011-08-31')].set_index('CustomerID').sort_index()
    ci = c.set_index('CustomerID').sort_index()
    assert len(c)==2172 and c.CustomerID.is_unique and first.index.equals(ci.index)
    np.testing.assert_array_equal(first.Day,ci.index_day)
    for field in ['breadth','spend','units','invoices']:
        np.testing.assert_allclose(first[field],ci['first_'+field])
    joined = daily.merge(c[['CustomerID','index_day']],on='CustomerID',validate='many_to_one')
    elapsed = (joined.Day-joined.index_day).dt.days
    future = joined.loc[elapsed.gt(0)&elapsed.le(90)]
    totals = future.groupby('CustomerID').agg(spend90=('spend','sum'),days90=('Day','size')).reindex(ci.index).fillna(0)
    np.testing.assert_allclose(totals.spend90,ci.spend90,rtol=1e-12,atol=1e-9)
    np.testing.assert_array_equal(totals.days90,ci.days90)
    second = future.sort_values('Day').groupby('CustomerID').head(1).set_index('CustomerID').reindex(ci.index)
    pd.testing.assert_series_equal(second.Day,ci.second_day,check_names=False)
    np.testing.assert_allclose(second.breadth,ci.second_breadth,equal_nan=True)
    np.testing.assert_allclose((ci.second_day-ci.index_day).dt.days,ci.return_gap_days,equal_nan=True)
    np.testing.assert_array_equal(ci.days90.gt(0).astype(int),ci.repeat90)
    assert (ci.index_day+pd.Timedelta(days=90)<=daily.Day.max()).all()
    assert ci.loc[ci.repeat90.eq(0),'return_gap_days'].isna().all()
    passed('Customer eligibility, index/follow-up separation, aggregation and conditional gaps')
    matrix=sparse.load_npz(ROOT/'data/processed/encoded_transactions.npz')
    columns=json.loads((ROOT/'data/processed/encoded_columns.json').read_text())
    assert matrix.shape==(391150,60) and len(columns)==60
    np.testing.assert_allclose(matrix[:,:3].toarray(),x[['Quantity','UnitPrice','LineValue']])
    np.testing.assert_array_equal(matrix[:,3].toarray().ravel(),x.InvoiceDate.dt.hour)
    for prefix,labels in [('Country_',x.Country),('YearMonth_',x.InvoiceDate.dt.strftime('%Y-%m')),
                          ('Weekday_',x.InvoiceDate.dt.day_name())]:
        indices=[i for i,name in enumerate(columns) if name.startswith(prefix)]
        block=matrix[:,indices]
        np.testing.assert_array_equal(np.asarray(block.sum(axis=1)).ravel(),np.ones(len(x)))
        actual=np.array([columns[indices[i]][len(prefix):] for i in np.asarray(block.argmax(axis=1)).ravel()])
        np.testing.assert_array_equal(actual,labels)
    passed('Encoded values, one-hot levels and full row alignment')
    tests=r['results']; assert [t['test'] for t in tests]==['T1','T2','T3','T4','T5']
    a=c.loc[c.broad.eq(1)];b=c.loc[c.broad.eq(0)];p=c.loc[c.repeat90.eq(1)]
    pooled=(a.repeat90.sum()+b.repeat90.sum())/len(c)
    gap=a.repeat90.mean()-b.repeat90.mean()
    z=gap/np.sqrt(pooled*(1-pooled)*(1/len(a)+1/len(b)))
    np.testing.assert_allclose(z*z,tests[0]['statistic'])
    np.testing.assert_allclose(2*stats.norm.sf(abs(z)),tests[0]['p'])
    def check_welch(left,right,result):
        n,m=len(left),len(right)
        v,w=np.var(left,ddof=1)/n,np.var(right,ddof=1)/m
        estimate=np.mean(left)-np.mean(right); se=np.sqrt(v+w)
        df=(v+w)**2/(v*v/(n-1)+w*w/(m-1))
        np.testing.assert_allclose([estimate,estimate/se,df],[result['estimate'],result['statistic'],result['df']])
        np.testing.assert_allclose(2*stats.t.sf(abs(estimate/se),df),result['p'])
        np.testing.assert_allclose(estimate+np.array([-1,1])*stats.t.ppf(.975,df)*se,result['ci'])
    check_welch(a.log_spend90,b.log_spend90,tests[1])
    d=p.second_breadth-p.first_breadth
    independent_t=stats.ttest_1samp(d,0)
    np.testing.assert_allclose([independent_t.statistic,independent_t.pvalue],[tests[2]['statistic'],tests[2]['p']])
    check_welch(p.loc[p.broad.eq(1),'return_gap_days'],p.loc[p.broad.eq(0),'return_gap_days'],tests[3])
    ranked_x=p.first_breadth.rank(method='average');ranked_y=p.days90.rank(method='average')
    rho=np.corrcoef(ranked_x,ranked_y)[0,1]
    ref_t=rho*np.sqrt((len(p)-2)/(1-rho**2))
    np.testing.assert_allclose([rho,ref_t,2*stats.t.sf(abs(ref_t),len(p)-2)],
                               [tests[4]['statistic'],tests[4]['approx_t'],tests[4]['p']])
    previous=0.
    for rank,(original,t) in enumerate(sorted(enumerate(tests),key=lambda pair:pair[1]['p'])):
        expected=max(previous,min(1.,(len(tests)-rank)*t['p']))
        np.testing.assert_allclose(expected,t['holm_p'])
        assert (expected<.05)==t['reject_holm']
        previous=expected
    assert [t['reject_holm'] for t in tests]==[True,True,True,False,False]
    for t in tests:
        assert len(t['ci'])==2 and np.isfinite(t['ci']).all() and t['ci'][0]<t['ci'][1]
    # Original three-test estimates were independently reproduced before extension.
    np.testing.assert_allclose([t['estimate'] for t in tests[:3]],
                              [0.1084695955164669,0.7210070167457319,-6.092255125284738],rtol=1e-12)
    csv=pd.read_csv(ROOT/'results/hypothesis_tests.csv')
    np.testing.assert_allclose(csv.ci_low,[t['ci'][0] for t in tests])
    np.testing.assert_allclose(csv.ci_high,[t['ci'][1] for t in tests])
    np.testing.assert_allclose(csv.holm_p,[t['holm_p'] for t in tests])
    passed('Independent test formulas, five-test Holm, intervals and CSV/JSON agreement')
    notebook=json.loads((ROOT/'project.ipynb').read_text(encoding='utf-8'))
    cells=[cell for cell in notebook['cells'] if cell['cell_type']=='code']
    assert [cell['execution_count'] for cell in cells]==list(range(1,len(cells)+1))
    assert not any(o['output_type']=='error' for cell in cells for o in cell['outputs'])
    analysis_cells='\n'.join(''.join(cell['source']) for cell in cells[1:-1])
    assert ast.dump(ast.parse(analysis_cells))==ast.dump(ast.parse((ROOT/'analysis.py').read_text(encoding='utf-8')))
    stream='\n'.join(''.join(o.get('text',[])) for cell in cells for o in cell['outputs'] if o['output_type']=='stream')
    embedded,_=json.JSONDecoder().raw_decode(stream[stream.index('{'):])
    assert embedded['results']==r['results']
    image_count=sum('image/png' in o.get('data',{}) for cell in cells for o in cell['outputs'])
    assert image_count==6
    passed('Executed notebook: sequential counts, no errors, source/results agreement and six figures')
    pdf_pages=None
    if args.pdf:
        import pymupdf
        doc=pymupdf.open(ROOT/'report.pdf');pdf_pages=len(doc)
        text='\n'.join(page.get_text() for page in doc)
        assert pdf_pages<=8
        for phrase in ['Aayush Gupta','Harshil','Raghav Mittal','Utkarsh','Jaideep Dahiya',
                       '2023014','2023235','2023415','2023569','2023254',
                       'raghav23415@iiitd.ac.in','Test 1','Test 2','Test 3','Test 4','Test 5',
                       '0.9692','0.0236']:
            assert phrase in text,phrase
        for stale in ['Complete]','Enter your','Team Kurtosis','Zomato','Bengaluru','iiird.ac.in']:
            assert stale not in text,stale
        links=[link.get('uri','') for page in doc for link in page.get_links()]
        assert 'https://github.com/harshil-0/TheOutliers_DSC' in links
        for page in doc:
            for word in page.get_text('words'):
                assert 0<=word[0]<=word[2]<=page.rect.width+1 and 0<=word[1]<=word[3]<=page.rect.height+1
        log=(ROOT/'report.log')
        if log.exists():
            assert 'Overfull' not in log.read_text(errors='replace')
        passed('PDF page limit, team metadata, five tests, link, placeholders and text bounds')
    summary={'status':'passed','checks':checks,'check_count':len(checks),
             'python':platform.python_version(),'main_tests':5,'customers':len(c),'returners':len(p),
             'pdf_pages':pdf_pages,'notebook_code_cells':len(cells),'embedded_figures':image_count,
             'source_sha256':raw_hash,'scope_note':'Computational checks do not certify individual member review or external submission.'}
    (ROOT/'results/validation.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
