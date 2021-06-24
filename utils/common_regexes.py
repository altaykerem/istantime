# ############ Numbers ############
NATURAL_NUMBERS = r"(?:[1-9][0-9]*)"
INTEGER_NUMBERS = r"-?[0-9]+"
DOT_SEPARATED_NUMBERS = r"[1-9]{1,2}(?:\.[0-9]{3})*"

# Cases of rational numbers, ex: -3.4, 1/4, .2, 4., 3,4
DOUBLE_NUMBERS = r"-?(?:(?:[0-9]*[,\.][0-9]+)|(?:[0-9]+[,\.][0-9]*))"
FRACTIONAL_NUMBERS = r"{}/{}".format(INTEGER_NUMBERS, NATURAL_NUMBERS)

NUMBERS = r'(?:(?:{})|(?:{})|(?:{})|(?:{}))'.format(INTEGER_NUMBERS, DOUBLE_NUMBERS,
                                                    FRACTIONAL_NUMBERS, DOT_SEPARATED_NUMBERS)
NUMBER_TEXTS = r'(?:bir|iki|üç|dört|beş|altı|yedi|sekiz|dokuz|on|sıfır|yirmi|otuz|kırk|elli|altmış|yetmiş|' \
               r'seksen|doksan|yüz|bin|milyon|milyar|trilyon|katrilyon)'

ALL_NUMBERS = r'(?:(?:{}|{})+)'.format(NUMBERS, NUMBER_TEXTS)

# ############ Turkish Language ############
# kaynastirma ünsüzleri
INCLUSIVE_CONSONANTS = "[yşsn]"

# suffixes
# Belirtme durum ekleri -> (i, ı, u, ü); example -> ayın 4ü
# Yönelme durum eki -> (y?e, y?a); example -> sabaha bana para yolla, salıya yolla, ayın 6sına
# Bulunma durumu eki -> (de, da, te, ta); example -> martta mali durumum nasıldı
# Ayrılma durumu eki -> (den ,dan, ten, tan); example -> ocaktan hazirana kadar harcamalarımı göster
# Tamlama ekleri -> (ın, in, un, ün); example -> ocağın
# ki, ti yapım ekleri; example ocak-ta-ki, dünkü, bu yılki, duvardaki
CASE_SUFFIXES = r"['\.\"]?{}?(?: ?(?:[dt][ea](?:(?:n)|(?:k[iı]))?)" \
                r"|(?:[iıuü]?nd[ae]n?)|(?: ?[ae])|(?: ?[iıuü]n?))".format(INCLUSIVE_CONSONANTS)
POSSESSIVE_SUFFIXES = r"[ıiuü]"
PRONOUN_SUFFIX = r"(?:[dt][ea])?k[iü]"
PLURALITY_SUFFIXES = r"l[ae]r"
GENITIVE_SUFFIXES = r"(?:{}?[ıiuü]n)".format(INCLUSIVE_CONSONANTS)
COMPLEMENTARY_VERB_SUFFIX = r"(?:idi)|(?:imiş)|(?:dir)"
EQUALITY_SUFFIX = r"c[ae]"
TRANSITIVE_SUFFIX = r"l[ae]"

# conjunctions
# ve, ile, -le,-y?l[ae]
# -ıp, -erek, -arak
# veya, ya da, yahut, veyahut
# ama, fakat, lakin
# yalnız, ancak, oysa, oysa ?ki, halbuki, ne var ki
# çünkü, zira
# de, da, ki, madem, mademki, demek, demek ki, üstelik, hatta, yani
# (ne|hem|kah|gah|ister) x (ne|hem|kah|gah|ister)( de)? y
CONJUNCTIONS = r"(?:(?: ve )|(?: ile )|(?:[y']?l[ae] ))"

SIRA_SAYI_SIFATILARI = r"[ıiuü]?nc[ıiuü]"
