CREATE TABLE public.simulated_price (
    -- Foreign key ensures each price belongs to a known candidate bond.
    internal_id TEXT NOT NULL
        REFERENCES public.bond_master(internal_id),
    valuation_date DATE NOT NULL,
    clean_price NUMERIC NOT NULL
        CHECK (
            clean_price > 0
            AND clean_price NOT IN
                ('NaN'::NUMERIC, 'Infinity'::NUMERIC, '-Infinity'::NUMERIC)
        ),
    price_status TEXT NOT NULL
        CHECK (price_status = 'simulated'),
    -- Composite key allows one price per bond on each valuation date.
    PRIMARY KEY (internal_id, valuation_date)
);
