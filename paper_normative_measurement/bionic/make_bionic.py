"""Generate a bionic-reading build: the first letters of each word bold+dark, the rest faded.

WHY IT IS A PREPROCESSOR AND NOT A LATEX MACRO. TeX has no hook that fires per word in the
paragraph builder, so the only place to split a word is before the file is read. That means the
script must reproduce, by hand, every context where text is NOT text: math, command names, the
arguments of reference-like commands, tabular column specifications, and comments. Each protection
below exists because omitting it produced a specific corruption on this document.
"""
import re, pathlib, sys

SRC = pathlib.Path(__file__).resolve().parents[1]
OUT = SRC / "bionic"

# commands whose ARGUMENT must never be split (identifiers, not prose)
OPAQUE = ("begin","end","label","ref","cref","Cref","autoref","cite","citep","citet","input","include",
          "bibliographystyle","bibliography","usepackage","documentclass","newcommand",
          "renewcommand","newenvironment","newtheorem","definecolor","color","hypersetup",
          "titleformat","titlespacing","setlist","captionsetup","usetikzlibrary","texttt",
          "url","href","includegraphics","DeclareMathOperator","newcolumntype","pagestyle",
          "geometry","numberwithin","theoremstyle","setlength","renewcommand","addtolength")

def split_at(w):
    n = len(w)
    return 1 if n <= 3 else 2 if n <= 6 else 3 if n <= 9 else 4

def bionic_words(text):
    """Head bold and near-black, then the tail fades in TWO steps rather than one.
    Ivan asked for a gradual fade; a single flat grey reads as two blocks glued together, whereas
    two steps let the eye leave the word instead of stopping at a boundary."""
    def rep(m):
        w = m.group(0)
        k = split_at(w)
        if len(w) <= k:
            return r"\bi{%s}{}{}" % w
        rest = w[k:]
        h = (len(rest) + 1) // 2
        return r"\bi{%s}{%s}{%s}" % (w[:k], rest[:h], rest[h:])
    # only pure-alphabetic runs of length >= 3; hyphenated parts handled independently
    return re.sub(r"(?<![\\A-Za-z])[A-Za-z]{3,}(?![A-Za-z])", rep, text)

def protect_and_map(line):
    """Replace every non-prose region by a placeholder, transform the rest, restore."""
    store, out, i, n = [], [], 0, len(line)
    def stash(s):
        store.append(s); return "\x00%d\x00" % (len(store)-1)
    while i < n:
        c = line[i]
        # comment: everything to end of line is untouched
        if c == "%" and (i == 0 or line[i-1] != "\\"):
            out.append(stash(line[i:])); break
        # display math \[ ... \]  and inline \( ... \)
        if line.startswith(r"\[", i) or line.startswith(r"\(", i):
            close = r"\]" if line.startswith(r"\[", i) else r"\)"
            j = line.find(close, i+2)
            j = n if j < 0 else j+2
            out.append(stash(line[i:j])); i = j; continue
        # inline math $ ... $
        if c == "$":
            j = i+1
            while j < n and not (line[j] == "$" and line[j-1] != "\\"): j += 1
            j = min(j+1, n)
            out.append(stash(line[i:j])); i = j; continue
        # a control sequence
        if c == "\\":
            m = re.match(r"\\([A-Za-z@]+|.)", line[i:])
            cs = m.group(0); name = m.group(1)
            j = i + len(cs)
            if name in OPAQUE:
                # swallow every following bracket group so identifiers are never split
                while j < n and line[j] in "[{":
                    close = "]" if line[j] == "[" else "}"
                    d, k = 0, j
                    while k < n:
                        if line[k] in "[{": d += 1
                        elif line[k] in "]}":
                            d -= 1
                            if d == 0: k += 1; break
                        k += 1
                    j = k
                out.append(stash(line[i:j])); i = j; continue
            out.append(stash(cs)); i = j; continue        # command name only; its text arg is prose
        # a tabular column spec or similar brace group directly after \begin{...}
        out.append(c); i += 1
    body = "".join(out)
    body = bionic_words(body)
    for idx, s in enumerate(store):
        body = body.replace("\x00%d\x00" % idx, s)
    return body

MATHENV = ("equation","equation*","align","align*","gather","gather*","multline",
           "multline*","eqnarray","split","array","cases","tikzpicture","verbatim")

def protect_blocks(txt):
    """Stash multi-line math and picture environments BEFORE any line-wise work.
    A line-wise protector cannot see a \\[ that opens on one line and closes on another, which is
    exactly how the first build corrupted part0b."""
    store = []
    def stash(m):
        store.append(m.group(0)); return "\x01%d\x01" % (len(store)-1)
    txt = re.sub(r"\\\[.*?\\\]", stash, txt, flags=re.S)
    for e in MATHENV:
        txt = re.sub(r"\\begin\{"+re.escape(e)+r"\}.*?\\end\{"+re.escape(e)+r"\}",
                     stash, txt, flags=re.S)
    return txt, store

def restore_blocks(txt, store):
    for i, s_ in enumerate(store):
        txt = txt.replace("\x01%d\x01" % i, s_)
    return txt

def process(txt):
    txt, store = protect_blocks(txt)
    txt = "\n".join(protect_and_map(l) for l in txt.split("\n"))
    return restore_blocks(txt, store)

def main():
    files = ["partA_concept.tex","partB_object_problems.tex","partm1_notation.tex",
             "part0_math.tex","part0b_worked.tex","part1_object.tex","part1b_toy.tex",
             "part3_gaps.tex","part2_estimators.tex"]
    VERBATIM = ["evidence_firewall.tex"]
    OUT.mkdir(exist_ok=True)
    for f in files:
        (OUT / f).write_text(process((SRC / f).read_text()))
    for f in VERBATIM:
        (OUT / f).write_text((SRC / f).read_text())
    # main + preamble carry structure, not prose: copy, then add the \bi macro
    pre = (SRC / "preamble.tex").read_text()
    pre += ("\n%% ---- bionic reading ----\n"
            "\\definecolor{BioInk}{HTML}{0B0E11}\n"
            "\\definecolor{BioMid}{HTML}{5C666D}\n"
            "\\definecolor{BioFade}{HTML}{97A0A6}\n"
            "\\newcommand{\\bi}[3]{{\\bfseries\\color{BioInk}#1}"
            "{\\color{BioMid}#2}{\\color{BioFade}#3}}\n")
    (OUT / "preamble.tex").write_text(pre)
    mt = (SRC / "main.tex").read_text()
    mt = protect_and_map_block(mt)
    (OUT / "main.tex").write_text(mt)
    print("wrote", OUT)

def protect_and_map_block(txt):
    keep, body = txt.split("\\begin{document}", 1)
    return keep + "\\begin{document}" + process(body)

if __name__ == "__main__":
    sys.exit(main())
