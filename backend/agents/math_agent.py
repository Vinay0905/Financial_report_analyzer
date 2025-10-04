



class MathAgent:
    def compute_ratios(self, financials):
        ratios = {}
        if financials.get("revenue") and financials.get("net_income"):
            ratios["net_margin"] = financials["net_income"] / (financials["revenue"] + 1e-8)
        return ratios
