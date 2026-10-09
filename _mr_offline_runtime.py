"""Offline CPU English->Marathi (Devanagari) translation via MIT IndicTrans2 distilled model."""
import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from IndicTransToolkit import IndicProcessor

MODEL_ID="naklitechie/indictrans2-en-indic-dist-200M"
torch.set_num_threads(2)
processor=IndicProcessor(inference=True)
tokenizer=AutoTokenizer.from_pretrained(MODEL_ID,trust_remote_code=True)
model=AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID,trust_remote_code=True,use_safetensors=True).eval()
print("MARATHI_MODEL_LOADED",MODEL_ID,flush=True)

def split_long_text(text,max_chars=760):
    if len(text)<=max_chars:return [text]
    pieces=re.split(r"(?<=[.!?])\s+(?=[A-Z§\"'])",text)
    if len(pieces)==1:
        pieces=re.split(r'(?<=;)\s+',text)
    out=[];buf=""
    for p in pieces:
        if len(p)>max_chars:
            if buf:out.append(buf);buf=""
            words=p.split(" ");chunk=""
            for word in words:
                if len(chunk)+len(word)+1>max_chars and chunk:
                    out.append(chunk);chunk=""
                chunk=(chunk+" "+word).strip()
            if chunk:out.append(chunk)
            continue
        if buf and len(buf)+len(p)+1>max_chars:
            out.append(buf);buf=""
        buf=(buf+" "+p).strip()
    if buf:out.append(buf)
    return out or [text]

def _translate(texts):
    if not texts:return []
    prepared=processor.preprocess_batch(texts,src_lang="eng_Latn",tgt_lang="mar_Deva")
    enc=tokenizer(prepared,padding="longest",truncation=True,max_length=512,return_tensors="pt",return_attention_mask=True)
    with torch.inference_mode():
        out=model.generate(**enc,use_cache=True,max_new_tokens=360,num_beams=3,num_return_sequences=1)
    decoded=tokenizer.batch_decode(out,skip_special_tokens=True,clean_up_tokenization_spaces=True)
    result=processor.postprocess_batch(decoded,lang="mar_Deva")
    if len(result)!=len(texts):
        raise ValueError("Offline model translation cardinality mismatch")
    return result

def translate_batch(texts):
    # Maintain cardinality and never join separate source text slots.
    parts=[];bounds=[]
    for t in texts:
        chunks=split_long_text(t)
        bounds.append(len(chunks))
        parts.extend(chunks)
    translations=[]
    for k in range(0,len(parts),8):
        translations.extend(_translate(parts[k:k+8]))
    output=[];i=0
    for n in bounds:
        output.append(" ".join(translations[i:i+n]))
        i+=n
    return output
