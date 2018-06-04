import pandas as pd

prediction_raw = dict()
for dict0 in pop_prediction_raw.values():
    for key1, dict1 in dict0.items():
        for key2, val2 in dict1.items():
            feature_name = '{}.{}'.format(key1,key2)
            prediction_raw[feature_name] = val2

prediction_raw_df = pd.DataFrame(prediction_raw)
