def get_terms_for_table():
    terms = []
    with open("./data/word_dict.csv", "r", encoding="utf-8") as f:
        cnt = 1
        for line in f.readlines()[1:]:
            term, pinyin, definition, source = line.split(";")
            terms.append([cnt, term, pinyin, definition])
            cnt += 1
    return terms