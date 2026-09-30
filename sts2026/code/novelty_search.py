"""Documented prior-work (novelty) searches on PubMed for candidate objectives.
Records the exact query, hit count, date, and the top titles so the search can be re-run.
Output: sts2026/lit/novelty_searches.md
"""
import json, time, urllib.parse, urllib.request, urllib.error, datetime
from pathlib import Path

Q = {
 "C1 individual resonance / optimal frequency": [
  '("auditory steady-state" OR ASSR) AND (individual OR personalized) AND (resonance OR "optimal frequency" OR "peak frequency")',
  '("40 Hz" OR gamma) AND (entrainment OR stimulation) AND "individual gamma frequency"',
  '("auditory steady-state" OR ASSR) AND (chirp OR "modulation frequency") AND (aging OR older OR elderly)',
  '("gamma sensory stimulation" OR "40 Hz stimulation" OR GENUS) AND (personalized OR individualized) AND frequency',
 ],
 "C2 trait stability + who entrains": [
  '("auditory steady-state" OR ASSR) AND ("test-retest" OR reliability OR ICC)',
  '("40 Hz" AND (auditory OR sound)) AND (dementia OR Alzheimer*) AND (responder* OR "individual differences" OR heterogeneity)',
  '("auditory steady-state" OR ASSR) AND (Alzheimer* OR "mild cognitive impairment" OR dementia)',
 ],
 "C3 entrainment vs superposition (auditory 40 Hz)": [
  '("auditory steady-state" OR ASSR) AND (superposition OR "middle latency") AND (entrainment OR oscillat*)',
  '("40 Hz" OR gamma) AND (auditory) AND (entrainment) AND (offset OR reverberation OR "after stimulus" OR echo OR ringing)',
  '("steady-state" ) AND (entrainment) AND ("evoked" ) AND (superposition) AND (older OR aging OR dementia OR Alzheimer*)',
 ],
 "C4 GENUS transcriptome vs human AD": [
  '("gamma sensory stimulation" OR "40 Hz" OR GENUS) AND (transcriptom* OR "single-nucleus" OR RNA-seq) AND Alzheimer*',
  '("40 Hz") AND (stimulation) AND (transcriptom* OR "single-nucleus") AND (human) AND (signature OR reversal OR "connectivity map")',
 ],
 "C5 structure (AlphaFold) + 40 Hz": [
  '("40 Hz" OR "gamma stimulation" OR GENUS) AND (AlphaFold OR "protein structure" OR docking)',
 ],
}


def _get(url):
    for k in range(6):
        try:
            return json.load(urllib.request.urlopen(url, timeout=30))
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(2 ** k)
    raise RuntimeError("PubMed rate limit")


def esearch(term):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(
        dict(db="pubmed", term=term, retmode="json", retmax=8, sort="relevance"))
    j = _get(url)["esearchresult"]
    ids = j.get("idlist", [])
    titles = []
    if ids:
        time.sleep(1.2)
        u2 = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode(
            dict(db="pubmed", id=",".join(ids), retmode="json"))
        s = _get(u2)["result"]
        titles = [(i, s[i].get("pubdate", "")[:4], s[i].get("title", "")) for i in ids]
    return int(j["count"]), titles


def main():
    out = [f"# Novelty searches (PubMed E-utilities), run {datetime.date.today()}\n",
           "Hit counts are raw; relevance judged by reading the titles and abstracts (notes added in the objective memo).\n"]
    for cand, qs in Q.items():
        out.append(f"\n## {cand}\n")
        for q in qs:
            n, tt = esearch(q)
            time.sleep(1.2)
            out.append(f"\n**Query:** `{q}`  \n**Hits:** {n}\n")
            for pmid, yr, ti in tt:
                out.append(f"- PMID {pmid} ({yr}): {ti}")
    p = Path(__file__).resolve().parents[1] / "lit" / "novelty_searches.md"
    p.write_text("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
