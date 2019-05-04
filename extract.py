#!/usr/bin/python3

###################################################################
#    File name     : extract.py
#    Author        : sha-ou
#    Date          : 2019年03月28日 星期四 13时08分53秒
#    Description   : 
###################################################################

import os
import re
import sys

common_pattern = r'^bv_1700_pbase_(\w+?)_jfet_(\d+?)_depth1_(\d+?)_cipconc_(\w+?)_cipthick_(\d\d)_cipwidthp_(\d{3})'
bv_pattern = r'_bv_623K\.log'
id_pattern = r'_id_Vg_20\.log'
ig_pattern = r'_ig_300K\.log'

def extract_slop(outf=None):
    '''\
Extract max slope
    '''
    if outf is None:
        outf = 'slope.csv'
    if os.path.exists(outf):
        os.remove(outf)
    title = 'pbase,jfet,depth1,cipconc,cipthick,cipwidthp,slope'
    extractm = 'extract init inf="{inf}"\n' + \
            'extract name="{pbase},{jfet},{depth1},{cipconc},{cipthick},{cipwidthp}," slope(maxslope(curve(v."drain", i."drain"))) ' +\
            'datafile="{dataf}"\n'
    pattern = re.compile(common_pattern + id_pattern)
    content = extract(outf, extractm, pattern)
    srcf = 'extract-slope.in'
    f = open(srcf, 'w')
    f.write(content)
    f.close()
    os.system('deckbuild -run -ascii %s' % srcf)
    os.system("sed -i '/^$/d' %s" % outf)
    os.system("sed -i '1i %s' %s" % (title, outf))

def extract_oxi(outf=None):
    if outf is None:
        outf = 'oxi-bv.csv'
    if os.path.exists(outf):
        os.remove(outf)
    title = 'pbase,jfet,depth1,cipconc,cipthick,cipwidthp,oxi'
    extractm = 'extract init inf="{inf}"\n' + \
            'extract name="{pbase},{jfet},{depth1},{cipconc},{cipthick},{cipwidthp}," x.val from curve(v."drain", probe."oxideField_y") ' +\
            'where y.val=-4e6 datafile="{dataf}"\n'
    pattern = re.compile(common_pattern + bv_pattern)
    content = extract(outf, extractm, pattern)
    srcf = 'extract-ava.in'
    f = open(srcf, 'w')
    f.write(content)
    f.close()
    os.system('deckbuild -run -ascii %s' % srcf)
    os.system("sed -i '/^$/d' %s " % outf)
    os.system("sed -i '1i %s' %s" % (title, outf))

def extract_ava(outf=None):
    if outf is None:
        outf = 'ava-bv.csv'
    if os.path.exists(outf):
        os.remove(outf)
    title = 'pbase,jfet,depth1,cipconc,cipthick,cipwidthp,ava'
    extractm = 'extract init inf="{inf}"\n' + \
            'extract name="{pbase},{jfet},{depth1},{cipconc},{cipthick},{cipwidthp}," x.val from curve(v."drain", i."drain") ' +\
            'where y.val=1e-10 datafile="{dataf}"\n'
    pattern = re.compile(common_pattern + bv_pattern)
    content = extract(outf, extractm, pattern)
    srcf = 'extract-ava.in'
    f = open(srcf, 'w')
    f.write(content)
    f.close()
    os.system('deckbuild -run -ascii %s' % srcf)
    os.system("sed -i '/^$/d' %s " % outf)
    os.system("sed -i '1i %s' %s" % (title, outf))

def extract(outf, extractm, pattern):
    content = ''
    for file in os.listdir():
        matched = pattern.match(file)
        if matched:
            pbase,jfet,depth1,cipconc,cipthick, cipwidthp = matched.groups()
            content = content + extractm.format(
                    inf=file, pbase=pbase, jfet=float(jfet)/10,
                    depth1=float(depth1)/10, dataf=outf,
                    cipconc=cipconc, cipthick=float(cipthick)/10, cipwidthp=int(cipwidthp)
                    )
    content = content + 'quit'
    return content

if __name__ == '__main__':
    if len(sys.argv) == 1:
        extract_ava()
        extract_oxi()
        extract_slop()
    if 'bv' in sys.argv:
        extract_ava()
        extract_oxi()
    if 'slope' in sys.argv:
        extract_slop()

