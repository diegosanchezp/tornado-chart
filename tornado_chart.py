from os import getenv
from typing import Dict, Any, TypeVar
from shimoku_api_python import Client
import pandas as pd
import numpy as np

KeyType = TypeVar('KeyType')
def deep_update(mapping: Dict[KeyType, Any], *updating_mappings: Dict[KeyType, Any]) -> Dict[KeyType, Any]:
    """
    Updates a nested dictionary
    """

    # https://github.com/pydantic/pydantic/blob/fd2991fe6a73819b48c906e3c3274e8e47d0f761/pydantic/utils.py#L200
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v, dict):
                updated_mapping[k] = deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping

# Default echarts options for tornado
pos_dataops_org = {
    'label': {
        'position': 'right',
    },
    'itemStyle': {
        'color': 'var(--chart-C2)',
        'borderRadius': [0, 9, 9, 0],
    },
    'emphasis': {
        'itemStyle': {
            'color': 'var(--chart-C2)',
            'borderColor': 'var(--chart-C2)',
        }
    },
}

neg_dataops_org = {
    'label': {
        'position': 'left',
    },
    'itemStyle': {
        'color': 'var(--complementary-red-light)',
        'borderRadius': [9, 0, 0, 9],
    },
    'emphasis': {
        'itemStyle': {
            'color': 'var(--complementary-red-light)',
            'borderColor': 'var(--complementary-red-light)',
        }
    },
}

options_org = {
    'toolbox': {
        'right': 10,
        'feature': {
            'saveAsImage': {},
            'dataView': {},
        }
    },
    'tooltip': {
        'trigger': 'axis',
        'axisPointer': {
            'type': 'shadow'
        }
    },
    'grid': {
        'top': 80,
        'bottom': 30
    },
    'xAxis': {
        'type': 'value',
        'axisLine': { 'show': False },
        'position': 'top',
        'axisLabel': { 'show': False },
        'splitLine': {
            'show': False,
        }
    },
    'yAxis': {
        'type': 'category',
        'axisLine': { 'show': True },
        'axisLabel': { 'show': False },
        'axisTick': { 'show': False },
        'splitLine': { 'show': False },
    },
};

seriesopt_org = {
    'name': 'Revenue',
    'type': 'bar',
    'stack': 'Total',
    'smooth': True,
    'label': {
        'show': True,
        'width': 270,
        'overflow': 'truncate',
        'formatter': '{b}\n{c}',
    },
}

def tornado(
    shimoku,
    menupath: str,
    order: int,
    df_neg: pd.DataFrame, df_pos: pd.DataFrame,
    cols_size=12,
    rows_size=5,
    neg_col_val = "value", pos_col_val = "value",
    neg_col_name = "name", pos_col_name = "name",
    options_mod = {}, neg_dataops_mod = {},
    pos_dataops_mod = {}, seriesopt_mod = {},
):
    """
    Plot a Tornado chart
    - options_mod: level 1 echarts options
    https://echarts.apache.org/en/option.html

    - for pos_dataops_mod and neg_dataops_mod, see
    https://echarts.apache.org/en/option.html#series-bar.data

    - for seriesopt_mod see
    https://echarts.apache.org/en/option.html#series-bar.type
    """

    options = deep_update(options_org, options_mod)
    pos_dataops = deep_update(pos_dataops_org,pos_dataops_mod)
    neg_dataops = deep_update(neg_dataops_org, neg_dataops_mod)
    series = deep_update(seriesopt_org, seriesopt_mod)

    series_data_neg = [{
        'value': val,
        **neg_dataops,
    } for val in list(df_neg[neg_col_val])]

    series_data_pos = [{
        'value': val,
        **pos_dataops,
    } for val in list(df_pos[pos_col_val])]

    y_data = list(df_neg[neg_col_name]) + list(df_pos[pos_col_name])
    options['yAxis']['data'] = y_data

    series_data = series_data_neg + series_data_pos
    series['data'] = series_data
    options['series'] = [
        series
    ]

    shimoku.plt.free_echarts(
        data=df_neg[:1], # Dummy data
        options=options,
        order=order,
        menu_path=menupath,
        cols_size=cols_size,
        rows_size=rows_size,
    )


def gen_rand_df(product_names, neg=False):
    """
    Generate random data for testing
    """
    df_size = 10
    rng = np.random.default_rng()

    values = rng.uniform(low=10, high=30, size=df_size)
    if neg:
        values = -1*values

    return pd.DataFrame({
        'value': values,
        'name': product_names,
    })

if __name__ == "__main__":

    product_names = ["Cheeseburger", "Fried Chicken", "Pasta Carbonara", "Caesar Salad", "Fish and Chips",
                 "Beef Stroganoff", "Pizza Margherita", "Grilled Salmon", "Taco Salad", "Crispy Calamari",
                 "Shrimp Scampi", "Garlic Bread", "Sizzling Fajitas", "Chicken Teriyaki", "French Onion Soup",
                 "Miso Ramen", "Crab Cakes", "Lobster Bisque", "Crispy Tofu Bowl", "Philly Cheesesteak",]
    # Random data
    df_pos = gen_rand_df(product_names[:10])
    df_neg = gen_rand_df(product_names[10:20], neg=True)

    # Plot
    shimoku = Client(
        universe_id=getenv('UNIVERSE_ID'),
        access_token=getenv('API_TOKEN'),
        business_id=getenv('BUSINESS_ID'),
        verbosity='INFO',
        async_execution=True,
    )

    tornado(
        shimoku,
        df_neg=df_neg, df_pos=df_pos,
        neg_dataops_mod={
            'itemStyle': {
                'color': 'blue',
            },
        },
        order=0, menupath='Tornado'
    )

    # Async execution
    shimoku.activate_async_execution()
    shimoku.run()
