def make_ngrams(word, min_size=3):
    """
    basestring       word: word to split into ngrams
           int   min_size: minimum size of ngrams
    """
    length = len(word)
    size_range = range(min_size, max(length, min_size) + 1)
    return list(set(
        word[i:i + size]
        for size in size_range
        for i in range(0, max(0, length - size) + 1)
    ))

def index_for_search(collection, show):
    collection.update(
        {
            "id": show["id"],
        },
        {
            "$set": {
                "ngrams": u' '.join(
                    make_ngrams(str(show["name"]), min_size=3)
                ),
            },
        },
        upsert=True,
    )