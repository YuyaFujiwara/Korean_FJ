import re

# Utilities: Hangul romanization (basic Revised Romanization)
L_TABLE = ["g","kk","n","d","tt","r","m","b","pp","s","ss","","j","jj","ch","k","t","p","h"]
V_TABLE = ["a","ae","ya","yae","eo","e","yeo","ye","o","wa","wae","oe","yo","u","wo","we","wi","yu","eu","ui","i"]
T_TABLE = ["", "k","kk","ks","n","nj","nh","t","l","lk","lm","lb","ls","lt","lp","lh","m","p","ps","t","t","ng","t","t","k","t","p","t"]

# Utilities: Hangul composition (minimal on-screen keyboard support)
L_JAMO = ["ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ","ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"]
V_JAMO = ["ㅏ","ㅐ","ㅑ","ㅒ","ㅓ","ㅔ","ㅕ","ㅖ","ㅗ","ㅘ","ㅙ","ㅚ","ㅛ","ㅜ","ㅝ","ㅞ","ㅟ","ㅠ","ㅡ","ㅢ","ㅣ"]
T_JAMO = ["", "ㄱ","ㄲ","ㄳ","ㄴ","ㄵ","ㄶ","ㄷ","ㄹ","ㄺ","ㄻ","ㄼ","ㄽ","ㄾ","ㄿ","ㅀ","ㅁ","ㅂ","ㅄ","ㅅ","ㅆ","ㅇ","ㅈ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"]

L_INDEX = {j: i for i, j in enumerate(L_JAMO)}
V_INDEX = {j: i for i, j in enumerate(V_JAMO)}
T_INDEX = {j: i for i, j in enumerate(T_JAMO)}

L_DOUBLE = {
    ("ㄱ", "ㄱ"): "ㄲ",
    ("ㄷ", "ㄷ"): "ㄸ",
    ("ㅂ", "ㅂ"): "ㅃ",
    ("ㅅ", "ㅅ"): "ㅆ",
    ("ㅈ", "ㅈ"): "ㅉ",
}

V_COMBINE = {
    ("ㅗ", "ㅏ"): "ㅘ",
    ("ㅗ", "ㅐ"): "ㅙ",
    ("ㅗ", "ㅣ"): "ㅚ",
    ("ㅜ", "ㅓ"): "ㅝ",
    ("ㅜ", "ㅔ"): "ㅞ",
    ("ㅜ", "ㅣ"): "ㅟ",
    ("ㅡ", "ㅣ"): "ㅢ",
}

V_SPLIT = {
    "ㅘ": "ㅗ",
    "ㅙ": "ㅗ",
    "ㅚ": "ㅗ",
    "ㅝ": "ㅜ",
    "ㅞ": "ㅜ",
    "ㅟ": "ㅜ",
    "ㅢ": "ㅡ",
}

T_COMBINE = {
    ("ㄱ", "ㅅ"): "ㄳ",
    ("ㄴ", "ㅈ"): "ㄵ",
    ("ㄴ", "ㅎ"): "ㄶ",
    ("ㄹ", "ㄱ"): "ㄺ",
    ("ㄹ", "ㅁ"): "ㄻ",
    ("ㄹ", "ㅂ"): "ㄼ",
    ("ㄹ", "ㅅ"): "ㄽ",
    ("ㄹ", "ㅌ"): "ㄾ",
    ("ㄹ", "ㅍ"): "ㄿ",
    ("ㄹ", "ㅎ"): "ㅀ",
    ("ㅂ", "ㅅ"): "ㅄ",
}

T_SPLIT = {v: k for k, v in T_COMBINE.items()}


def compose_hangul(l_jamo: str, v_jamo: str, t_jamo=None) -> str:
    l = L_INDEX.get(l_jamo)
    v = V_INDEX.get(v_jamo)
    t = T_INDEX.get(t_jamo or "")
    if l is None or v is None or t is None:
        return ""
    return chr(0xAC00 + (l * 21 + v) * 28 + t)


def hangul_to_rr(text: str) -> str:
    out = []
    for ch in text.strip():
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            s = code - 0xAC00
            l = s // 588
            v = (s % 588) // 28
            t = s % 28
            out.append(L_TABLE[l] + V_TABLE[v] + T_TABLE[t])
        else:
            out.append(ch)
    return "".join(out)


def norm_answer(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[\s\-\_\'\"\.]", "", s)
    return s