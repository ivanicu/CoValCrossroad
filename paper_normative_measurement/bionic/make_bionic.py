"""Bionic-reading build, with the policy copied from the local book3 / atomizer reader.

WHERE THE POLICY COMES FROM
    reader/assets/core/core.js  ->  BSTOP, bionicVars(), _bxFreqScan(), _bxCommon(), _bxApplyOne()
    reader/assets/reader.css    ->  .bx, .bxr, .w.bx-fade

MY FIRST VERSION HAD IT BACKWARDS, AND THAT IS EXACTLY WHAT "TOO DARK" MEANT.
    mine    : content-word TAILS heavily faded; function words left at FULL ink.
    reader  : function words recede AS WHOLE UNITS; content-word tails stay nearly
              full strength (opacity .78 at the default contrast).
    The page reads heavy in mine because the thousands of short glue words end up the
    darkest thing on it, and the words worth navigating by end up the palest.

WHY A PREPROCESSOR AND NOT A MACRO
    TeX has no per-word hook in the paragraph builder, so a word can only be split
    before the file is read. Everything in protect_and_map() below exists because
    omitting it corrupted this document in a specific way, found by rendering.
"""
import re, pathlib, sys, math

SRC = pathlib.Path(__file__).resolve().parents[1]
OUT = SRC / "bionic"

# --------------------------------------------------------------------------- policy
BSTOP = set("the a an and or of to in on at is are be as by for we it that this "
            "with from can not but if so".split())          # core.js BSTOP, verbatim

FRAC = 0.40                                                  # core.js bP().get('frac',0.4)

# core.js contrast preset 'mid' is weight 700 / rest .78 / fade .46. Opacity is emulated
# as a blend over white: c = 255 - alpha*(255 - ink).
INK, REST, FADE = "14181C", "484C50", "93989B"

FREQ, LNMAX = {}, 1.0


def freq_scan(texts):
    """core.js _bxFreqScan. Commonness is measured on THIS document, so a frequent topic
    term is not mistaken for glue."""
    global FREQ, LNMAX
    FREQ = {}
    for t in texts:
        for tok in re.findall(r"[A-Za-z]+", t):
            w = tok.lower()
            FREQ[w] = FREQ.get(w, 0) + 1
    LNMAX = math.log(max(FREQ.values(), default=1) + 1) or 1.0


def commonness(w):
    return math.log(FREQ.get(w, 1) + 1) / LNMAX              # 1 = most common, 0 = rare


def is_function_word(w, n):
    """core.js: stoplist floor OR (common AND short). The len<=5 guard is theirs and exists
    to stop a frequent TOPIC term being treated as glue."""
    return (w in BSTOP) or (commonness(w) >= 0.80 and n <= 5)


def head_len(word, rarity):
    """core.js: k = max(1, round(len*frac*(0.5+0.5*rarity))); if k>=len then k=len-1.
    A rare word gets a LONGER head; a common content word a shorter one."""
    n = len(word)
    k = max(1, round(n * FRAC * (0.5 + 0.5 * rarity)))
    return n - 1 if k >= n else k


def bionic_words(text):
    def rep(m):
        w = m.group(0)
        lw = w.lower()
        n = len(w)
        if n < 3:                                            # core.js: len<3 untouched
            return w
        if is_function_word(lw, n):                          # subtractive: whole word recedes
            return "\\bfade{" + w + "}"
        k = head_len(w, 1.0 - commonness(lw))
        return "\\bi{" + w[:k] + "}{" + w[k:] + "}"
    return re.sub(r"(?<![\\A-Za-z])[A-Za-z]{3,}(?![A-Za-z])", rep, text)


# --------------------------------------------------------------------------- protection
OPAQUE = ("begin", "end", "label", "ref", "cref", "Cref", "autoref", "cite", "citep", "citet",
          "input", "include", "bibliographystyle", "bibliography", "usepackage", "documentclass",
          "newcommand", "renewcommand", "newenvironment", "newtheorem", "definecolor", "color",
          "hypersetup", "titleformat", "titlespacing", "setlist", "captionsetup",
          "usetikzlibrary", "texttt", "url", "href", "includegraphics", "DeclareMathOperator",
          "newcolumntype", "pagestyle", "geometry", "numberwithin", "theoremstyle",
          "setlength", "addtolength")

MATHENV = ("equation", "equation*", "align", "align*", "gather", "gather*", "multline",
           "multline*", "eqnarray", "split", "array", "cases", "tikzpicture", "verbatim")


def protect_blocks(txt):
    """Stash multi-line math and picture environments BEFORE any line-wise work: a line-wise
    protector cannot see a display-math opener whose closer is on another line."""
    store = []

    def stash(m):
        store.append(m.group(0))
        return "\x01%d\x01" % (len(store) - 1)

    txt = re.sub(r"\\\[.*?\\\]", stash, txt, flags=re.S)
    for e in MATHENV:
        txt = re.sub(r"\\begin\{" + re.escape(e) + r"\}.*?\\end\{" + re.escape(e) + r"\}",
                     stash, txt, flags=re.S)
    return txt, store


def protect_and_map(line):
    store, out, i, n = [], [], 0, len(line)

    def stash(s):
        store.append(s)
        return "\x00%d\x00" % (len(store) - 1)

    while i < n:
        c = line[i]
        if c == "%" and (i == 0 or line[i - 1] != "\\"):
            out.append(stash(line[i:]))
            break
        if line.startswith("\\[", i) or line.startswith("\\(", i):
            close = "\\]" if line.startswith("\\[", i) else "\\)"
            j = line.find(close, i + 2)
            j = n if j < 0 else j + 2
            out.append(stash(line[i:j]))
            i = j
            continue
        if c == "$":
            j = i + 1
            while j < n and not (line[j] == "$" and line[j - 1] != "\\"):
                j += 1
            j = min(j + 1, n)
            out.append(stash(line[i:j]))
            i = j
            continue
        if c == "\\":
            m = re.match(r"\\([A-Za-z@]+|.)", line[i:])
            cs, name = m.group(0), m.group(1)
            j = i + len(cs)
            if name in OPAQUE:
                while j < n and line[j] in "[{":
                    d, k = 0, j
                    while k < n:
                        if line[k] in "[{":
                            d += 1
                        elif line[k] in "]}":
                            d -= 1
                            if d == 0:
                                k += 1
                                break
                        k += 1
                    j = k
                out.append(stash(line[i:j]))
                i = j
                continue
            out.append(stash(cs))
            i = j
            continue
        out.append(c)
        i += 1
    body = bionic_words("".join(out))
    for idx, s_ in enumerate(store):
        body = body.replace("\x00%d\x00" % idx, s_)
    return body


def process(txt):
    txt, store = protect_blocks(txt)
    txt = "\n".join(protect_and_map(l) for l in txt.split("\n"))
    for i, s_ in enumerate(store):
        txt = txt.replace("\x01%d\x01" % i, s_)
    return txt


# --------------------------------------------------------------------------- build
FILES = ["partA_concept.tex", "partB_object_problems.tex", "partm1_notation.tex",
         "part0_math.tex", "part0b_worked.tex", "part1_object.tex", "part1b_toy.tex",
         "part3_gaps.tex", "part2_estimators.tex"]
# pgfkeys style definitions look like prose to a regex and are not; the safe subset was
# smaller than the file, so it is copied whole.
VERBATIM = ["evidence_firewall.tex"]

MACROS = ("\n%% ---- bionic reading; policy from reader/assets/core/core.js ----\n"
          "\\definecolor{BioInk}{HTML}{" + INK + "}\n"
          "\\definecolor{BioRest}{HTML}{" + REST + "}\n"
          "\\definecolor{BioFade}{HTML}{" + FADE + "}\n"
          "\\newcommand{\\bi}[2]{{\\bfseries\\color{BioInk}#1}{\\color{BioRest}#2}}\n"
          "\\newcommand{\\bfade}[1]{{\\color{BioFade}#1}}\n")


def main():
    OUT.mkdir(exist_ok=True)
    freq_scan([(SRC / f).read_text() for f in FILES])
    for f in FILES:
        (OUT / f).write_text(process((SRC / f).read_text()))
    for f in VERBATIM:
        (OUT / f).write_text((SRC / f).read_text())
    (OUT / "preamble.tex").write_text((SRC / "preamble.tex").read_text() + MACROS)
    mt = (SRC / "main.tex").read_text()
    keep, body = mt.split("\\begin{document}", 1)
    (OUT / "main.tex").write_text(keep + "\\begin{document}" + process(body))
    fn = sorted((w for w in FREQ if is_function_word(w, len(w))),
                key=lambda w: -FREQ[w])
    print("vocabulary %d | treated as function words %d" % (len(FREQ), len(fn)))
    print("top 25 receding whole:", " ".join(fn[:25]))


if __name__ == "__main__":
    sys.exit(main())
