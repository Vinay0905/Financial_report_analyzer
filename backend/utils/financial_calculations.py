def basic_financials(data):
    out = {"revenue": data.get("revenue"), "net_income": data.get("net_income")}
    if data.get("assets") and data.get("liabilities"):
        out["de_ratio"] = data["liabilities"] / (data["assets"] + 1e-8)
    return out
