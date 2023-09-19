from parsers import NewsAm, MamulAm, TertAm
import json
import pickle


if __name__ == "__main__":
        # ns = NewsAm(regions=['armenia'], categories=['politics', 'society', 'economics'], start_date='16/08/2023', end_date='16/09/2023')
        # ns_parsed = ns.Parse()
        #
        # ns_parsed.save('/home/laptop/Desktop/ns_parsed.pkl')

        ml = MamulAm( categories=['քաղաքականություն', 'տնտեսություն', 'հասարակություն'], n_pages=3)
        ml_parsed = ml.Parse()

        ml_parsed.save('/home/laptop/Desktop/ml_parsed.pkl')

        # tr = TertAm(categories=['politics', 'business'], n_pages=4)
        # tr_parsed = tr.Parse()
        #
        # tr_parsed.save('/home/laptop/Desktop/tr_parsed.pkl')
        #
        # total_parsed = ns_parsed + ml_parsed + tr_parsed

        with open('/home/laptop/Desktop/ml_parsed.pkl', 'rb') as f:
                parsed = pickle.load(f)

        print(parsed.to_list())





