CREATE TABLE public.bond_return_result (
    internal_id TEXT PRIMARY KEY
        REFERENCES public.bond_master(internal_id),
    -- Accrued interest, coupon cash, and dirty prices are USD per $100 face.
    beginning_ai_usd_per_100_face NUMERIC,
    ending_ai_usd_per_100_face NUMERIC,
    coupon_cash_usd_per_100_face NUMERIC,
    beginning_dirty_price_usd_per_100_face NUMERIC,
    ending_dirty_price_usd_per_100_face NUMERIC,
    -- Returns are decimals: for example, 0.01 represents one percent.
    price_return_decimal NUMERIC,
    income_return_decimal NUMERIC,
    total_return_decimal NUMERIC,
    -- Coupon payment dates retain the export's text representation.
    coupon_payment_dates TEXT,
    result_status TEXT
);
