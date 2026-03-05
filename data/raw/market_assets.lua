return {
    -- Это комментарий из старой системы["BTC_USD"] = {
        type = "Crypto",
        volatility = 0.85,
        tags = {"high_risk", "digital"},
        -- Висячая запятая ниже:
        min_trade_size = 0.0001,
    },
    ["SP500"] = {
        type = "Equities",
        volatility = 0.15,
        tags = {"index", "traditional"},
    }
}