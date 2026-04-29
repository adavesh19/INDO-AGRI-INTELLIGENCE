# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 21:46:27 2019

@author: PRATYUSH, Rahul, Somya, Abhay
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS, cross_origin
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import requests
import crops
import random
import io
import json
import os
from functools import lru_cache

# import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/ticker": {"origins": "http://localhost:port"}})

commodity_dict = {
    "arhar": "static/Arhar.csv",
    "bajra": "static/Bajra.csv",
    "barley": "static/Barley.csv",
    "copra": "static/Copra.csv",
    "cotton": "static/Cotton.csv",
    "sesamum": "static/Sesamum.csv",
    "gram": "static/Gram.csv",
    "groundnut": "static/Groundnut.csv",
    "jowar": "static/Jowar.csv",
    "maize": "static/Maize.csv",
    "masoor": "static/Masoor.csv",
    "moong": "static/Moong.csv",
    "niger": "static/Niger.csv",
    "paddy": "static/Paddy.csv",
    "ragi": "static/Ragi.csv",
    "rape": "static/Rape.csv",
    "jute": "static/Jute.csv",
    "safflower": "static/Safflower.csv",
    "soyabean": "static/Soyabean.csv",
    "sugarcane": "static/Sugarcane.csv",
    "sunflower": "static/Sunflower.csv",
    "urad": "static/Urad.csv",
    "wheat": "static/Wheat.csv"
}

annual_rainfall = [29, 21, 37.5, 30.7, 52.6, 150, 299, 251.7, 179.2, 70.5, 39.8, 10.9]
base = {
    "Paddy": 1245.5,
    "Arhar": 3200,
    "Bajra": 1175,
    "Barley": 980,
    "Copra": 5100,
    "Cotton": 3600,
    "Sesamum": 4200,
    "Gram": 2800,
    "Groundnut": 3700,
    "Jowar": 1520,
    "Maize": 1175,
    "Masoor": 2800,
    "Moong": 3500,
    "Niger": 3500,
    "Ragi": 1500,
    "Rape": 2500,
    "Jute": 1675,
    "Safflower": 2500,
    "Soyabean": 2200,
    "Sugarcane": 2250,
    "Sunflower": 3700,
    "Urad": 4300,
    "Wheat": 1350

}
commodity_list = []


class Commodity:

    def __init__(self, csv_name):
        self.name = csv_name
        dataset = pd.read_csv(csv_name)
        self.X = dataset.iloc[:, :-1].values
        self.Y = dataset.iloc[:, 3].values

        #from sklearn.model_selection import train_test_split
        #X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.1, random_state=0)

        # Fitting decision tree regression to dataset
        from sklearn.tree import DecisionTreeRegressor
        self.regressor = DecisionTreeRegressor(max_depth=12, random_state=42)
        self.regressor.fit(self.X, self.Y)
        #y_pred_tree = self.regressor.predict(X_test)
        # fsa=np.array([float(1),2019,45]).reshape(1,3)
        # fask=regressor_tree.predict(fsa)

    def getPredictedValue(self, value):
        if value[1]>=2019:
            fsa = np.array(value).reshape(1, 3)
            #print(" ",self.regressor.predict(fsa)[0])
            return self.regressor.predict(fsa)[0]
        else:
            c=self.X[:,0:2]
            x=[]
            for i in c:
                x.append(i.tolist())
            fsa = [value[0], value[1]]
            ind = 0
            for i in range(0,len(x)):
                if x[i]==fsa:
                    ind=i
                    break
            #print(index, " ",ind)
            #print(x[ind])
            #print(self.Y[i])
            return self.Y[i]

    def getCropName(self):
        a = self.name.split('.')
        return a[0]

    def __str__(self):
        return self.getCropName().split('/')[-1].lower()


LOCATION_MARKETS = {
    "Karnataka": {
        "Bengaluru Rural": {
            "Devanahalli": ["ragi", "maize", "paddy", "groundnut", "sunflower", "tomato", "onion", "chilli"],
            "Doddaballapura": ["ragi", "maize", "groundnut", "cotton", "jowar", "turmeric"],
            "Nelamangala": ["ragi", "paddy", "gram", "moong", "vegetables"]
        },
        "Mysuru": {
            "Nanjangud": ["paddy", "sugarcane", "ragi", "maize", "banana"],
            "Hunsur": ["tobacco", "maize", "ragi", "cotton", "ginger"],
            "T. Narasipura": ["paddy", "sugarcane", "sesamum", "groundnut"]
        },
        "Belagavi": {
            "Gokak": ["sugarcane", "maize", "soyabean", "jowar", "cotton"],
            "Athani": ["jowar", "wheat", "gram", "sunflower", "groundnut"],
            "Chikodi": ["sugarcane", "maize", "soyabean", "turmeric"]
        }
    },
    "Maharashtra": {
        "Pune": {
            "Haveli": ["jowar", "wheat", "sugarcane", "gram", "onion"],
            "Baramati": ["sugarcane", "maize", "soyabean", "groundnut", "grapes"],
            "Indapur": ["jowar", "bajra", "gram", "cotton", "pomegranate"]
        },
        "Nagpur": {
            "Katol": ["cotton", "soyabean", "arhar", "gram", "orange"],
            "Umred": ["paddy", "cotton", "soyabean", "jowar"],
            "Hingna": ["cotton", "soyabean", "wheat", "gram"]
        },
        "Nashik": {
            "Niphad": ["onion", "wheat", "gram", "maize", "grapes"],
            "Sinnar": ["bajra", "jowar", "onion", "soyabean"],
            "Dindori": ["grapes", "paddy", "nagali", "vegetables"]
        }
    },
    "Tamil Nadu": {
        "Thanjavur": {
            "Kumbakonam": ["paddy", "sugarcane", "blackgram", "sesamum"],
            "Papanasam": ["paddy", "urad", "groundnut", "banana"],
            "Orathanadu": ["paddy", "maize", "groundnut", "sesamum"]
        },
        "Coimbatore": {
            "Pollachi": ["coconut", "copra", "maize", "groundnut", "banana"],
            "Mettupalayam": ["vegetables", "maize", "cotton", "turmeric"],
            "Sulur": ["maize", "cotton", "groundnut", "jowar"]
        },
        "Madurai": {
            "Melur": ["paddy", "groundnut", "cotton", "sesamum"],
            "Usilampatti": ["jowar", "bajra", "cotton", "gram"],
            "Vadipatti": ["paddy", "sugarcane", "banana", "maize"]
        }
    },
    "Uttar Pradesh": {
        "Meerut": {
            "Sardhana": ["sugarcane", "wheat", "paddy", "barley", "mustard"],
            "Mawana": ["sugarcane", "wheat", "gram", "paddy"],
            "Daurala": ["sugarcane", "wheat", "maize", "potato"]
        },
        "Varanasi": {
            "Pindra": ["paddy", "wheat", "arhar", "gram", "vegetables"],
            "Rohaniya": ["paddy", "wheat", "mustard", "masoor"],
            "Sevapuri": ["paddy", "wheat", "moong", "arhar"]
        },
        "Lakhimpur Kheri": {
            "Gola Gokarannath": ["sugarcane", "paddy", "wheat", "mustard"],
            "Nighasan": ["paddy", "wheat", "sugarcane", "maize"],
            "Palia": ["paddy", "sugarcane", "wheat", "gram"]
        }
    },
    "Punjab": {
        "Ludhiana": {
            "Samrala": ["wheat", "paddy", "maize", "barley"],
            "Jagraon": ["wheat", "paddy", "cotton", "gram"],
            "Khanna": ["wheat", "paddy", "mustard", "maize"]
        },
        "Amritsar": {
            "Ajnala": ["wheat", "paddy", "maize", "barley"],
            "Baba Bakala": ["wheat", "paddy", "gram", "mustard"],
            "Majitha": ["wheat", "paddy", "vegetables", "maize"]
        }
    },
    "Gujarat": {
        "Rajkot": {
            "Gondal": ["groundnut", "cotton", "sesamum", "wheat", "cumin"],
            "Jetpur": ["cotton", "groundnut", "jowar", "castor"],
            "Dhoraji": ["groundnut", "cotton", "wheat", "gram"]
        },
        "Ahmedabad": {
            "Daskroi": ["cotton", "wheat", "jowar", "groundnut"],
            "Dholka": ["cotton", "wheat", "gram", "sesamum"],
            "Sanand": ["cotton", "wheat", "castor", "maize"]
        }
    },
    "Madhya Pradesh": {
        "Indore": {
            "Mhow": ["soyabean", "wheat", "gram", "maize"],
            "Depalpur": ["soyabean", "wheat", "cotton", "gram"],
            "Sanwer": ["soyabean", "wheat", "maize", "arhar"]
        },
        "Sehore": {
            "Ashta": ["soyabean", "wheat", "gram", "masoor"],
            "Ichhawar": ["soyabean", "wheat", "maize", "arhar"],
            "Budni": ["wheat", "gram", "soyabean", "paddy"]
        }
    },
    "Rajasthan": {
        "Jaipur": {
            "Chomu": ["bajra", "wheat", "barley", "gram", "mustard"],
            "Sanganer": ["bajra", "wheat", "gram", "vegetables"],
            "Kotputli": ["bajra", "wheat", "mustard", "barley"]
        },
        "Jodhpur": {
            "Osian": ["bajra", "moong", "moth", "sesamum"],
            "Bilara": ["bajra", "wheat", "gram", "cumin"],
            "Phalodi": ["bajra", "moong", "sesamum", "guar"]
        }
    }
}

DISPLAY_COMMODITIES = [
    "arhar", "bajra", "barley", "copra", "cotton", "sesamum", "gram", "groundnut",
    "jowar", "maize", "masoor", "moong", "niger", "paddy", "ragi", "rape", "jute",
    "safflower", "soyabean", "sugarcane", "sunflower", "urad", "wheat", "onion",
    "tomato", "potato", "turmeric", "chilli", "coconut", "banana", "mustard", "cumin",
    "castor", "ginger", "blackgram", "vegetables", "grapes", "orange", "pomegranate"
]

STATE_CROP_PROFILES = {
    "Andhra Pradesh": ["paddy", "maize", "groundnut", "cotton", "chilli", "turmeric", "sugarcane"],
    "Arunachal Pradesh": ["paddy", "maize", "millets", "ginger", "vegetables"],
    "Assam": ["paddy", "jute", "maize", "sesamum", "mustard", "vegetables"],
    "Bihar": ["paddy", "wheat", "maize", "arhar", "gram", "potato"],
    "Chhattisgarh": ["paddy", "maize", "arhar", "moong", "sesamum"],
    "Delhi": ["wheat", "mustard", "vegetables", "paddy"],
    "Goa": ["paddy", "ragi", "coconut", "vegetables"],
    "Gujarat": ["cotton", "groundnut", "sesamum", "wheat", "jowar", "cumin", "castor"],
    "Haryana": ["wheat", "paddy", "mustard", "barley", "cotton", "sugarcane"],
    "Himachal Pradesh": ["maize", "wheat", "barley", "gram", "vegetables"],
    "Jammu And Kashmir": ["paddy", "maize", "wheat", "barley", "safflower"],
    "Jharkhand": ["paddy", "maize", "arhar", "moong", "sesamum"],
    "Karnataka": ["ragi", "jowar", "maize", "paddy", "groundnut", "sunflower", "cotton"],
    "Kerala": ["paddy", "copra", "coconut", "banana", "vegetables"],
    "Madhya Pradesh": ["soyabean", "wheat", "gram", "masoor", "maize", "cotton"],
    "Maharashtra": ["cotton", "soyabean", "jowar", "sugarcane", "groundnut", "onion", "turmeric"],
    "Manipur": ["paddy", "maize", "ginger", "vegetables"],
    "Meghalaya": ["paddy", "maize", "ginger", "turmeric", "vegetables"],
    "Mizoram": ["paddy", "maize", "ginger", "turmeric", "vegetables"],
    "Nagaland": ["paddy", "maize", "ginger", "vegetables"],
    "Odisha": ["paddy", "jute", "arhar", "moong", "sesamum", "groundnut"],
    "Punjab": ["wheat", "paddy", "maize", "barley", "cotton", "mustard"],
    "Rajasthan": ["bajra", "wheat", "barley", "gram", "mustard", "moong", "sesamum"],
    "Sikkim": ["maize", "paddy", "ginger", "vegetables"],
    "Tamil Nadu": ["paddy", "groundnut", "cotton", "sesamum", "sugarcane", "copra"],
    "Telangana": ["paddy", "maize", "cotton", "groundnut", "turmeric", "chilli"],
    "Tripura": ["paddy", "jute", "maize", "vegetables"],
    "Uttar Pradesh": ["sugarcane", "wheat", "paddy", "potato", "arhar", "gram", "mustard"],
    "Uttarakhand": ["wheat", "paddy", "maize", "barley", "gram"],
    "West Bengal": ["paddy", "jute", "potato", "mustard", "moong", "vegetables"],
}


def normalise_crop_name(name):
    aliases = {
        "mustard": "rape", "blackgram": "urad", "coconut": "copra", "nagali": "ragi", "millets": "ragi",
        "moth": "moong", "guar": "gram", "tobacco": "cotton", "banana": "paddy",
        "onion": "maize", "tomato": "maize", "potato": "wheat", "turmeric": "sesamum",
        "chilli": "sesamum", "cumin": "niger", "castor": "groundnut", "ginger": "ragi",
        "vegetables": "maize", "grapes": "paddy", "orange": "cotton", "pomegranate": "jowar"
    }
    name_l = (name or "").lower()
    return aliases.get(name_l, name_l)


def get_commodity(name):
    model_name = normalise_crop_name(name)
    for commodity in commodity_list:
        if str(commodity) == model_name:
            return commodity, model_name
    return commodity_list[0], "arhar"


@lru_cache(maxsize=4096)
def predicted_price_for(name, month, year):
    commodity, model_name = get_commodity(name)
    base_name = model_name.capitalize()
    base_price = base.get(base_name, 1600)
    rain = annual_rainfall[month - 1]
    wpi = commodity.getPredictedValue([float(month), year, rain])
    return round((wpi * base_price) / 100, 2)


def market_series(name):
    now = datetime.now()
    past = []
    for offset in range(11, -1, -1):
        dt = now.replace(day=1) - pd.DateOffset(months=offset)
        past.append({"label": dt.strftime("%b %y"), "price": predicted_price_for(name, int(dt.month), int(dt.year))})

    present_price = predicted_price_for(name, now.month, now.year)

    future = []
    for offset in range(1, 13):
        dt = now.replace(day=1) + pd.DateOffset(months=offset)
        future.append({"label": dt.strftime("%b %y"), "price": predicted_price_for(name, int(dt.month), int(dt.year))})

    combined = past + [{"label": now.strftime("%b %y"), "price": present_price}] + future
    high = max(combined, key=lambda item: item["price"])
    low = min(combined, key=lambda item: item["price"])
    avg_future = round(sum(item["price"] for item in future) / len(future), 2)
    change = round(((future[-1]["price"] - present_price) / present_price) * 100, 2) if present_price else 0
    return {
        "past": past,
        "present": {"label": now.strftime("%d %b %Y"), "price": present_price},
        "future": future,
        "high": high,
        "low": low,
        "avg_future": avg_future,
        "change": change,
        "model_crop": normalise_crop_name(name)
    }


@lru_cache(maxsize=1)
def state_districts_catalog():
    data_path = os.path.join(app.root_path, "static", "india-state-district.json")
    grouped = {}
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as handle:
            for row in json.load(handle):
                state = row.get("StateName")
                district = row.get("DistrictName(InEnglish)")
                if state and district:
                    grouped.setdefault(state, set()).add(district)
    for state, districts in LOCATION_MARKETS.items():
        grouped.setdefault(state, set()).update(districts.keys())
    return {state: sorted(districts) for state, districts in sorted(grouped.items())}


def generated_taluks(state, district):
    known = LOCATION_MARKETS.get(state, {}).get(district, {})
    if known:
        return sorted(known.keys())
    base_name = district.replace(" District", "").replace("Urban", "").strip()
    return [
        f"{base_name} Sadar",
        f"{base_name} North",
        f"{base_name} South",
        f"{base_name} Rural",
        f"{base_name} Market Yard",
        f"{base_name} Agro Block",
    ]


def crops_for_region(state, district, taluk):
    known = LOCATION_MARKETS.get(state, {}).get(district, {}).get(taluk)
    if known:
        return known
    profile = STATE_CROP_PROFILES.get(state, ["paddy", "wheat", "maize", "gram", "groundnut", "vegetables"])
    district_shift = sum(ord(ch) for ch in (district or "")) % len(DISPLAY_COMMODITIES)
    extras = DISPLAY_COMMODITIES[district_shift:district_shift + 8]
    return list(dict.fromkeys(profile + extras))[:14]


def location_factor(state, district, taluk, crop):
    seed = sum(ord(ch) for ch in f"{state}|{district}|{taluk}|{crop}")
    local = crop.lower() in [c.lower() for c in crops_for_region(state, district, taluk)]
    mandi_depth = 1 + ((seed % 17) - 8) / 100
    local_bonus = 1.045 if local else .985
    volatility = 1 + (((seed // 7) % 9) - 4) / 100
    return round(mandi_depth * local_bonus * volatility, 4)


def adjusted_market_series(name, state, district, taluk):
    series = market_series(name)
    factor = location_factor(state, district, taluk, name)
    for bucket in ["past", "future"]:
        for item in series[bucket]:
            item["price"] = round(item["price"] * factor, 2)
    series["present"]["price"] = round(series["present"]["price"] * factor, 2)
    combined = series["past"] + [series["present"]] + series["future"]
    series["high"] = max(combined, key=lambda item: item["price"])
    series["low"] = min(combined, key=lambda item: item["price"])
    series["avg_future"] = round(sum(item["price"] for item in series["future"]) / len(series["future"]), 2)
    series["change"] = round(((series["future"][-1]["price"] - series["present"]["price"]) / series["present"]["price"]) * 100, 2) if series["present"]["price"] else 0
    series["location_factor"] = factor
    return series


def next_season_name():
    month = datetime.now().month
    if month in [6, 7, 8, 9, 10]:
        return "Rabi"
    if month in [11, 12, 1, 2, 3]:
        return "Zaid / Summer"
    return "Kharif"


def best_crop_recommendations(state, district, taluk):
    candidates = crops_for_region(state, district, taluk)
    ranked = []
    for crop_name in candidates:
        series = adjusted_market_series(crop_name, state, district, taluk)
        local_score = 18 if crop_name.lower() in [c.lower() for c in candidates[:8]] else 6
        score = round(55 + local_score + min(max(series["change"], -12), 18) + (series["avg_future"] / 1200), 1)
        ranked.append({
            "name": crop_name,
            "score": min(score, 98),
            "present_price": series["present"]["price"],
            "future_price": series["future"][2]["price"],
            "change": series["change"],
            "best_month": series["high"]["label"],
        })
    ranked.sort(key=lambda item: (item["score"], item["future_price"]), reverse=True)
    return ranked[:8]


@lru_cache(maxsize=1024)
def best_sell_markets(state, crop):
    catalog = state_districts_catalog()
    districts = catalog.get(state, [])[:80]
    markets = []
    for district in districts:
        for taluk in generated_taluks(state, district)[:3]:
            series = adjusted_market_series(crop, state, district, taluk)
            markets.append({
                "state": state,
                "district": district,
                "taluk": taluk,
                "price": series["present"]["price"],
                "best_month": series["high"]["label"],
                "best_price": series["high"]["price"],
            })
    markets.sort(key=lambda item: (item["price"], item["best_price"]), reverse=True)
    return tuple(tuple(sorted(item.items())) for item in markets[:8])


def sell_market_dicts(state, crop):
    return [dict(item) for item in best_sell_markets(state, crop)]


def build_market_payload(state, district, taluk, crop):
    if not district:
        districts = state_districts_catalog().get(state, [])
        district = districts[0] if districts else ""
    if not taluk:
        taluks = generated_taluks(state, district)
        taluk = taluks[0] if taluks else ""
    crop = crop.lower()
    local_crops = crops_for_region(state, district, taluk)
    series = adjusted_market_series(crop, state, district, taluk)
    all_local = []
    seen = []
    for candidate in local_crops + DISPLAY_COMMODITIES:
        c = candidate.lower()
        if c in seen:
            continue
        seen.append(c)
        try:
            price = adjusted_market_series(c, state, district, taluk)["present"]["price"]
        except Exception:
            price = 0
        all_local.append({
            "name": c,
            "price": price,
            "is_local": c in [x.lower() for x in local_crops],
            "model_crop": normalise_crop_name(c),
        })
    all_local.sort(key=lambda item: item["price"], reverse=True)
    return {
        "ok": True,
        "state": state,
        "district": district,
        "taluk": taluk,
        "crop": crop,
        "local_crops": local_crops,
        "series": series,
        "rankings": all_local[:18],
        "recommendations": best_crop_recommendations(state, district, taluk),
        "sell_markets": sell_market_dicts(state, crop),
        "next_season": next_season_name(),
        "generated_at": datetime.now().strftime('%d %b %Y, %I:%M %p'),
        "note": "Prices are ML estimates calibrated by crop season, local crop fit, and district market depth. For official transaction-grade accuracy, connect Agmarknet/eNAM mandi arrivals and prices."
    }


@app.route('/')
def index():
    context = {
        "top5": TopFiveWinners(),
        "bottom5": TopFiveLosers(),
        "sixmonths": SixMonthsForecast()
    }
    return render_template('index.html', context=context)


@app.route('/ai-farmer')
def ai_farmer():
    """AI Farmer Intelligence Dashboard"""
    top5  = TopFiveWinners()
    bot5  = TopFiveLosers()
    six   = SixMonthsForecast()
    # Build full commodity price list for the advisor
    current_month  = datetime.now().month
    current_year   = datetime.now().year
    current_rain   = annual_rainfall[current_month - 1]
    all_prices = []
    for c in commodity_list:
        cname = c.getCropName().split('/')[-1]
        base_p = base.get(cname, 1000)
        try:
            wpi = c.getPredictedValue([float(current_month), current_year, current_rain])
            price = round((wpi * base_p) / 100, 2)
        except:
            price = base_p
        all_prices.append({'name': cname, 'price': price, 'base': base_p})
    all_prices.sort(key=lambda x: -x['price'])
    context = {
        'top5': top5, 'bottom5': bot5, 'sixmonths': six,
        'all_prices': all_prices,
        'month': datetime.now().strftime('%B %Y'),
    }
    return render_template('ai_farmer.html', context=context)


@app.route('/market-intelligence')
def market_intelligence():
    """Futuristic location-wise price predictor with PDF export."""
    catalog = state_districts_catalog()
    context = {
        "states": list(catalog.keys()),
        "commodities": DISPLAY_COMMODITIES,
        "total_districts": sum(len(v) for v in catalog.values()),
        "month": datetime.now().strftime('%B %Y'),
    }
    return render_template('market_intelligence.html', context=context)


@app.route('/api/location-options')
def location_options_api():
    state = request.args.get('state', '')
    district = request.args.get('district', '')
    taluk = request.args.get('taluk', '')
    catalog = state_districts_catalog()
    if not state:
        return jsonify({"ok": True, "states": list(catalog.keys()), "districts": [], "taluks": []})
    districts = catalog.get(state, [])
    if not district and districts:
        district = districts[0]
    taluks = generated_taluks(state, district) if district else []
    crops_here = crops_for_region(state, district, taluk or (taluks[0] if taluks else ""))
    return jsonify({
        "ok": True,
        "states": list(catalog.keys()),
        "districts": districts,
        "taluks": taluks,
        "crops": list(dict.fromkeys(crops_here + DISPLAY_COMMODITIES))
    })


@app.route('/api/market-intelligence')
def market_intelligence_api():
    state = request.args.get('state', 'Karnataka')
    district = request.args.get('district', '')
    taluk = request.args.get('taluk', '')
    crop = request.args.get('crop', 'paddy').lower()
    return jsonify(build_market_payload(state, district, taluk, crop))


@app.route('/market-report.pdf')
def market_report_pdf():
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.linecharts import HorizontalLineChart
    except Exception as exc:
        return jsonify({"ok": False, "error": "PDF engine missing. Install reportlab.", "detail": str(exc)}), 500

    state = request.args.get('state', 'Karnataka')
    district = request.args.get('district', '')
    taluk = request.args.get('taluk', '')
    crop = request.args.get('crop', 'paddy').lower()
    data = build_market_payload(state, district, taluk, crop)
    series = data["series"]
    recommendations = data["recommendations"]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=14*mm, leftMargin=14*mm, topMargin=12*mm, bottomMargin=12*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="BrandTitle", parent=styles["Title"], fontSize=22, leading=26, textColor=colors.HexColor("#064e3b"), spaceAfter=8))
    styles.add(ParagraphStyle(name="SmallMuted", parent=styles["BodyText"], fontSize=8, leading=11, textColor=colors.HexColor("#64748b")))
    story = [
        Paragraph("AGRI INTELLIGENCE Market Predictor", styles["BrandTitle"]),
        Paragraph(f"{crop.title()} report for {taluk}, {district}, {state} | Generated {data['generated_at']}", styles["SmallMuted"]),
        Spacer(1, 8),
    ]
    summary_rows = [
        ["Present Price", f"Rs. {series['present']['price']:,.2f}", "12M Direction", f"{series['change']}%"],
        ["Best Sell Window", f"{series['high']['label']} | Rs. {series['high']['price']:,.2f}", "Lowest Window", f"{series['low']['label']} | Rs. {series['low']['price']:,.2f}"],
        ["Forecast Average", f"Rs. {series['avg_future']:,.2f}", "Best Next Season", recommendations[0]["name"].title() if recommendations else "-"],
    ]
    table = Table(summary_rows, colWidths=[38*mm, 54*mm, 38*mm, 54*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#ecfdf5")),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#0f172a")),
        ("GRID", (0,0), (-1,-1), .4, colors.HexColor("#a7f3d0")),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("PADDING", (0,0), (-1,-1), 8),
    ]))
    story += [table, Spacer(1, 14)]

    values = [item["price"] for item in series["past"]] + [series["present"]["price"]] + [item["price"] for item in series["future"]]
    drawing = Drawing(178*mm, 70*mm)
    chart = HorizontalLineChart()
    chart.x = 8
    chart.y = 10
    chart.height = 55*mm
    chart.width = 160*mm
    chart.data = [values]
    chart.lines[0].strokeColor = colors.HexColor("#10b981")
    chart.lines[0].strokeWidth = 2.2
    chart.valueAxis.valueMin = min(values) * .96
    chart.valueAxis.valueMax = max(values) * 1.04
    chart.categoryAxis.labels.boxAnchor = "ne"
    chart.categoryAxis.labels.angle = 45
    chart.categoryAxis.categoryNames = [item["label"] for item in series["past"]] + ["Now"] + [item["label"] for item in series["future"]]
    drawing.add(chart)
    story += [Paragraph("Past - Present - Future Price Graph", styles["Heading2"]), drawing, Spacer(1, 12)]

    rec_rows = [["Rank", "Best Crop", "Score", "Present", "Next Season", "Best Month"]]
    for idx, item in enumerate(recommendations[:8], 1):
        rec_rows.append([idx, item["name"].title(), f"{item['score']}", f"Rs. {item['present_price']:,.0f}", f"Rs. {item['future_price']:,.0f}", item["best_month"]])
    rec_table = Table(rec_rows, colWidths=[14*mm, 40*mm, 22*mm, 34*mm, 34*mm, 34*mm])
    rec_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0f766e")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), .3, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ("PADDING", (0,0), (-1,-1), 6),
    ]))
    story += [Paragraph(f"Best Crops For {taluk} Now And Next {data['next_season']} Season", styles["Heading2"]), rec_table, Spacer(1, 10)]
    sell_rows = [["Rank", "Sell At", "Present Price", "Best Future Window"]]
    for idx, item in enumerate(data["sell_markets"][:8], 1):
        sell_rows.append([
            idx,
            f"{item['taluk']}, {item['district']}",
            f"Rs. {item['price']:,.0f}",
            f"{item['best_month']} | Rs. {item['best_price']:,.0f}",
        ])
    sell_table = Table(sell_rows, colWidths=[14*mm, 76*mm, 38*mm, 50*mm])
    sell_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#075985")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), .3, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f0f9ff")]),
        ("PADDING", (0,0), (-1,-1), 6),
    ]))
    story += [Paragraph(f"Where To Sell {crop.title()} For Higher Amount", styles["Heading2"]), sell_table, Spacer(1, 10)]
    story += [Paragraph(data["note"], styles["SmallMuted"])]
    doc.build(story)
    buffer.seek(0)
    filename = f"{state}-{district}-{taluk}-{crop}-market-report.pdf".replace(" ", "-")
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=filename)


@app.route('/commodity/<name>')
def crop_profile(name):
    try:
        max_crop, min_crop, forecast_crop_values = TwelveMonthsForecast(name)
        prev_crop_values   = TwelveMonthPrevious(name)

        # Build 3-element forecast tuples: [label, price, pct_change]
        fv_display = []
        base_price = float(forecast_crop_values[0][1]) if forecast_crop_values else 1.0
        for item in forecast_crop_values:
            price = float(item[1]) if item[1] else 0.0
            try:
                chg = round(((price - base_price) / base_price) * 100, 2) if base_price else 0.0
            except:
                chg = 0.0
            fv_display.append([item[0], round(price, 2), chg])

        forecast_x = [i[0] for i in fv_display]
        forecast_y = [i[1] for i in fv_display]
        forecast_changes = [i[2] for i in fv_display]
        previous_x = [i[0] for i in prev_crop_values]
        previous_y = [round(float(i[1]), 2) for i in prev_crop_values]
        current_price = CurrentMonth(name)
        crop_data = crops.crop(name)

        context = {
            "name":           name,
            "max_crop":       max_crop if max_crop else ["—", 0],
            "min_crop":       min_crop if min_crop else ["—", 0],
            "forecast_values":fv_display,
            "forecast_x":     str(forecast_x),
            "forecast_y":     forecast_y,
            "forecast_changes": forecast_changes,
            "previous_x":     previous_x,
            "previous_y":     previous_y,
            "current_price":  round(float(current_price), 2) if current_price else 0,
            "image_url":      crop_data[0] if crop_data else '',
            "prime_loc":      crop_data[1] if crop_data else '—',
            "type_c":         crop_data[2] if crop_data else '—',
            "export":         crop_data[3] if crop_data else '—',
        }
        return render_template('commodity.html', context=context)
    except Exception as e:
        import traceback; traceback.print_exc()
        # Safe fallback context — no data to display
        context = {
            "name": name, "max_crop": ["—", 0], "min_crop": ["—", 0],
            "forecast_values": [], "forecast_x": "[]", "forecast_y": [],
            "forecast_changes": [], "previous_x": [], "previous_y": [],
            "current_price": 0, "image_url": "", "prime_loc": "—",
            "type_c": "—", "export": "—",
        }
        return render_template('commodity.html', context=context)



@app.route('/api/all-crops')
def all_crops_api():
    """Return all 23 commodity names + current prices for the crop grid."""
    current_month = datetime.now().month
    current_year  = datetime.now().year
    current_rain  = annual_rainfall[current_month - 1]
    result = []
    for c in commodity_list:
        cname = c.getCropName().split('/')[-1]
        base_p = base.get(cname, 1000)
        try:
            wpi = c.getPredictedValue([float(current_month), current_year, current_rain])
            price = round((wpi * base_p) / 100, 2)
        except:
            price = base_p
        result.append({'name': cname, 'price': price})
    result.sort(key=lambda x: x['name'])
    return jsonify({'ok': True, 'crops': result})


@app.route('/ticker/<item>/<number>')
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def ticker(item, number):
    n = int(number)
    i = int(item)
    data = SixMonthsForecast()
    context = str(data[n][i])

    if i == 2 or i == 5:
        context = '₹' + context
    elif i == 3 or i == 6:

        context = context + '%'

    #print('context: ', context)
    return context



@app.route('/api/geocode')
def geocode():
    """Reverse-geocode GPS coords to village/taluk/district/state via OpenStreetMap Nominatim (free, no key)."""
    lat = request.args.get('lat', '')
    lon = request.args.get('lon', '')
    try:
        import urllib.request as ur, json
        url = (f"https://nominatim.openstreetmap.org/reverse"
               f"?format=json&lat={lat}&lon={lon}&addressdetails=1&zoom=14")
        req = ur.Request(url, headers={'User-Agent': 'AgriIntelligence/1.0'})
        data = json.loads(ur.urlopen(req, timeout=8).read())
        addr = data.get('address', {})
        result = {
            'village':  addr.get('village') or addr.get('hamlet') or addr.get('suburb') or addr.get('neighbourhood') or '',
            'taluk':    addr.get('county') or addr.get('subdistrict') or addr.get('town') or '',
            'district': addr.get('state_district') or addr.get('district') or addr.get('city') or '',
            'state':    addr.get('state', ''),
            'pincode':  addr.get('postcode', ''),
            'display':  data.get('display_name', ''),
            'full':     addr,
        }
        return jsonify({'ok': True, 'data': result})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})


@app.route('/api/weather')
def live_weather():
    """Fetch real-time weather from Open-Meteo (free, no API key required)"""
    lat = request.args.get('lat', 22.5)
    lon = request.args.get('lon', 78.9)
    try:
        import urllib.request as ur, json
        url = (f"https://api.open-meteo.com/v1/forecast"
               f"?latitude={lat}&longitude={lon}"
               f"&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code"
               f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code"
               f"&timezone=Asia%2FKolkata&forecast_days=7")
        data = json.loads(ur.urlopen(url, timeout=6).read())
        return jsonify({'ok': True, 'data': data})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})


@app.route('/api/market/<name>')
def live_market(name):
    """Return live ML-predicted price + 30-day daily trend for any commodity"""
    try:
        name_l = name.lower()
        commodity = None
        for c in commodity_list:
            cname = c.getCropName().split('/')[-1].lower()
            if name_l == cname or name_l in cname or cname in name_l:
                commodity = c
                break
        if commodity is None:
            return jsonify({'ok': False, 'error': 'Commodity not found'})

        from datetime import timedelta
        now = datetime.now()
        base_name = name_l.capitalize()
        base_price = base.get(base_name, 1000)
        rainfall = annual_rainfall

        # 30-day daily prices
        trend = []
        for d in range(0, 30):
            dt = now + timedelta(days=d)
            m = dt.month
            y = dt.year
            r = rainfall[m - 1]
            try:
                wpi = commodity.getPredictedValue([float(m), y, r])
                price = round((wpi * base_price) / 100, 2)
            except:
                price = base_price
            trend.append({'date': dt.strftime('%d %b'), 'price': price})

        current_m = now.month
        current_y = now.year
        r_now = rainfall[current_m - 1]
        try:
            wpi_now = commodity.getPredictedValue([float(current_m), current_y, r_now])
            current_price = round((wpi_now * base_price) / 100, 2)
        except:
            current_price = base_price

        return jsonify({'ok': True, 'name': name_l, 'current_price': current_price, 'trend_30d': trend})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})



def TopFiveWinners():
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_rainfall = annual_rainfall[current_month - 1]
    prev_month = current_month - 1
    prev_rainfall = annual_rainfall[prev_month - 1]
    current_month_prediction = []
    prev_month_prediction = []
    change = []

    for i in commodity_list:
        current_predict = i.getPredictedValue([float(current_month), current_year, current_rainfall])
        current_month_prediction.append(current_predict)
        prev_predict = i.getPredictedValue([float(prev_month), current_year, prev_rainfall])
        prev_month_prediction.append(prev_predict)
        change.append((((current_predict - prev_predict) * 100 / prev_predict), commodity_list.index(i)))
    sorted_change = change
    sorted_change.sort(reverse=True)
    # print(sorted_change)
    to_send = []
    for j in range(0, 5):
        perc, i = sorted_change[j]
        name = commodity_list[i].getCropName().split('/')[1]
        to_send.append([name, round((current_month_prediction[i] * base[name]) / 100, 2), round(perc, 2)])
    #print(to_send)
    return to_send


def TopFiveLosers():
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_rainfall = annual_rainfall[current_month - 1]
    prev_month = current_month - 1
    prev_rainfall = annual_rainfall[prev_month - 1]
    current_month_prediction = []
    prev_month_prediction = []
    change = []

    for i in commodity_list:
        current_predict = i.getPredictedValue([float(current_month), current_year, current_rainfall])
        current_month_prediction.append(current_predict)
        prev_predict = i.getPredictedValue([float(prev_month), current_year, prev_rainfall])
        prev_month_prediction.append(prev_predict)
        change.append((((current_predict - prev_predict) * 100 / prev_predict), commodity_list.index(i)))
    sorted_change = change
    sorted_change.sort()
    to_send = []
    for j in range(0, 5):
        perc, i = sorted_change[j]
        name = commodity_list[i].getCropName().split('/')[1]
        to_send.append([name, round((current_month_prediction[i] * base[name]) / 100, 2), round(perc, 2)])
   # print(to_send)
    return to_send



def SixMonthsForecast():
    month1=[]
    month2=[]
    month3=[]
    month4=[]
    month5=[]
    month6=[]
    for i in commodity_list:
        crop=SixMonthsForecastHelper(i.getCropName())
        k=0
        for j in crop:
            time = j[0]
            price = j[1]
            change = j[2]
            if k==0:
                month1.append((price,change,i.getCropName().split("/")[1],time))
            elif k==1:
                month2.append((price,change,i.getCropName().split("/")[1],time))
            elif k==2:
                month3.append((price,change,i.getCropName().split("/")[1],time))
            elif k==3:
                month4.append((price,change,i.getCropName().split("/")[1],time))
            elif k==4:
                month5.append((price,change,i.getCropName().split("/")[1],time))
            elif k==5:
                month6.append((price,change,i.getCropName().split("/")[1],time))
            k+=1
    # Sort by percentage change (index 1) instead of raw absolute price (index 0)
    month1.sort(key=lambda x: x[1])
    month2.sort(key=lambda x: x[1])
    month3.sort(key=lambda x: x[1])
    month4.sort(key=lambda x: x[1])
    month5.sort(key=lambda x: x[1])
    month6.sort(key=lambda x: x[1])
    
    crop_month_wise=[]
    seen_best = set()
    seen_worst = set()
    
    for month_data in [month1, month2, month3, month4, month5, month6]:
        # Pick the lowest % change (worst) that hasn't been picked yet
        worst_idx = 0
        while worst_idx < len(month_data) and month_data[worst_idx][2] in seen_worst:
            worst_idx += 1
        if worst_idx >= len(month_data): worst_idx = 0  # Fallback
        
        # Pick the highest % change (best) that hasn't been picked yet
        best_idx = len(month_data) - 1
        while best_idx >= 0 and month_data[best_idx][2] in seen_best:
            best_idx -= 1
        if best_idx < 0: best_idx = len(month_data) - 1 # Fallback
            
        best = month_data[best_idx]
        worst = month_data[worst_idx]
        
        seen_best.add(best[2])
        seen_worst.add(worst[2])
        
        # Format expected by frontend: [time, best_change, best_name, best_price, worst_change, worst_name, worst_price]
        crop_month_wise.append([best[3], best[1], best[2], best[0], worst[1], worst[2], worst[0]])

   # print(crop_month_wise)
    return crop_month_wise

def SixMonthsForecastHelper(name):
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_rainfall = annual_rainfall[current_month - 1]
    name = name.split("/")[1]
    name = name.lower()
    commodity = commodity_list[0]
    for i in commodity_list:
        if name == str(i):
            commodity = i
            break
    month_with_year = []
    for i in range(1, 7):
        if current_month + i <= 12:
            month_with_year.append((current_month + i, current_year, annual_rainfall[current_month + i - 1]))
        else:
            month_with_year.append((current_month + i - 12, current_year + 1, annual_rainfall[current_month + i - 13]))
    wpis = []
    current_wpi = commodity.getPredictedValue([float(current_month), current_year, current_rainfall])
    change = []

    for m, y, r in month_with_year:
        current_predict = commodity.getPredictedValue([float(m), y, r])
        wpis.append(current_predict)
        change.append(((current_predict - current_wpi) * 100) / current_wpi)

    crop_price = []
    for i in range(0, len(wpis)):
        m, y, r = month_with_year[i]
        x = datetime(y, m, 1)
        x = x.strftime("%b %y")
        crop_price.append([x, round((wpis[i]* base[name.capitalize()]) / 100, 2) , round(change[i], 2)])

   # print("Crop_Price: ", crop_price)
    return crop_price

def CurrentMonth(name):
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_rainfall = annual_rainfall[current_month - 1]
    name = name.lower()
    commodity = commodity_list[0]
    for i in commodity_list:
        if name == str(i):
            commodity = i
            break
    current_wpi = commodity.getPredictedValue([float(current_month), current_year, current_rainfall])
    current_price = (base[name.capitalize()]*current_wpi)/100
    return current_price

def TwelveMonthsForecast(name):
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_rainfall = annual_rainfall[current_month - 1]
    name = name.lower()
    commodity = commodity_list[0]
    for i in commodity_list:
        if name == str(i):
            commodity = i
            break
    month_with_year = []
    for i in range(1, 13):
        if current_month + i <= 12:
            month_with_year.append((current_month + i, current_year, annual_rainfall[current_month + i - 1]))
        else:
            month_with_year.append((current_month + i - 12, current_year + 1, annual_rainfall[current_month + i - 13]))
    max_index = 0
    min_index = 0
    max_value = 0
    min_value = 9999
    wpis = []
    current_wpi = commodity.getPredictedValue([float(current_month), current_year, current_rainfall])
    change = []

    for m, y, r in month_with_year:
        current_predict = commodity.getPredictedValue([float(m), y, r])
        if current_predict > max_value:
            max_value = current_predict
            max_index = month_with_year.index((m, y, r))
        if current_predict < min_value:
            min_value = current_predict
            min_index = month_with_year.index((m, y, r))
        wpis.append(current_predict)
        change.append(((current_predict - current_wpi) * 100) / current_wpi)

    max_month, max_year, r1 = month_with_year[max_index]
    min_month, min_year, r2 = month_with_year[min_index]
    min_value = min_value * base[name.capitalize()] / 100
    max_value = max_value * base[name.capitalize()] / 100
    crop_price = []
    for i in range(0, len(wpis)):
        m, y, r = month_with_year[i]
        x = datetime(y, m, 1)
        x = x.strftime("%b %y")
        crop_price.append([x, round((wpis[i]* base[name.capitalize()]) / 100, 2) , round(change[i], 2)])
   # print("forecasr", wpis)
    x = datetime(max_year,max_month,1)
    x = x.strftime("%b %y")
    max_crop = [x, round(max_value,2)]
    x = datetime(min_year, min_month, 1)
    x = x.strftime("%b %y")
    min_crop = [x, round(min_value,2)]

    return max_crop, min_crop, crop_price


def TwelveMonthPrevious(name):
    name = name.lower()
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_rainfall = annual_rainfall[current_month - 1]
    commodity = commodity_list[0]
    wpis = []
    crop_price = []
    for i in commodity_list:
        if name == str(i):
            commodity = i
            break
    month_with_year = []
    for i in range(1, 13):
        if current_month - i >= 1:
            month_with_year.append((current_month - i, current_year, annual_rainfall[current_month - i - 1]))
        else:
            month_with_year.append((current_month - i + 12, current_year - 1, annual_rainfall[current_month - i + 11]))

    for m, y, r in month_with_year:
        current_predict = commodity.getPredictedValue([float(m), 2013, r])
        wpis.append(current_predict)

    for i in range(0, len(wpis)):
        m, y, r = month_with_year[i]
        x = datetime(y,m,1)
        x = x.strftime("%b %y")
        crop_price.append([x, round((wpis[i]* base[name.capitalize()]) / 100, 2)])
   # print("previous ", wpis)
    new_crop_price =[]
    for i in range(len(crop_price)-1,-1,-1):
        new_crop_price.append(crop_price[i])
    return new_crop_price

@app.route('/api/geocode')
def geocode_api():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"ok": False, "error": "Missing lat/lon"}), 400
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=14&addressdetails=1"
        headers = {'User-Agent': 'AgriIntelligence/1.0 (Contact: demo@example.com)'}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status() 
        data = response.json()
        addr = data.get('address', {})
        
        village = addr.get('village') or addr.get('suburb') or addr.get('neighbourhood') or addr.get('town')
        taluk = addr.get('county') or addr.get('city_district') or addr.get('state_district')
        district = addr.get('state_district') or addr.get('county')
        state = addr.get('state')
        pincode = addr.get('postcode')
        
        return jsonify({
            "ok": True, 
            "data": {
                "village": village,
                "taluk": taluk,
                "district": district,
                "state": state,
                "pincode": pincode
            }
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/api/weather')
def weather_api():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"ok": False, "error": "Missing lat/lon"}), 400
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return jsonify({"ok": True, "data": data})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
print("Loading ML models for 23 commodities...")
arhar = Commodity(commodity_dict["arhar"])
commodity_list.append(arhar)
bajra = Commodity(commodity_dict["bajra"])
commodity_list.append(bajra)
barley = Commodity(commodity_dict["barley"])
commodity_list.append(barley)
copra = Commodity(commodity_dict["copra"])
commodity_list.append(copra)
cotton = Commodity(commodity_dict["cotton"])
commodity_list.append(cotton)
sesamum = Commodity(commodity_dict["sesamum"])
commodity_list.append(sesamum)
gram = Commodity(commodity_dict["gram"])
commodity_list.append(gram)
groundnut = Commodity(commodity_dict["groundnut"])
commodity_list.append(groundnut)
jowar = Commodity(commodity_dict["jowar"])
commodity_list.append(jowar)
maize = Commodity(commodity_dict["maize"])
commodity_list.append(maize)
masoor = Commodity(commodity_dict["masoor"])
commodity_list.append(masoor)
moong = Commodity(commodity_dict["moong"])
commodity_list.append(moong)
niger = Commodity(commodity_dict["niger"])
commodity_list.append(niger)
paddy = Commodity(commodity_dict["paddy"])
commodity_list.append(paddy)
ragi = Commodity(commodity_dict["ragi"])
commodity_list.append(ragi)
rape = Commodity(commodity_dict["rape"])
commodity_list.append(rape)
jute = Commodity(commodity_dict["jute"])
commodity_list.append(jute)
safflower = Commodity(commodity_dict["safflower"])
commodity_list.append(safflower)
soyabean = Commodity(commodity_dict["soyabean"])
commodity_list.append(soyabean)
sugarcane = Commodity(commodity_dict["sugarcane"])
commodity_list.append(sugarcane)
sunflower = Commodity(commodity_dict["sunflower"])
commodity_list.append(sunflower)
urad = Commodity(commodity_dict["urad"])
commodity_list.append(urad)
wheat = Commodity(commodity_dict["wheat"])
commodity_list.append(wheat)
print("ML Models loaded.")

if __name__ == "__main__":
    app.run()
