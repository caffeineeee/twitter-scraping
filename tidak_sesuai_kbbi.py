from place_lists_here import terimakasih_kata_dasar_tidak_sesuai_kbbi, sapaan_kata_dasar

# TODO: if interested, continue this so it becomes available as a Python package (in PyPI, etc.)

alfabet = "abcdefghijklmnopqrstuvwxyz"

terimakasih = (  # this is the final list
    [string for string in terimakasih_kata_dasar_tidak_sesuai_kbbi]  # e.g. trims
    + [
        string + letter
        for string in terimakasih_kata_dasar_tidak_sesuai_kbbi
        for letter in alfabet
    ]  # e.g. trims + x
    + [
        letter + string
        for letter in alfabet
        for string in terimakasih_kata_dasar_tidak_sesuai_kbbi
    ]  # e.g. x + trims
    + [
        letter + string + letter  # e.g. x + trims + x
        for string in terimakasih_kata_dasar_tidak_sesuai_kbbi
        for letter in alfabet
    ]
)

sapaan = (  # this is the final list
    [string for string in sapaan_kata_dasar]  # e.g. bro
    + [
        string + letter for string in sapaan_kata_dasar for letter in alfabet
    ]  # e.g. bro + x
    + [
        letter + string for letter in alfabet for string in sapaan_kata_dasar
    ]  # e.g. x + bro
    + [
        letter + string + letter  # e.g. x + bro + x
        for string in sapaan_kata_dasar
        for letter in alfabet
    ]
)
