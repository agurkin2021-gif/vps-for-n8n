from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent
SENTENCE_UPDATES={
"te/index.html":{
"దిగుమతులు, పత్రాలు & భారీ ఉద్యోగాలు":"డేటా దిగుమతులు, పత్రాలు, భారీ పనులు",
"ఒక ఉదాహరణతో ప్రారంభించండి. అవసరమైనప్పుడు కార్మికులను చేర్చుకోండి.":"ఒక n8n ఇన్‌స్టాన్స్‌తో ప్రారంభించండి. అవసరమైతే వర్కర్లను జోడించండి.",
"అమలు n8n":"n8nను డిప్లాయ్ చేయండి",
"ఉత్పత్తి భద్రత":"ప్రొడక్షన్ భద్రత",
"క్యూ మోడ్ & కార్మికులు":"Queue Mode, వర్కర్లు"
},
"te/n8n-vps-requirements.html":{
"CPU / కరెన్సీ":"CPU / సమాంతర పనులు",
"ఏకకాలిక మరణశిక్షలు":"ఒకేసారి నడిచే ఎగ్జిక్యూషన్లు",
"కాంతి, ఎల్లప్పుడూ ఆన్‌లో ఉండే ఉదాహరణ":"తేలికపాటి, ఎల్లప్పుడూ నడిచే n8n ఇన్‌స్టాన్స్",
"ఆచరణాత్మక చిన్న ఉత్పత్తి":"చిన్న ప్రొడక్షన్‌కు ఆచరణయోగ్యమైన సెటప్",
"కాంతి, ఎల్లప్పుడూ ఆన్‌లో ఉండే ఉదాహరణ":"తేలికపాటి, ఎల్లప్పుడూ నడిచే n8n ఇన్‌స్టాన్స్"},
"te/n8n-queue-mode.html":{
"కార్మికుల సామర్థ్యం":"వర్కర్ల సామర్థ్యం",
"కార్మికులు గణన మరియు ప్రతి కార్మికుని ఉద్యోగాల ద్వారా స్కేల్ చేస్తారు":"వర్కర్ల సంఖ్యతో పాటు ఒక్కో వర్కర్‌లో సమాంతర పనుల పరిమితి కూడా ముఖ్యం",
"ఎప్పుడు కార్మికులను జోడించండి":"అదనపు వర్కర్లను ఎప్పుడు జోడించాలి?",
"ఎప్పుడు సమ్మతిని పెంచండి":"సమాంతర పనుల పరిమితిని ఎప్పుడు పెంచాలి?",
"ఎప్పుడు సమ్మతిని తగ్గించండి":"సమాంతర పనుల పరిమితిని ఎప్పుడు తగ్గించాలి?",
"PostgreSQL చూడండి":"PostgreSQL పనితీరును పర్యవేక్షించండి"}
}
HEADING=re.compile(r'(<h[2-4]\b[^>]*>)([\s\S]*?)(</h[2-4]>)',re.I)
def main():
    for rel,replacements in SENTENCE_UPDATES.items():
        p=ROOT/rel
        content=p.read_text(encoding="utf-8")
        def rewrite(m):
            key=m.group(2).strip()
            if key in replacements:return m.group(1)+replacements[key]+m.group(3)
            return m.group()
        updated=HEADING.sub(rewrite,content)
        p.write_text(updated,encoding="utf-8")
    from _te_translate_full import PAGES
    for _,rel in PAGES:
        p=ROOT/rel
        body=p.read_text(encoding="utf-8")
        for old,new in (
            ("మరణశిక్షలు","ఎగ్జిక్యూషన్లు"),
            ("కార్మికులు","వర్కర్లు"),
            ("ఉద్యోగాలు","పనులు"),
            ("కరెన్సీ నియంత్రణలు","కంకరెన్సీ నియంత్రణలు"),
            ("ఉత్పత్తి-కరెన్సీ","ప్రొడక్షన్ కంకరెన్సీ"),
            ("తక్కువ-కరెన్సీ","తక్కువ కంకరెన్సీ")
        ):
            body=body.replace(old,new)
        p.write_text(body,encoding="utf-8")
    for rel in ["te/index.html","_te_editorial.py"]:
        p=ROOT/rel
        s=p.read_text(encoding="utf-8")
        s=s.replace("n8n కోసం VPS రోజుకు $0.07 నుంచి","n8n కోసం VPS $0.07/Day నుంచి")
        p.write_text(s,encoding="utf-8")
if __name__=="__main__":main()
